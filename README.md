# npins-updater

## Install

`npins-updater` can be installed and updated via npins itself:

1. add npins-updater to your sources:

```bash
npins add github herbetom npins-updater -b main
```

2. edit `shell.nix` to add npins-updater to your development shell:


```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
    npins
    # This is the important line:
    (pkgs.callPackage "${(import ./npins).npins-updater}/pkgs/npins-updater.nix" {})
  ];
}
```

3. enter `nix-shell`. That's it!


## Usage

```
$ npins-updater --help
usage: npins-updater [-h] [--no-changelog] [-c CONFIG] [-S] [PACKAGE]

Update npins sources and commit changes with a changelog

positional arguments:
  PACKAGE               The repo to update, if none is provided it will update all

options:
  -h, --help            show this help message and exit
  --no-changelog        do not create a changelog
  -c CONFIG, --config CONFIG
                        provide a config file, default is ~/.config/npins-updater/config.toml
  -S, --sign            GPG-sign commits.
```

## Config File


```
# Enty for the nixpkgs repo
[repo.nixpkgs]
# url=string - URL of the repo.
url="https://github.com/NixOS/nixpkgs/"

# path=string - path of the repo
path="/home/user/git/NixOS/nixpkgs"

# fetch=string|boolean (optional): true by default. If true it will fetch from the default remote. If false it won't fetch. If a string is provided if will try fetching from the that remote.
fetch="upstream"

[repo.npins-updater]
url="https://github.com/herbetom/npins-updater/"
path="/home/user/git/npins-updater"
fetch=true
```
