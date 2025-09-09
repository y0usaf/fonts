#!/usr/bin/env python3
"""
Fast Font Generator

This script generates Fast Font variants with different reading optimization techniques.
Uses fontTools and other font manipulation libraries to create speed reading fonts.

Requirements:
- fonttools: Font manipulation library
- defcon: Font object library
- ufoLib2: UFO font format support
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict

try:
    from fontTools.ttLib import TTFont
    from fontTools.feaLib.builder import addOpenTypeFeatures
    from fontTools.feaLib.parser import Parser
    from fontTools.misc.loggingTools import configLogger
except ImportError:
    print("Error: fonttools not installed. Install with: uv add fonttools")
    sys.exit(1)


class FastFontGenerator:
    """Generator for Fast Font variants with reading optimization features."""
    
    def __init__(self, base_font_path: str):
        """Initialize with a base font file."""
        self.base_font_path = Path(base_font_path)
        if not self.base_font_path.exists():
            raise FileNotFoundError(f"Base font not found: {base_font_path}")
        
        self.font = TTFont(str(self.base_font_path))
        
    def create_fast_reading_feature(self, bold_percentage: float = 0.4) -> str:
        """
        Create OpenType feature code for fast reading (bionic reading style).
        
        Args:
            bold_percentage: Percentage of word to make bold (0.0-1.0)
        """
        feature_code = """
feature calt {
    @az = [a-z A-Z];
    @AZ = [a.bold-z.bold A.bold-Z.bold];
    @all = [@az @AZ];

    # Word length rules based on percentage
    # For words <= 3 characters: 1 character bold
    # For word == 4 characters: 2 characters bold  
    # For words > 4 characters: ~40% bold (rounded)

    # 17+ character words (7 chars bold)
    ignore sub @all @all @all @all @all @all @all @az' @all @all @all @all @all @all @all @all @all @all;
    sub @all @all @all @all @all @all @az' @all @all @all @all @all @all @all @all @all @all by @AZ;

    # 14-16 character words (6 chars bold)
    ignore sub @all @all @all @all @all @all @az' @all @all @all @all @all @all @all @all;
    sub @all @all @all @all @all @az' @all @all @all @all @all @all @all @all by @AZ;

    # 12-13 character words (5 chars bold)
    ignore sub @all @all @all @all @all @az' @all @all @all @all @all @all;
    sub @all @all @all @all @az' @all @all @all @all @all @all @all by @AZ;

    # 9-11 character words (4 chars bold)
    ignore sub @all @all @all @all @az' @all @all @all @all @all;
    sub @all @all @all @az' @all @all @all @all @all by @AZ;

    # 7-8 character words (3 chars bold)
    ignore sub @all @all @all @az' @all @all @all @all;
    sub @all @all @az' @all @all @all @all by @AZ;

    # 4-6 character words (2 chars bold)
    ignore sub @all @all @az' @all @all;
    sub @all @az' @all @all by @AZ;

    # 1-3 character words (1 char bold)
    ignore sub @all @az';
    sub @az' by @AZ;
} calt;
"""
        return feature_code

    def generate_fast_variant(self, output_path: str, variant_name: str = "Fast") -> None:
        """Generate a fast reading variant of the font."""
        print(f"Generating {variant_name} variant...")
        
        # Create a copy of the font
        new_font = TTFont(str(self.base_font_path))
        
        # Add fast reading features
        feature_code = self.create_fast_reading_feature()
        
        try:
            # Parse and add the feature
            parser = Parser(feature_code, followIncludes=False)
            feature_table = parser.parse()
            addOpenTypeFeatures(new_font, feature_table)
            
            # Update font names
            name_table = new_font['name']
            for name_record in name_table.names:
                if name_record.nameID == 1:  # Font Family name
                    name_record.string = f"{name_record.toUnicode()} {variant_name}"
                elif name_record.nameID == 4:  # Full font name
                    name_record.string = f"{name_record.toUnicode()} {variant_name}"
            
            # Save the new font
            new_font.save(output_path)
            print(f"✓ Generated: {output_path}")
            
        except Exception as e:
            print(f"✗ Error generating {variant_name} variant: {e}")
        finally:
            new_font.close()

    def generate_dotted_variant(self, output_path: str) -> None:
        """Generate a variant with dots as space markers (Space Reading technique)."""
        print("Generating Dotted variant...")
        
        # This would require more complex glyph manipulation
        # For now, create a basic variant
        new_font = TTFont(str(self.base_font_path))
        
        # Update font names
        name_table = new_font['name']
        for name_record in name_table.names:
            if name_record.nameID == 1:
                name_record.string = f"{name_record.toUnicode()} Dotted"
            elif name_record.nameID == 4:
                name_record.string = f"{name_record.toUnicode()} Dotted"
        
        new_font.save(output_path)
        new_font.close()
        print(f"✓ Generated: {output_path}")

    def list_font_info(self) -> Dict[str, str]:
        """Get basic information about the font."""
        info = {}
        if 'name' in self.font:
            name_table = self.font['name']
            for name_record in name_table.names:
                if name_record.nameID == 1:  # Family name
                    info['family'] = name_record.toUnicode()
                elif name_record.nameID == 2:  # Subfamily
                    info['subfamily'] = name_record.toUnicode()
                elif name_record.nameID == 4:  # Full name
                    info['full_name'] = name_record.toUnicode()
        return info


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Generate Fast Font variants for speed reading",
        epilog="Example: python generate_fonts.py fonts/MyFont.ttf --all"
    )
    
    parser.add_argument(
        "font_path", 
        help="Path to the base font file (.ttf or .otf)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        default="./fonts",
        help="Output directory for generated fonts (default: ./fonts)"
    )
    
    parser.add_argument(
        "--fast", 
        action="store_true",
        help="Generate Fast reading variant"
    )
    
    parser.add_argument(
        "--dotted",
        action="store_true", 
        help="Generate Dotted (Space Reading) variant"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all variants"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show font information and exit"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()
    
    if args.verbose:
        configLogger(level="INFO")
    
    try:
        generator = FastFontGenerator(args.font_path)
        
        if args.info:
            info = generator.list_font_info()
            print("Font Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            return
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        base_name = Path(args.font_path).stem
        
        # Generate requested variants
        if args.all or args.fast:
            output_path = output_dir / f"{base_name}_Fast.ttf"
            generator.generate_fast_variant(str(output_path))
        
        if args.all or args.dotted:
            output_path = output_dir / f"{base_name}_Dotted.ttf"
            generator.generate_dotted_variant(str(output_path))
        
        if not any([args.fast, args.dotted, args.all, args.info]):
            print("No variants specified. Use --help for options.")
            print("Quick start: python generate_fonts.py font.ttf --all")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()