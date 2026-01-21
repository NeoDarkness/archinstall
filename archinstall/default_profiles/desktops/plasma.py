from typing import override

from archinstall.default_profiles.profile import GreeterType, ProfileType
from archinstall.default_profiles.xorg import XorgProfile


class PlasmaProfile(XorgProfile):
	def __init__(self) -> None:
		super().__init__('KDE Plasma', ProfileType.DesktopEnv)

	@property
	@override
	def packages(self) -> list[str]:
		return [
			'plasma-meta',
			'kde-system-meta',
			'konsole',
			'kate',
			'ark',
			'dolphin-plugins',
			'firefox',
			'gwengwenview',
			'kamoso',
			'elisa',
			'ffmpegthumbs',
			'kdegraphics-thumbnailers',
			'partitionmanager',
			'kolourpaint',
			'okular',
			'krdc',
			'kgpg',
			'kfind',
			'kwalletmanager',
			'filelight',
			'isoimagewriter',
			'kcalc',
			'kdebugsettings',
			'kdf',
			'kdialog',
			'keditbookmarks',
			'kamera',
			'kdeconnect',
			'krfb',
			'kdenetwork-filesharing',
			'kio-gdrive',
			'colord-kde',
			'plasma-keyboard',
			'plymouth-kcm'
		]

	@property
	@override
	def default_greeter_type(self) -> GreeterType:
		return GreeterType.Sddm
