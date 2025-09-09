# Fast Fonts Collection

A collection of fast reading fonts including custom variants.

## Structure

```
├── fonts/              # Custom fast fonts
│   └── Go-Mono-Fast.ttf
├── Fast-Font/          # Original Fast-Font repository content
└── flake.nix          # Nix package definition
```

## Usage

### Install with Nix
```bash
# Install all fonts
nix profile install github:y0usaf/Fast-Fonts

# Install only custom fonts
nix profile install github:y0usaf/Fast-Fonts#custom-fast-fonts

# Install only original fonts  
nix profile install github:y0usaf/Fast-Fonts#original-fast-fonts
```

### Manual Installation
Copy font files to your system font directory and enable "Contextual Alternates" in applications that support OpenType features.

## Custom Fonts

### Go Mono Fast
Custom fast reading variant of the Go programming language's monospace font, optimized for code reading and programming.

## License
MIT