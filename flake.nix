{
  description = "y0usaf's font collection";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      lib = nixpkgs.lib;
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = lib.genAttrs supportedSystems;
      families = lib.attrNames
        (lib.filterAttrs (_: type: type == "directory") (builtins.readDir ./fonts));
      mkFontPackage = pkgs: name: src: description:
        pkgs.stdenvNoCC.mkDerivation {
          pname = "y0usaf-fonts-${name}";
          version = "1.0.0";
          inherit src;

          installPhase = ''
            runHook preInstall

            mkdir -p $out/share/fonts/truetype $out/share/fonts/opentype
            find . -type f -name "*.ttf" -exec install -m444 -t $out/share/fonts/truetype {} +
            find . -type f -name "*.otf" -exec install -m444 -t $out/share/fonts/opentype {} +

            runHook postInstall
          '';

          meta = {
            inherit description;
            homepage = "https://github.com/y0usaf/fonts";
            platforms = lib.platforms.all;
            license = lib.licenses.agpl3Plus;
          };
        };
    in {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          familyPackages = lib.genAttrs families (name:
            mkFontPackage pkgs name (./fonts + "/${name}")
              "y0usaf's ${name} fonts and generated fast-reading variants");
        in familyPackages // {
          fonts = mkFontPackage pkgs "all" ./fonts
            "y0usaf's font collection and generated fast-reading variants";
          default = self.packages.${system}.fonts;
        });
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = [
              (pkgs.python3.withPackages (ps: [ ps.fonttools ps.uharfbuzz ]))
            ];
          };
        });
    };
}
