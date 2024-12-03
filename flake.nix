{
  description = "A basic flake using pyproject.toml project metadata";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{
      flake-parts,
      nixpkgs,
      pyproject-nix,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
      ];
      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          system,
          ...
        }:
        let
          # Loads pyproject.toml into a high-level project representation
          # Do you notice how this is not tied to any `system` attribute or package sets?
          # That is because `project` refers to a pure data representation.
          project = pyproject-nix.lib.project.loadPyproject {
            # Read & unmarshal pyproject.toml relative to this project root.
            # projectRoot is also used to set `src` for renderers such as buildPythonPackage.
            projectRoot = ./.;
          };

          # This example is only using x86_64-linux
          # pkgs = nixpkgs.legacyPackages.x86_64-linux;

          # We are using the default nixpkgs Python3 interpreter & package set.
          #
          # This means that you are purposefully ignoring:
          # - Version bounds
          # - Dependency sources (meaning local path dependencies won't resolve to the local path)
          #
          # To use packages from local sources see "Overriding Python packages" in the nixpkgs manual:
          # https://nixos.org/manual/nixpkgs/stable/#reference
          #
          # Or use an overlay generator such as uv2nix:
          # https://github.com/pyproject-nix/uv2nix
          python = pkgs.python3;

        in
        {
          # Create a development shell containing dependencies from `pyproject.toml`
          devShells.default =
            let
              # Returns a function that can be passed to `python.withPackages`
              arg = project.renderers.withPackages {
                inherit python;
                # Include dev dependencies found under project.optional-dependencies
                extras = [ "test" ];
              };

              # Returns a wrapped environment (virtualenv like) with all our packages
              pythonEnv = python.withPackages arg;

            in
            # Create a devShell like normal.
            pkgs.mkShell {
              packages = [
                pythonEnv
                self'.packages.default
              ];
            };

          # Build our package using `buildPythonPackage
          packages.default =
            let
              # Returns an attribute set that can be passed to `buildPythonPackage`.
              attrs = project.renderers.buildPythonPackage { inherit python; };
            in
            # Pass attributes to buildPythonPackage.
            # Here is a good spot to add on any missing or custom attributes.
            python.pkgs.buildPythonPackage (attrs // { env.CUSTOM_ENVVAR = "hello"; });
        };
    };
}
