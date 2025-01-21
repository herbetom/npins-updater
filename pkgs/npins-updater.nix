# default.nix
{ stdenv, fetchurl }:

stdenv.mkDerivation {
  name = "npins-updater";
  version = "0.0.4";

  src = ./npins-updater.py;

  dontUnpack = true;

  buildInputs = [];

  installPhase = ''
    mkdir -p $out/bin
    cp $src $out/bin/npins-updater
  '';

  meta = {
    description = "npins-updater is a tool to update npins dependencies";
  };
}
