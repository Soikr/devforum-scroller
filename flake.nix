{
  description = "Logs in and scrolls through the Roblox Devforums most recent posts.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
      inherit (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication defaultPoetryOverrides;
    in {
      packages.default = mkPoetryApplication {
        projectDir = self;
        python = pkgs.python313;

        overrides = defaultPoetryOverrides.extend (final: prev: {
          selenium = pkgs.python313Packages.selenium;
          pex = pkgs.python313Packages.pex;
        });

        propagatedBuildInputs = [
          pkgs.firefox
          pkgs.geckodriver
        ];
      };

      formatter = pkgs.alejandra;
    });
}
