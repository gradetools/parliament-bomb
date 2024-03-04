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
          version = "0.1.0";
          src = ./.;
          cargoLock = {
           lockFile = ./Cargo.lock;
         };
        };

        devShell = pkgs.mkShell {
          buildInputs = [ (rustVersion.override { extensions = [ "rust-src" ]; }) ];
        };

      in {
        packages = {
          parliamentbomb = myRustBuild;
        };
        defaultPackage = myRustBuild;
        devShell = devShell;
      });
}

