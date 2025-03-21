{
  nixConfig.flake-registry = "https://raw.githubusercontent.com/fornybar/registry/main/registry.json";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          natscli
          python3
          python3Packages.nats-py
          python3Packages.requests
        ];
        shellHook = ''
          root=$(git rev-parse --show-toplevel)
          export PYTHONPATH=$PYTHONPATH:$root/src
          if [[ -f "$root/.env" ]]; then
            source $root/.env
          fi
        '';
      };
    };
}
