import re
from typing import override

from archinstall.lib.menu.helpers import Confirmation, Input, Selection
from archinstall.lib.translationhandler import tr
from archinstall.tui.ui.menu_item import MenuItem, MenuItemGroup
from archinstall.tui.ui.result import ResultType

from ..menu.list_manager import ListManager
from ..models.users import User
from ..utils.util import get_password


class UserList(ListManager[User]):
	def __init__(self, prompt: str, lusers: list[User]):
		self._actions = [
			tr('Add a user'),
			tr('Change password'),
			tr('Promote/Demote user'),
			tr('Delete User'),
		]

		super().__init__(
			lusers,
			[self._actions[0]],
			self._actions[1:],
			prompt,
		)

	@override
	def selected_action_display(self, selection: User) -> str:
		return selection.username

	@override
	def handle_action(self, action: str, entry: User | None, data: list[User]) -> list[User]:
		if action == self._actions[0]:  # add
			new_user = self._add_user()
			if new_user is not None:
				# in case a user with the same username as an existing user
				# was created we'll replace the existing one
				data = [d for d in data if d.username != new_user.username]
				data += [new_user]
		elif action == self._actions[1] and entry:  # change password
			header = f'{tr("User")}: {entry.username}\n'
			header += tr('Enter new password')
			new_password = get_password(header=header)

			if new_password:
				user = next(filter(lambda x: x == entry, data))
				user.password = new_password
		elif action == self._actions[2] and entry:  # promote/demote
			user = next(filter(lambda x: x == entry, data))
			user.sudo = False if user.sudo else True
		elif action == self._actions[3] and entry:  # delete
			data = [d for d in data if d != entry]

		return data

	def _check_for_correct_username(self, username: str | None) -> str | None:
		if username is not None:
			if re.match(r'^[a-z_][a-z0-9_-]*\$?$', username) and len(username) <= 32:
				return None
		return tr('The username you entered is invalid')

	def _add_user(self) -> User | None:
		editResult = Input(
			tr('Enter a username'),
			allow_skip=True,
			validator_callback=self._check_for_correct_username,
		).show()

		match editResult.type_:
			case ResultType.Skip:
				return None
			case ResultType.Selection:
				username = editResult.get_value()
			case _:
				raise ValueError('Unhandled result type')

		if not username:
			return None

		header = f'{tr("Username")}: {username}\n'
		prompt = f'{header}\n' + tr('Enter a password')

		password = get_password(header=prompt, allow_skip=True)

		if not password:
			return None

		header += f'{tr("Password")}: {password.hidden()}\n'
		prompt = f'{header}\n' + tr('Should "{}" be a superuser (sudo)?\n').format(username)

		result = Confirmation(
			header=prompt,
			allow_skip=False,
			preset=True,
		).show()

		match result.type_:
			case ResultType.Selection:
				sudo = result.item() == MenuItem.yes()
			case _:
				raise ValueError('Unhandled result type')

		header += f'{tr("Sudo")}: {sudo}\n'
		prompt = f'{header}\n' + tr('Enter full name for this user (optional)')

		full_name_result = Input(
			header=prompt,
			allow_skip=True,
		).show()

		full_name = None
		if full_name_result.type_ == ResultType.Selection:
			full_name = full_name_result.get_value()

		header += f'{tr("Full name")}: {full_name if full_name else ""}\n'
		prompt = f'{header}\n' + tr('Select a shell for this user')

		shells = ['/bin/bash', '/bin/zsh', '/bin/fish']
		shell_items = [MenuItem(s, value=s) for s in shells]
		shell_group = MenuItemGroup(shell_items, sort_items=True)
		shell_group.set_default_by_value('/bin/bash')

		shell_result = Selection(
			shell_group,
			header=prompt,
			allow_skip=False,
		).show()

		shell = '/bin/bash'
		if shell_result.type_ == ResultType.Selection:
			shell = shell_result.get_value()

		return User(username, password, sudo, shell=shell, full_name=full_name)


def ask_for_additional_users(prompt: str = '', defined_users: list[User] = []) -> list[User]:
	users = UserList(prompt, defined_users).run()
	return users
