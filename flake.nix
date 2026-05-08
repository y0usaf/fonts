{
  description = "y0usaf's font collection";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          fonts = pkgs.stdenvNoCC.mkDerivation {
            pname = "y0usaf-fonts";
            version = "1.0.0";
            src = ./fonts;

            installPhase = ''
              runHook preInstall

              mkdir -p $out/share/fonts/truetype $out/share/fonts/opentype
              find . -type f -name "*.ttf" -exec install -m444 -t $out/share/fonts/truetype {} +
              find . -type f -name "*.otf" -exec install -m444 -t $out/share/fonts/opentype {} +

              runHook postInstall
            '';

            meta = with pkgs.lib; {
              description = "y0usaf's font collection and generated fast-reading variants";
              homepage = "https://github.com/y0usaf/fonts";
              platforms = platforms.all;
              license = licenses.agpl3Plus;
            };
          };

          default = self.packages.${system}.fonts;
        });
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = [
              (pkgs.python3.withPackages (ps: [ ps.fonttools ]))
            ];
          };
        });
    };
}
