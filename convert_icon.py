from PIL import Image
import os

png_path = os.path.join("assets", "icons", "KDNAVIEN_icon_v1.2.png")
ico_path = os.path.join("assets", "icons", "KDNAVIEN.ico")

img = Image.open(png_path)
img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
print(f"Icon converted successfully: {ico_path}")