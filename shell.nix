
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
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
}
