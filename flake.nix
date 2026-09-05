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
            while IFS= read -r license; do
              install -Dm444 "$license" "$out/share/licenses/$pname/$license"
            done < <(find . -type f -name LICENSE)

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
      checks = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python3.withPackages (ps: [ ps.fonttools ps.uharfbuzz ps.freetype-py ]);
        in {
          astra-pixel = pkgs.runCommand "astra-pixel-check" {
            nativeBuildInputs = [ python ];
          } ''
            cp -r ${self} source
            chmod -R u+w source
            cd source
            python scripts/check_astra_pixel.py > measured.json
            python scripts/check_pixel_mono.py
            cmp measured.json assets/previews/astra-pixel/metrics.json
            python scripts/build_astra_pixel.py --out rebuilt
            for font in fonts/astra-pixel/*.ttf; do
              cmp "$font" "rebuilt/$(basename "$font")"
            done
            python scripts/build_pixel_mono.py --out rebuilt-pixel --specimen rebuilt-pixel/specimen.html
            for font in fonts/pixel-mono/*.ttf; do
              cmp "$font" "rebuilt-pixel/$(basename "$font")"
            done
            cmp assets/previews/pixel-mono/specimen.html rebuilt-pixel/specimen.html
            python scripts/preview_astra_pixel.py
            cmp assets/previews/astra-pixel/comparison.html ${self}/assets/previews/astra-pixel/comparison.html
            python scripts/build_astra_pixel.py --family Text --alternate dotted-zero --alternate serif-ell --tracking 1 --leading 1 --out custom
            mkdir $out
            cp measured.json $out/metrics.json
          '';
        });
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = [
              (pkgs.python3.withPackages (ps: [ ps.fonttools ps.uharfbuzz ps.freetype-py ]))
            ];
          };
        });
    };
}
