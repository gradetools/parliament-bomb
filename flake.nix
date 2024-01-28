{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      formatter = pkgs.alejandra;
      packages = {
        cavestock = pkgs.callPackage ./nix/default.nix;
        default = self.packages.${system}.cavestock;
      };

      devShells.default = pkgs.mkShell {
        buildInputs = [
          pkgs.gcc
          pkgs.gnumake
          pkgs.systemd.dev
          pkgs.curl
          pkgs.jansson
        ];
        packages = with pkgs;
        with pkgs.python311Packages; [
         nextcord
         requests
         python-dotenv
         setuptools
         matplotlib
         uptime
         psutil
        ];
      };
    });
}

