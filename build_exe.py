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

def build_exe():
    """打包为EXE文件"""
    print("开始打包JiHouNote...")
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置打包命令
    main_script = os.path.join(project_dir, "src", "main.py")
    icon_path = os.path.join(project_dir, "resources", "icon.ico")
    resources_dir = os.path.join(project_dir, "resources")
    
    # 应用程序名称
    app_name = "JiHouNote"  # 修改这里，将应用名称改为JiHouNote
    
    # 检查图标文件是否存在，如果不存在则使用默认图标
    icon_param = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
    
    # 构建命令
    cmd = [
        "pyinstaller",
        f"--name={app_name}",  # 使用新的应用名称
        "--windowed",  # 不显示控制台窗口
        "--onefile",   # 打包为单个EXE文件
        icon_param,
        # 资源文件添加
        "--add-data", f"{resources_dir};resources",
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
        
        # 打包完成后，将dist目录中的EXE文件复制到项目根目录
        exe_path = os.path.join(project_dir, "dist", f"{app_name}.exe")
        if os.path.exists(exe_path):
            target_path = os.path.join(project_dir, f"{app_name}.exe")
            shutil.copy2(exe_path, target_path)
            print(f"\n打包成功！EXE文件已复制到: {target_path}")
        else:
            print(f"\n打包可能成功，但未找到EXE文件: {exe_path}")
            print("正在检查dist目录内容...")
            dist_dir = os.path.join(project_dir, "dist")
            if os.path.exists(dist_dir):
                print("dist目录中的文件:")
                for file in os.listdir(dist_dir):
                    print(f" - {file}")
                
                # 尝试复制找到的第一个exe文件
                exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
                if exe_files:
                    first_exe = exe_files[0]
                    target_path = os.path.join(project_dir, first_exe)
                    shutil.copy2(os.path.join(dist_dir, first_exe), target_path)
                    print(f"已复制找到的EXE文件: {first_exe} 到项目根目录")
            else:
                print("dist目录不存在，打包可能失败")
    
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("JiHouNote - 打包工具")
    print("=" * 40)
    
    # 检查是否安装了PyInstaller
    if not check_pyinstaller():
        print("未检测到PyInstaller，需要先安装")
        install_pyinstaller()
    
    # 打包为EXE
    if build_exe():
        print("\n打包过程完成！")
    else:
        print("\n打包过程出错，请查看上面的错误信息。")
    
    input("\n按Enter键退出...")