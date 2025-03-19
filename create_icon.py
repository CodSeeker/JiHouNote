import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """创建一个简单的图标文件"""
    try:
        # 检查PIL库是否安装
        import PIL
    except ImportError:
        print("正在安装PIL库...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    
    # 创建resources目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(project_dir, "resources")
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    icon_path = os.path.join(resources_dir, "icon.ico")
    
    # 如果图标已存在，则不重新创建
    if os.path.exists(icon_path):
        print(f"图标文件已存在: {icon_path}")
        return
    
    # 创建一个256x256的图像
    img = Image.new('RGBA', (256, 256), color=(53, 95, 171, 255))
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except IOError:
        font = ImageFont.load_default()
    
    # 在图像中心绘制文本
    text = "JH"
    text_width, text_height = draw.textsize(text, font=font)
    position = ((256 - text_width) // 2, (256 - text_height) // 2)
    draw.text(position, text, font=font, fill=(255, 255, 255, 255))
    
    # 保存为ICO文件
    img.save(icon_path, format='ICO')
    print(f"图标文件已创建: {icon_path}")

if __name__ == "__main__":
    create_icon()