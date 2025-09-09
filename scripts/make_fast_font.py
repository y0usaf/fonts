#!/usr/bin/env python3
"""
Make Fast Font - Create speed reading fonts from regular and bold font pairs.

Similar to addfeatures.py but specifically for creating Fast Fonts with proper
bold glyph variants and contextual alternates.
"""

from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.feaLib.parser import Parser
from argparse import ArgumentParser
import tempfile
import os
import sys


def make_fast_font_features():
    """Generate the Fast Font OpenType feature code."""
    return """
feature calt {
    @az = [a-z A-Z];
    @AZ = [a.bold-z.bold A.bold-Z.bold];
    @all = [@az @AZ];

    # Fast reading rules - bold first ~40% of each word
    # Based on Fast-Font implementation

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


def add_bold_glyphs(font, bold_font):
    """Add bold glyph variants to the regular font."""
    print("Adding bold glyph variants...")
    
    # Get character mappings
    regular_cmap = font.getBestCmap()
    bold_cmap = bold_font.getBestCmap()
    
    # Get glyph tables
    glyf = font['glyf']
    bold_glyf = bold_font['glyf']
    hmtx = font['hmtx']
    bold_hmtx = bold_font['hmtx']
    
    # Characters to process (a-z, A-Z)
    chars = []
    for i in range(ord('a'), ord('z') + 1):
        chars.append(chr(i))
    for i in range(ord('A'), ord('Z') + 1):
        chars.append(chr(i))
    
    added_count = 0
    
    for char in chars:
        unicode_val = ord(char)
        
        # Check if character exists in both fonts
        if unicode_val in regular_cmap and unicode_val in bold_cmap:
            regular_glyph = regular_cmap[unicode_val]
            bold_glyph = bold_cmap[unicode_val]
            
            # Create .bold variant name
            bold_variant = f"{regular_glyph}.bold"
            
            # Copy glyph outline from bold font
            if bold_glyph in bold_glyf:
                # Copy the glyph data
                glyf[bold_variant] = bold_glyf[bold_glyph]
                
                # Copy metrics
                if bold_glyph in bold_hmtx.metrics:
                    hmtx[bold_variant] = bold_hmtx[bold_glyph]
                
                added_count += 1
    
    print(f"Added {added_count} bold glyph variants")
    return added_count


def main():
    parser = ArgumentParser(
        description="Create Fast Font from regular and bold font files"
    )
    
    parser.add_argument(
        "regular", 
        help="Regular font file (.ttf or .otf)"
    )
    
    parser.add_argument(
        "bold",
        help="Bold font file (.ttf or .otf)" 
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output Fast Font file (default: adds _Fast suffix)"
    )
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output:
        output = args.output
    else:
        base = args.regular.rsplit('.', 1)[0]
        ext = args.regular.rsplit('.', 1)[1] if '.' in args.regular else 'ttf'
        output = f"{base}_Fast.{ext}"
    
    print(f"Creating Fast Font:")
    print(f"  Regular: {args.regular}")
    print(f"  Bold: {args.bold}")
    print(f"  Output: {output}")
    
    try:
        # Load fonts
        print("Loading fonts...")
        font = TTFont(args.regular)
        bold_font = TTFont(args.bold)
        
        # Add bold glyph variants
        added = add_bold_glyphs(font, bold_font)
        
        if added == 0:
            print("Warning: No bold glyphs were added")
        
        # Add Fast Font features
        print("Adding Fast reading features...")
        feature_code = make_fast_font_features()
        
        # Write to temp file and parse
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fea', delete=False) as f:
            f.write(feature_code)
            temp_fea = f.name
        
        try:
            with open(temp_fea, 'r') as f:
                addOpenTypeFeatures(font, f)
            print("✓ Fast reading features added")
        except Exception as e:
            print(f"Warning: Could not add features: {e}")
        finally:
            os.unlink(temp_fea)
        
        # Update font name
        if 'name' in font:
            name_table = font['name']
            for record in name_table.names:
                if record.nameID in [1, 4]:  # Family and full name
                    old_name = record.toUnicode()
                    if 'Fast' not in old_name:
                        record.string = f"{old_name} Fast"
        
        # Save the Fast Font
        print(f"Saving Fast Font to {output}")
        font.save(output)
        
        # Cleanup
        font.close()
        bold_font.close()
        
        print("✓ Fast Font created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()