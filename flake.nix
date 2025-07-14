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

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs { inherit system; };
      p2n = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
      poetryApp = p2n.mkPoetryApplication {
        projectDir = self;
        overrides = p2n.defaultPoetryOverrides.extend (self: super: {
          selenium = pkgs.python313Packages.selenium;
          pex = pkgs.python313Packages.pex;
        });
      };
    in {
      packages = {
        devforumauto = poetryApp;
        default = poetryApp;
      };
    });
}
