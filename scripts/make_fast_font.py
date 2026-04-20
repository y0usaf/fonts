#!/usr/bin/env python3
"""
Make Fast Font - Create speed reading fonts from regular and bold font pairs.

Similar to addfeatures.py but specifically for creating Fast Fonts with proper
bold glyph variants and contextual alternates.
"""

from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from argparse import ArgumentParser
from fix_font_names import best_name, normalize_font_metadata
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


def transformed_glyph(glyph_set, glyph_name, transform):
    pen = TTGlyphPen(glyph_set)
    glyph_set[glyph_name].draw(TransformPen(pen, transform))
    return pen.glyph()


def transformed_lsb(glyph_set, glyph_name, transform, fallback_lsb):
    pen = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(TransformPen(pen, transform))
    return fallback_lsb if pen.bounds is None else round(pen.bounds[0])


def add_bold_glyphs(font, bold_font, *, bold_scale_x=1.0):
    """Add bold glyph variants to the regular font."""
    print("Adding bold glyph variants...")
    
    # Get character mappings
    regular_cmap = font.getBestCmap()
    bold_cmap = bold_font.getBestCmap()
    
    # Get glyph tables
    glyf = font['glyf']
    hmtx = font['hmtx']
    bold_metrics = bold_font['hmtx'].metrics
    bold_glyph_set = bold_font.getGlyphSet()
    
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
            
            if bold_glyph in bold_metrics:
                adv, lsb = bold_metrics[bold_glyph]
                transform = Transform(1, 0, 0, 1, 0, 0)
                if bold_scale_x != 1.0:
                    advance_center = adv / 2
                    transform = Transform().translate(advance_center, 0).scale(bold_scale_x, 1).translate(-advance_center, 0)
                glyf[bold_variant] = transformed_glyph(bold_glyph_set, bold_glyph, transform)
                hmtx[bold_variant] = (adv, transformed_lsb(bold_glyph_set, bold_glyph, transform, lsb))
                added_count += 1
    
    print(f"Added {added_count} bold glyph variants")
    return added_count


def source_family_subfamily(font):
    if 'name' not in font:
        return None, None
    nt = font['name']
    family = best_name(nt, 16) or best_name(nt, 1)
    subfamily = best_name(nt, 17) or best_name(nt, 2)
    return family, subfamily


def fast_family_name(family: str | None) -> str | None:
    if not family:
        return None
    family = family.strip()
    return family if family.startswith("Fast ") else f"Fast {family}"


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
    parser.add_argument(
        "--bold-scale-x",
        type=float,
        default=1.0,
        help="Horizontally scale copied bold glyphs (default: 1.0)"
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
        added = add_bold_glyphs(font, bold_font, bold_scale_x=args.bold_scale_x)
        
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
        
        # Normalize metadata when the source style maps cleanly to RIBBI.
        family, subfamily = source_family_subfamily(font)
        if family and subfamily:
            meta = normalize_font_metadata(font, fast_family_name(family), subfamily)
            print(f"✓ Metadata normalized: {meta['full']}")
        elif 'name' in font:
            name_table = font['name']
            for record in name_table.names:
                if record.nameID in [1, 4]:
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