{
  description = "Example flake which just gives you a dev shell with yarn";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      out = system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };

          python = pkgs.python3.withPackages (py: with py; [
            pysdl2
            numpy
            sounddevice
            wavefile
          ]);
        in
          {
            fuckit = pkgs.SDL2;
            devShells.default = pkgs.mkShell {
              PYSDL2_DLL_PATH = pkgs.SDL2 + "/lib";
              buildInputs = [ pkgs.SDL2 python ];
            };

          };
    in
      flake-utils.lib.eachDefaultSystem out // {
        overlays.default = final: prev: {};
      };

}
