{
  description = "y0usaf's Fast Fonts Collection";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in {
      packages = forAllSystems (system: {
        # Custom fast fonts (your generated fonts)
        custom-fast-fonts = nixpkgs.legacyPackages.${system}.stdenvNoCC.mkDerivation {
          pname = "y0usaf-custom-fast-fonts";
          version = "1.0.0";
          src = ./fonts;

          installPhase = ''
            mkdir -p $out/share/fonts/truetype
            find . -name "*.ttf" -exec install -m444 {} $out/share/fonts/truetype/ \;
          '';

          meta = with nixpkgs.legacyPackages.${system}.lib; {
            description = "Custom fast reading fonts by y0usaf";
            homepage = "https://github.com/y0usaf/Fast-Fonts";
            platforms = platforms.all;
            license = licenses.mit;
          };
        };

        # Original fast fonts
        original-fast-fonts = nixpkgs.legacyPackages.${system}.stdenvNoCC.mkDerivation {
          pname = "original-fast-fonts";
          version = "1.0.0";
          src = ./Fast-Font;

          installPhase = ''
            mkdir -p $out/share/fonts/truetype
            install -m444 -Dt $out/share/fonts/truetype *.ttf
          '';

          meta = with nixpkgs.legacyPackages.${system}.lib; {
            description = "Original Fast Font Collection";
            homepage = "https://github.com/Born2Root/Fast-Font";
            platforms = platforms.all;
            license = licenses.mit;
          };
        };

        # All fonts combined
        default = nixpkgs.legacyPackages.${system}.buildEnv {
          name = "all-fast-fonts";
          paths = [ 
            self.packages.${system}.custom-fast-fonts
            self.packages.${system}.original-fast-fonts
          ];
        };
      });
    };
}