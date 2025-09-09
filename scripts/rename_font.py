#!/usr/bin/env python3
"""
Flexible Font Renamer - Rename font family and full names in TTF/OTF files.

Usage: python rename_font.py <font_file> <new_name> [-o output_file]
"""

from fontTools.ttLib import TTFont
from argparse import ArgumentParser
import sys
import os


def rename_font(font_path, new_name, output_path=None):
    """
    Rename a font's family and full name.
    
    Args:
        font_path: Path to the input font file
        new_name: The new font family name
        output_path: Optional output path (defaults to overwriting input)
    """
    try:
        # Load the font
        font = TTFont(font_path)
        
        if 'name' not in font:
            raise ValueError("Font file does not contain a name table")
        
        name_table = font['name']
        updated_records = 0
        
        print(f"Renaming font: {font_path}")
        print(f"New name: {new_name}")
        
        # Update font names
        for record in name_table.names:
            if record.nameID == 1:  # Font Family name
                old_name = record.toUnicode()
                print(f"  Family name: '{old_name}' -> '{new_name}'")
                record.string = new_name
                updated_records += 1
            elif record.nameID == 4:  # Full font name
                old_name = record.toUnicode()
                # Keep style info if present (Regular, Bold, etc.)
                style_parts = old_name.split()
                if len(style_parts) > 1:
                    # Try to preserve style information
                    style = style_parts[-1]
                    if style.lower() in ['regular', 'bold', 'italic', 'light', 'medium', 'heavy']:
                        new_full_name = f"{new_name} {style}"
                    else:
                        new_full_name = f"{new_name} Regular"
                else:
                    new_full_name = f"{new_name} Regular"
                    
                print(f"  Full name: '{old_name}' -> '{new_full_name}'")
                record.string = new_full_name
                updated_records += 1
            elif record.nameID == 6:  # PostScript name
                old_name = record.toUnicode()
                # Create PostScript-safe name (no spaces, special chars)
                ps_name = new_name.replace(' ', '').replace('-', '').replace('_', '')
                print(f"  PostScript name: '{old_name}' -> '{ps_name}'")
                record.string = ps_name
                updated_records += 1
        
        if updated_records == 0:
            print("Warning: No name records were updated")
        else:
            print(f"Updated {updated_records} name records")
        
        # Save the font
        output = output_path or font_path
        print(f"Saving to: {output}")
        font.save(output)
        font.close()
        
        print("✓ Font renamed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = ArgumentParser(
        description="Rename font family and full names in TTF/OTF files"
    )
    
    parser.add_argument(
        "font_file",
        help="Path to the font file to rename"
    )
    
    parser.add_argument(
        "new_name",
        help="The new font family name"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (defaults to overwriting input file)"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview current font names without changing anything"
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.font_file):
        print(f"Error: Font file '{args.font_file}' not found")
        sys.exit(1)
    
    # Preview mode - just show current names
    if args.preview:
        try:
            font = TTFont(args.font_file)
            if 'name' in font:
                print(f"Current names in {args.font_file}:")
                name_table = font['name']
                for record in name_table.names:
                    if record.nameID in [1, 4, 6]:  # Family, Full, PostScript
                        name_type = {1: "Family", 4: "Full", 6: "PostScript"}[record.nameID]
                        print(f"  {name_type}: '{record.toUnicode()}'")
            font.close()
        except Exception as e:
            print(f"Error reading font: {e}")
        return
    
    # Rename the font
    success = rename_font(args.font_file, args.new_name, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()