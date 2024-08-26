# niv-updater

## Install

`niv-updater` can be installed and updated via niv itself:

1. add niv-updater to your sources:

```bash
niv add herbetom/niv-updater
```

2. edit `shell.nix` to add niv-updater to your development shell:


```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
    niv
    # This is the important line:
    (pkgs.callPackage "${(import ./nix/sources.nix).niv-updater}/pkgs/niv-updater.nix" {})
  ];
}
```

3. enter `nix-shell`. That's it!


## Usage

```
$ niv-updater --help
usage: niv-updater [-h] [--no-changelog] [-c CONFIG] [-S] [PACKAGE]

Update niv sources and commit changes with a changelog

positional arguments:
  PACKAGE               The repo to update, if none is provided it will update all

options:
  -h, --help            show this help message and exit
  --no-changelog        do not create a changelog
  -c CONFIG, --config CONFIG
                        provide a config file, default is ~/.config/niv-updater/config.toml
  -S, --sign            GPG-sign commits.
```

## Config File


```
# github_token=string (optional): Useful if you run into an api limit with niv
github_token="github_YOUR-PERSONAL-ACCESS-TOKEN"


# Enty for the nixpkgs repo
[repo.nixpkgs]
# url=string - URL of the repo.
url="https://github.com/NixOS/nixpkgs/"

# path=string - path of the repo
path="/home/user/git/NixOS/nixpkgs"

# fetch=string|boolean (optional): true by default. If true it will fetch from the default remote. If false it won't fetch. If a string is provided if will try fetching from the that remote.
fetch="upstream"

[repo.niv-updater]
url="https://github.com/herbetom/niv-updater/"
path="/home/user/git/niv-updater"
fetch=true
```
