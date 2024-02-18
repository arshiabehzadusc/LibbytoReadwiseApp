# Libby2Readwise Application Setup

This README provides instructions for setting up the environment to build the Libby2Readwise application. The application requires specific libraries (`libffi`, `libssl`, and `libcrypto`) to be available for packaging. Depending on your system configuration, you may need to specify the paths to these libraries manually.

## Prerequisites

Before building the application, ensure you have the following installed:
- Python 3.x
- py2app
- Homebrew (for macOS users)

## Setting Up Environment Variables

The build script uses environment variables to locate the necessary libraries. If the default paths do not match your system's configuration, you can specify custom paths using environment variables.

### Locating Libraries

First, locate the libraries on your system. The default paths are:
- `libffi`: `/opt/homebrew/opt/libffi/lib/libffi.8.dylib`
- `libssl` and `libcrypto` (part of OpenSSL): `/opt/homebrew/Cellar/openssl@3/3.2.1/lib/`

If these paths do not match, find the correct paths on your system. For OpenSSL, you can use `brew info openssl@3` to find the installation directory.

### Setting Environment Variables

Set the following environment variables according to your library paths:

- `LIBFFI_PATH`: Path to `libffi.8.dylib`
- `LIBSSL_PATH`: Path to `libssl.dylib`
- `LIBCRYPTO_PATH`: Path to `libcrypto.dylib`

#### Example: Setting Environment Variables in Terminal

```bash
export LIBFFI_PATH=/path/to/libffi.8.dylib
export LIBSSL_PATH=/path/to/libssl.dylib
export LIBCRYPTO_PATH=/path/to/libcrypto.dylib

## Build Application

Now you can build the application using py2app:
```bash
python builder.py py2app

Build should be under `dist` directory