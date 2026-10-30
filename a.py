from PIL import Image

# Tomar PNG file er path
img = Image.open("Plan.png").convert("RGBA")

# Multiple sizes soho ICO save
img.save("icon.ico", format="ICO",
         sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icon.ico created successfully")