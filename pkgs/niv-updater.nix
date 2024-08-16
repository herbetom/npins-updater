# default.nix
{ stdenv, fetchurl }:

stdenv.mkDerivation {
  name = "niv-updater";
  version = "0.0.1";

  src = ./niv-updater.py;

  dontUnpack = true;

  buildInputs = [];

  installPhase = ''
    mkdir -p $out/bin
    cp $src $out/bin/niv-updater
  '';

  meta = {
    description = "niv-updater is a tool to update niv dependencies";
  };
}