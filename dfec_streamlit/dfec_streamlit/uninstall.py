import subprocess

# インストールされたパッケージが書かれたファイル
with open('installed_packages.txt') as f:
    packages = f.read().splitlines()

# 各パッケージについてアンインストールコマンドを実行
for package in packages:
    subprocess.run(['pip', 'uninstall', '-y', package])