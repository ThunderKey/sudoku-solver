
{
  description = "Sudoku Solver development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            poetry
          ];
          
          shellHook = ''
            echo "Setting up development environment..."
            if [ -f pyproject.toml ]; then
              echo "Installing dependencies with Poetry..."
              poetry install
              echo "Poetry environment is ready!"
              echo "Run 'poetry run dev' to start the application"
            fi
          '';
        };
      });
}
