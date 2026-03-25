#!/usr/bin/env python3
"""
Create official SAP-style icon and logo for Quantum Transport Optimizer
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Install with: pip install pillow")


def create_sap_logo(size=200):
    """Create official SAP logo style"""
    if not PIL_AVAILABLE:
        return None

    # SAP official colors
    sap_blue = (0, 51, 102)  # #003366
    sap_gold = (240, 171, 0)  # #F0AB00
    white = (255, 255, 255)

    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw SAP logo box (official style)
    box_height = size // 3
    box_y = (size - box_height) // 2

    # Blue background box
    draw.rectangle([0, box_y, size, box_y + box_height],
                   fill=sap_blue)

    # SAP text
    try:
        font_size = box_height // 2
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "SAP"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (size - text_width) // 2
        text_y = box_y + (box_height - text_height) // 2

        draw.text((text_x, text_y), text, fill=white, font=font)
    except:
        pass

    return img


def create_icon(size=256):
    """Create professional SAP-style icon with gradient and modern design"""
    if not PIL_AVAILABLE:
        print("Cannot create icon without PIL/Pillow")
        return

    # SAP Colors
    sap_blue = (0, 51, 102)      # #003366
    sap_gold = (240, 171, 0)     # #F0AB00
    sap_light_blue = (0, 102, 204)  # Lighter blue for gradient
    white = (255, 255, 255)

    # Create image with gradient background
    img = Image.new('RGB', (size, size), sap_blue)
    draw = ImageDraw.Draw(img)

    # Add subtle gradient effect
    for y in range(size):
        gradient_factor = y / size
        r = int(sap_blue[0] + (sap_light_blue[0] -
                sap_blue[0]) * gradient_factor * 0.3)
        g = int(sap_blue[1] + (sap_light_blue[1] -
                sap_blue[1]) * gradient_factor * 0.3)
        b = int(sap_blue[2] + (sap_light_blue[2] -
                sap_blue[2]) * gradient_factor * 0.3)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    center = size // 2

    # Draw modern truck icon (simplified logistics symbol)
    truck_width = size // 2
    truck_height = size // 3
    truck_x = center - truck_width // 2
    truck_y = center - truck_height // 2

    # Truck body
    draw.rectangle([truck_x, truck_y, truck_x + truck_width * 0.6, truck_y + truck_height],
                   fill=sap_gold, outline=white, width=2)

    # Truck cab
    cab_width = truck_width * 0.3
    draw.rectangle([truck_x + truck_width * 0.65, truck_y + truck_height * 0.3,
                    truck_x + truck_width, truck_y + truck_height],
                   fill=sap_gold, outline=white, width=2)

    # Wheels
    wheel_radius = size // 20
    wheel_y = truck_y + truck_height + wheel_radius // 2
    draw.ellipse([truck_x + truck_width * 0.2 - wheel_radius, wheel_y - wheel_radius,
                  truck_x + truck_width * 0.2 + wheel_radius, wheel_y + wheel_radius],
                 fill=white, outline=sap_gold, width=2)
    draw.ellipse([truck_x + truck_width * 0.8 - wheel_radius, wheel_y - wheel_radius,
                  truck_x + truck_width * 0.8 + wheel_radius, wheel_y + wheel_radius],
                 fill=white, outline=sap_gold, width=2)

    # Quantum symbol overlay (small)
    q_size = size // 6
    q_x = truck_x + truck_width * 0.25
    q_y = truck_y + truck_height * 0.3

    # Small quantum circuit
    draw.ellipse([q_x, q_y, q_x + q_size, q_y + q_size],
                 outline=white, width=2)
    draw.line([q_x + q_size//2, q_y, q_x + q_size//2, q_y + q_size],
              fill=white, width=2)
    draw.ellipse([q_x + q_size//3, q_y + q_size//3,
                  q_x + q_size*2//3, q_y + q_size*2//3],
                 fill=white)

    # Add "SAP" text at top
    try:
        font_size = size // 8
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "SAP"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = center - text_width // 2
        text_y = size // 10

        draw.text((text_x, text_y), text, fill=sap_gold, font=font)
    except:
        pass

    # Add "Quantum Transport" text at bottom
    try:
        font_size_small = size // 12
        try:
            font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_small)
        except:
            font_small = ImageFont.load_default()

        text = "Quantum Transport"
        bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = bbox[2] - bbox[0]
        text_x = center - text_width // 2
        text_y = size - size // 6

        draw.text((text_x, text_y), text, fill=white, font=font_small)
    except:
        pass

    # Save icon
    img.save('icon.png')
    print(f"✓ Icon created: icon.png ({size}x{size})")

    # Create smaller versions
    for small_size in [128, 64, 32]:
        small_img = img.resize((small_size, small_size),
                               Image.Resampling.LANCZOS)
        small_img.save(f'icon_{small_size}.png')
        print(f"✓ Icon created: icon_{small_size}.png")

    # Create SAP logo for GUI
    sap_logo = create_sap_logo(200)
    if sap_logo:
        sap_logo.save('sap_logo.png')
        print(f"✓ SAP logo created: sap_logo.png (200x200)")


if __name__ == "__main__":
    create_icon(256)
