import os
import subprocess
import sys
import shutil

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("PyInstaller安装完成")

def build_mac_app():
    """为Mac打包应用程序"""
    print("开始为Mac打包JiHouNote...")
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置打包命令
    main_script = os.path.join(project_dir, "src", "main.py")
    icon_path = os.path.join(project_dir, "resources", "icon.icns")  # Mac使用.icns格式图标
    resources_dir = os.path.join(project_dir, "resources")
    
    # 应用程序名称
    app_name = "JiHouNote"
    
    # 检查图标文件是否存在
    icon_param = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
    
    # 构建命令 - Mac版本使用:分隔符而不是;
    cmd = [
        "pyinstaller",
        f"--name={app_name}",
        "--windowed",  # 不显示控制台窗口
        "--onefile",   # 打包为单个应用
        icon_param,
        # Mac上资源文件路径分隔符为:
        "--add-data", f"{resources_dir}:resources",
        "--noconfirm",  # 不询问确认
        "--clean",      # 清理临时文件
        main_script
    ]
    
    # 过滤掉空参数
    cmd = [item for item in cmd if item]
    
    print("执行命令:", " ".join(cmd))
    
    # 执行打包命令
    try:
        subprocess.check_call(cmd)
        
        # 打包完成后，检查应用是否生成
        app_path = os.path.join(project_dir, "dist", f"{app_name}.app")
        if os.path.exists(app_path):
            print(f"\n打包成功！Mac应用已生成: {app_path}")
        else:
            print(f"\n打包可能成功，但未找到应用。请检查dist目录。")
            # 列出dist目录内容
            dist_dir = os.path.join(project_dir, "dist")
            if os.path.exists(dist_dir):
                print("dist目录中的文件:")
                for file in os.listdir(dist_dir):
                    print(f" - {file}")
    
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("JiHouNote - Mac打包工具")
    print("=" * 40)
    
    # 检查是否在Mac系统上运行
    if sys.platform != "darwin":
        print("错误: 此脚本只能在Mac系统上运行")
        print(f"当前系统: {sys.platform}")
        input("\n按Enter键退出...")
        sys.exit(1)
    
    # 检查是否安装了PyInstaller
    if not check_pyinstaller():
        print("未检测到PyInstaller，需要先安装")
        install_pyinstaller()
    
    # 打包为Mac应用
    if build_mac_app():
        print("\n打包过程完成！")
    else:
        print("\n打包过程出错，请查看上面的错误信息。")
    
    input("\n按Enter键退出...")