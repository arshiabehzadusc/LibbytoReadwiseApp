#!/usr/bin/env python3
import os
from setuptools import setup

def find_library_path(env_var, default_path):
	"""Find the library path using an environment variable or default to a common path."""
	return os.getenv(env_var, default_path)

default_libffi_path = '/opt/homebrew/opt/libffi/lib/libffi.8.dylib'
default_libssl_path = '/opt/homebrew/Cellar/openssl@3/3.2.1/lib/libssl.dylib'
default_libcrypto_path = '/opt/homebrew/Cellar/openssl@3/3.2.1/lib/libcrypto.dylib'

libffi_path = find_library_path('LIBFFI_PATH', default_libffi_path)
libssl_path = find_library_path('LIBSSL_PATH', default_libssl_path)
libcrypto_path = find_library_path('LIBCRYPTO_PATH', default_libcrypto_path)

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
	'packages': ['PyQt5', 'pandas', 'requests', 'charset_normalizer', 'pyarrow', 'ssl', 'certifi'],
	'includes': ['converter','_ssl', 'certifi', 'openssl'],  # Include other Python files or packages if your app depends on them
	'frameworks': [libffi_path, libssl_path, libcrypto_path],
	'iconfile':'Libby2Readwise.icns',
}
setup(
	app=APP,
	name='Libby2Readwise',
	data_files=DATA_FILES,
	options={'py2app': OPTIONS},
	setup_requires=['py2app'],
)
