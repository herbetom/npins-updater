{pkgs ? import <nixpkgs> {}}: {
  niv-updater = pkgs.callPackage ./pkgs/niv-updater.nix {};
}
