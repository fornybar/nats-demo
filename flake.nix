{
  nixConfig.flake-registry = "https://raw.githubusercontent.com/fornybar/registry/main/registry.json";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          (final: prev: {
            nats-demo = import ./default.nix { python = final.python3; };
          })
        ];
      };
    in
    {
      packages.${system}.default = pkgs.nats-demo;
      devShells.${system}.default = pkgs.mkShell {
        inputsFrom = [ self.packages.${system}.default ];
        packages = with pkgs; [
          nats-server
          natscli
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
