#!/usr/bin/env python3

from setuptools import setup

APP = ['gui.py']  # Your main script
DATA_FILES = []  # Include other data files if needed
OPTIONS = {
	'argv_emulation': True,
	'excludes': ['zmq'],
	'plist': {
		'CFBundleName': 'Libby2Readwise',
		'CFBundleDisplayName': 'Libby2Readwise',
		'CFBundleIdentifier': 'com.yourdomain.Libby2Readwise',
		'CFBundleVersion': '1.0',
		'CFBundleShortVersionString': '1.0',
		'CFBundleDocumentTypes': [{
			'CFBundleTypeExtensions': ['json'],
			'CFBundleTypeName': 'JSON files',
			'CFBundleTypeRole': 'Viewer',
			'LSHandlerRank': 'Owner'
		}],
		# Specify any other plist options you need here
	},
	'packages': ['PyQt5', 'pandas'],
	'includes': ['converter'],  # Include other Python files or packages if your app depends on them
	'frameworks': ['/opt/homebrew/opt/libffi/lib/libffi.8.dylib'],
	'iconfile':'Libby2Readwise.icns',
}
setup(
	app=APP,
	name='Libby2Readwise',
	data_files=DATA_FILES,
	options={'py2app': OPTIONS},
	setup_requires=['py2app'],
)
