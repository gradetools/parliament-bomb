{
 description = "Parliament Bomb Discord Bot";

 inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
 inputs.flake-utils.url = "github:numtide/flake-utils";
 inputs.rust-overlay.url = "github:oxalica/rust-overlay";

 outputs = { self, nixpkgs, flake-utils, rust-overlay, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs { inherit system overlays; };
        rustVersion = pkgs.rust-bin.stable.latest.default;

        rustPlatform = pkgs.makeRustPlatform {
          cargo = rustVersion;
          rustc = rustVersion;
        };

        myRustBuild = rustPlatform.buildRustPackage {
          pname = "parliamentbomb";
          version = "3.1.0";
          src = ./.;
          nativeBuildInputs = [ 
            pkgs.openssl 
            pkgs.pkg-config
          ];
          PKG_CONFIG_PATH = "${pkgs.openssl.dev}/lib/pkgconfig";
          cargoLock = {
            lockFile = ./Cargo.lock;
          };
        };

        devShell = pkgs.mkShell {
          buildInputs = [
            (rustVersion.override { extensions = [ "rust-src" ]; })
            pkgs.openssl
            pkgs.pkg-config 
          ];
        };

      in {
        packages = {
          parliamentbomb = myRustBuild;
        };
        defaultPackage = myRustBuild;
        devShell = devShell;
      });
}

