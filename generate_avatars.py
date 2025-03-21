import os
from PIL import Image, ImageDraw, ImageFont
import hashlib
import random

# Create directory if it doesn't exist
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Function to generate an avatar with initials based on a name
def generate_avatar(filename, name, size=(128, 128)):
    # Create a hash from the name to get consistent colors
    hash_object = hashlib.md5(name.encode())
    hash_hex = hash_object.hexdigest()
    
    # Use hash to determine background color (keep it in dark/medium range for readability)
    r = int(hash_hex[0:2], 16) % 156 + 50  # Range 50-205
    g = int(hash_hex[2:4], 16) % 156 + 50  # Range 50-205
    b = int(hash_hex[4:6], 16) % 156 + 50  # Range 50-205
    
    # Create the image with the background color
    img = Image.new('RGB', size, color=(r, g, b))
    d = ImageDraw.Draw(img)
    
    # Get initials from the name
    initials = ''.join([name[0].upper() for name in name.split() if name])
    if not initials:
        initials = "?"
    
    # Use a default font
    try:
        font_size = size[0] // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # If the font is not available, use default
        font = ImageFont.load_default()
    
    # Calculate text size and position
    text_width, text_height = d.textbbox((0, 0), initials, font=font)[2:4]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text in white
    d.text(position, initials, fill=(255, 255, 255), font=font)
    
    # Save the image
    img.save(f'static/images/{filename}')
    print(f"Created avatar: {filename}")

# Generate avatars for users
users = [
    ("user1.jpg", "Emily Chen"),
    ("user2.jpg", "Marcus Kim"),
    ("user3.jpg", "Sarah Johnson"),
    ("user4.jpg", "Jordan Taylor"),
    ("user5.jpg", "Aisha Patel"),
    ("user6.jpg", "Alex Wong")
]

for filename, name in users:
    generate_avatar(filename, name)

print("Avatar generation complete.")
