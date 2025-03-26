{ self, pkgs, system, nixpkgs, nixosVm }:
let
  start = pkgs.writeShellScriptBin "devserver" ''
    # Share project files with VM, mounted at /tmp/shared
    export SHARED_DIR=$(git rev-parse --show-toplevel)
    rm -f nixos.qcow2
    (${self.nixosConfigurations.devserver.config.system.build.vm}/bin/run-nixos-vm) &
  '';

  ssh = pkgs.writeShellScriptBin "devssh" ''
    ssh -o NoHostAuthenticationForLocalhost=yes root@localhost -p 2222
  '';
in
{
  apps = {
    devserver = {
      type = "app";
      program = "${start}/bin/devserver";
    };

    devssh = {
      type = "app";
      program = "${ssh}/bin/devssh";
    };
  };

  config = nixpkgs.lib.nixosSystem {
    inherit system pkgs;
    modules = [
      nixosVm.nixosModules.default
      {
        time.timeZone = "Europe/Oslo";
        system.stateVersion = "23.11";
        networking.firewall.allowedTCPPorts = [ 4222 8000 ];
        virtualisation = {
          diskSize = 10 * 1024; # 10GB
          memorySize = 5 * 1024; # 5GB
          useEFIBoot = true;

          forwardPorts = [
            { from = "host"; host.port = 4222; guest.port = 4222; } # Nats
            { from = "host"; host.port = 8000; guest.port = 8000; } # API
          ];
        };
        environment.systemPackages = with pkgs; [ natscli ];

        services.nats = {
          enable = true;
          jetstream = true;
          settings = {
            listen = "0.0.0.0:4222";
            client_advertise = "0.0.0.0:4222";
          };
        };
        systemd.services =
          let
            defaultConfig = {
              wantedBy = [ "multi-user.target" ];
              after = [ "nats.service" ];
            };
          in
          {
            parse = defaultConfig // {
              script = ''
                sleep 1;
                ${pkgs.nats-demo}/bin/pr-parse
              '';
            };
            reply = defaultConfig // {
              script = ''
                sleep 1;
                ${pkgs.nats-demo}/bin/pr-reply
              '';
            };
            api = defaultConfig // {
              path = [ (pkgs.python3.withPackages (ps: [ ps.uvicorn pkgs.nats-demo ])) ];
              script = ''
                sleep 1;
                uvicorn --host 0.0.0.0 nats_demo.primary_reserves.api:api
              '';
            };
          };
      }
    ];
  };
}
