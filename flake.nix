{
  description = "Nix environment for Python-Vault-Project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      # Systems supported
      allSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forAllSystems =
        f:
        nixpkgs.lib.genAttrs allSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forAllSystems (
        { pkgs }:
        let
          geminiWrapper = pkgs.writeShellScriptBin "gemini" ''
            exec npx gemini "$@"
          '';
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.nodejs_24
              geminiWrapper

              (pkgs.python3.withPackages (
                ps: with ps; [
                  virtualenv
                  pip
                ]
              ))
            ];

            shellHook = ''
              # Install Node dependencies
              npm ci

              # Create and source Python virtual environment
              if [ ! -d ".venv" ]; then
                python3 -m venv .venv
              fi
              source .venv/bin/activate
              pip install -r requirements.txt
            '';
          };
        }
      );
    };
}
