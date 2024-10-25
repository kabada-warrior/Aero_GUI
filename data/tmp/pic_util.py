from PIL import Image

# 打开原始图像
img = Image.open("/Users/xuehao/Desktop/code_proj/aero_1_GUI/data/tmp/school_symbol.png")

# 创建不同尺寸的图像
sizes = [16, 32, 64, 128, 256, 512, 1024]
for size in sizes:
    resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
    resized_img.save(f"/Users/xuehao/Desktop/code_proj/aero_1_GUI/data/pic/icon_{size}x{size}.png")

for size in sizes:
    retina_size = size * 2
    resized_img = img.resize((retina_size, retina_size), Image.Resampling.LANCZOS)
    resized_img.save(f"/Users/xuehao/Desktop/code_proj/aero_1_GUI/data/pic/icon_{size}x{size}@2x.png")