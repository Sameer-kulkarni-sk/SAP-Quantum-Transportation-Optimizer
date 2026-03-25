#!/usr/bin/env python3
"""
Create SAP logo icon for the application
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_sap_icon():
    """Create SAP logo icon"""

    # Create icon sizes
    sizes = [16, 32, 48, 64, 128, 256]

    for size in sizes:
        # Create image with SAP blue background
        img = Image.new('RGB', (size, size), color='#0070F2')
        draw = ImageDraw.Draw(img)

        # Calculate font size (approximately 60% of icon size)
        font_size = int(size * 0.6)

        try:
            # Try to use a bold font
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()

        # Draw "SAP" text in white
        text = "SAP"

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]

        # Draw text
        draw.text((x, y), text, fill='white', font=font)

        # Save icon
        icon_path = f"sap_icon_{size}.png"
        img.save(icon_path)
        print(f"Created {icon_path}")

    # Create main icon (256x256)
    print("\nCreating main SAP logo...")
    main_icon = Image.new('RGB', (256, 256), color='#0070F2')
    draw = ImageDraw.Draw(main_icon)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            font = ImageFont.load_default()

    text = "SAP"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - bbox[1]

    draw.text((x, y), text, fill='white', font=font)

    main_icon.save("sap_logo.png")
    print("Created sap_logo.png")

    # Create .ico file for Windows
    try:
        icon_img = Image.open("sap_icon_256.png")
        icon_img.save("sap_icon.ico", format='ICO', sizes=[
                      (16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print("Created sap_icon.ico")
    except Exception as e:
        print(f"Could not create .ico file: {e}")


if __name__ == "__main__":
    print("Creating SAP logo icons...")
    create_sap_icon()
    print("\nDone! Icons created successfully.")
