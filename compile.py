import PyInstaller.__main__

PyInstaller.__main__.run([
    '--name',
    'address_explorer',
    '--onefile',
    'functions.py',
    'main.py',
    '--icon',
    './icon/1486395296-05-wallet_80570.ico'
])