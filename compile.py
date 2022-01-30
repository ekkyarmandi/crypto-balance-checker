import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    '--name',
    'balance_checker',
    '--onefile',
    'functions.py',
    'main.py',
    '--icon',
    './icon/1486395296-05-wallet_80570.ico'
])

src = "./dist/"
dst = "./"
file = "balance_checker.exe"
if os.path.exists(src+file):
    os.rename(src+file,dst+file)