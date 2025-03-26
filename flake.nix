{
  nixConfig.flake-registry = "https://raw.githubusercontent.com/fornybar/registry/main/registry.json";

  outputs = { self, nixpkgs, nixosVm }:
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
      devServer = import ./devserver.nix {
        inherit self pkgs system nixpkgs nixosVm;
      };
    in
    {
      apps.${system} = devServer.apps;
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
      nixosConfigurations.devserver = devServer.config;
    };
}
