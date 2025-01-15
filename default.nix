{pkgs ? import <nixpkgs> {}}: {
  npins-updater = pkgs.callPackage ./pkgs/npins-updater.nix {};
}
