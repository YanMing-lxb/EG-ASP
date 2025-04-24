"""
=======================================================================
·······································································
·······································································
····Y88b···d88P················888b·····d888·d8b·······················
·····Y88b·d88P·················8888b···d8888·Y8P·······················
······Y88o88P··················88888b·d88888···························
·······Y888P··8888b···88888b···888Y88888P888·888·88888b·····d88b·······
········888······"88b·888·"88b·888·Y888P·888·888·888·"88b·d88P"88b·····
········888···d888888·888··888·888··Y8P··888·888·888··888·888··888·····
········888··888··888·888··888·888···"···888·888·888··888·Y88b·888·····
········888··"Y888888·888··888·888·······888·888·888··888··"Y88888·····
································································888·····
··························································Y8b·d88P·····
···························································"Y88P"······
·······································································
=======================================================================

-----------------------------------------------------------------------
Author       : 焱铭
Date         : 2025-04-24 17:23:53 +0800
LastEditTime : 2025-04-24 19:47:54 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /EG-ASP/tools/build.py
Description  : 项目构建脚本
-----------------------------------------------------------------------
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目配置
PROJECT_NAME = "egasp"
ENTRY_POINT = Path("src/egasp/__main__.py")
DATA_DIR = Path("src/egasp/data")
ICON_FILE = Path("src/egasp/data/egasp.ico")
REQUIREMENTS = "requirements.txt"
VENV_NAME = "venv_egasp"  # 统一虚拟环境名称

def create_venv(venv_name=VENV_NAME):
    """创建隔离的虚拟环境"""
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_name], 
                      check=True,
                      stdout=subprocess.DEVNULL)
        print(f"✅ 虚拟环境 {venv_name} 创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return False

def install_dependencies(venv_name=VENV_NAME):
    """安装项目依赖"""
    pip_exec = "pip.exe" if os.name == "nt" else "pip"
    pip_path = Path(venv_name)/"Scripts"/pip_exec if os.name == "nt" else Path(venv_name)/"bin"/pip_exec
    
    if not pip_path.exists():
        print(f"❌ 找不到pip可执行文件: {pip_path}")
        return False

    try:
        # 安装项目依赖
        subprocess.run([str(pip_path), "install", "-r", REQUIREMENTS],
                      check=True,
                      stdout=subprocess.DEVNULL)
        
        # 单独安装PyInstaller
        subprocess.run([str(pip_path), "install", "pyinstaller"],
                      check=True,
                      stdout=subprocess.DEVNULL)
        
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def run_pyinstaller(venv_name=VENV_NAME):
    """使用PyInstaller打包应用程序"""
    pyinstaller_exec = "pyinstaller.exe" if os.name == "nt" else "pyinstaller"
    venv_bin_dir = "Scripts" if os.name == "nt" else "bin"
    pyinstaller_path = Path(venv_name)/venv_bin_dir/pyinstaller_exec

    # 验证PyInstaller安装
    if not pyinstaller_path.exists():
        print(f"❌ PyInstaller未正确安装: {pyinstaller_path}")
        return False

    # 转换为绝对路径
    data_dir = DATA_DIR.resolve()
    entry_file = ENTRY_POINT.resolve()
    
    # 构建参数配置
    args = [
        str(pyinstaller_path),
        "--onefile",
        "--clean",
        f"--name={PROJECT_NAME}",
        "--distpath=dist",
        "--workpath=build",
        "--specpath=build",
        "--add-data", f"{data_dir}{os.sep}*:.{os.sep}data",  # 使用绝对路径
        str(entry_file)  # 绝对路径
    ]

    # 系统特定配置
    if os.name == 'nt':  # Windows
        if ICON_FILE.exists():
            args.extend(["-i", str(ICON_FILE.resolve())])
    elif sys.platform == 'darwin':  # macOS
        args.extend([
            "--windowed",
            f"--osx-bundle-identifier=com.github.YanMing-lxb.{PROJECT_NAME}",
            "--target-architecture=universal2"
        ])
    else:  # Linux
        args.append("--strip")

    try:
        print("🔄 执行打包命令：")
        print(" ".join(args))  # 打印完整命令用于调试
        subprocess.run(args, check=True)
        print("✅ 应用程序打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False

def clean_up(venv_name=VENV_NAME):
    """清理构建环境"""
    try:
        # 删除虚拟环境
        if Path(venv_name).exists():
            shutil.rmtree(venv_name)
            print(f"✅ 删除虚拟环境: {venv_name}")
            
        # 清理构建产物
        build_artifacts = ["build", "__pycache__"]
        for artifact in build_artifacts:
            if Path(artifact).exists():
                shutil.rmtree(artifact)
                print(f"✅ 删除构建产物: {artifact}")
                
        # 清理spec文件
        for spec_file in Path().glob("*.spec"):
            spec_file.unlink()
            print(f"✅ 删除spec文件: {spec_file}")
            
        return True
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False

if __name__ == "__main__":
    exit_code = 0
    try:
        if not create_venv():
            exit_code = 1
        elif not install_dependencies():
            exit_code = 2
        elif not run_pyinstaller():
            exit_code = 3
    except Exception as e:
        error_messages = {
            FileNotFoundError: "必要文件缺失，请检查项目结构",
            PermissionError: "权限不足，请尝试管理员权限运行",
            subprocess.SubprocessError: "系统命令执行失败",
            Exception: f"未知错误发生: {str(e)}"
        }
        err_type = type(e)
        print(f"❗ {error_messages.get(err_type, '发生意外错误')}")
        exit_code = 99
    finally:
        clean_up()
        print(f"\n🛠️  构建流程完成，退出码: {exit_code}")
        sys.exit(exit_code)