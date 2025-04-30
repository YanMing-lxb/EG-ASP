import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

from rich.theme import Theme
from rich.console import Console

if sys.stdout.encoding != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ======================
# 主题与样式配置
# ======================
custom_theme = Theme({
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "bold blue",
    "status": "bold cyan",
    "time": "bold magenta"
})
console = Console(theme=custom_theme,legacy_windows=False)

# ======================
# 项目配置
# ======================
PROJECT_NAME = "egasp"
ENTRY_POINT = Path("src/egasp/__main__.py")
DATA_DIR = Path("src/egasp/data")
ICON_FILE = Path("src/egasp/data/egasp.ico")
REQUIREMENTS = "requirements.txt"
VENV_NAME = "venv_egasp"

BUILD_CONFIG = {
    "common": ["--onefile", "--clean"],
    "windows": ["--noconsole"] if os.name == 'nt' else [],
    "macos": ["--windowed", "--target-architecture=universal2"],
    "linux": ["--strip"]
}

# ======================
# 工具函数
# ======================
def get_venv_tool(venv_name: str, tool_name: str) -> Path:
    """获取虚拟环境工具路径"""
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    ext = ".exe" if os.name == "nt" else ""
    return Path(venv_name) / bin_dir / f"{tool_name}{ext}"

def format_duration(seconds: float) -> str:
    """格式化时间显示"""
    if seconds > 60:
        return f"{seconds // 60:.0f}m {seconds % 60:.1f}s"
    return f"{seconds:.2f}s"

def run_command(command: list, success_msg: str, error_msg: str, process_name: str = "执行命令") -> bool:
    """
    通用命令执行函数
    :param command: 要执行的命令列表
    :param success_msg: 成功时显示的消息（支持富文本样式）
    :param error_msg: 失败时的错误提示前缀
    :param process_name: 正在进行的操作名称（用于状态提示）
    :return: 执行是否成功
    """
    try:
        console.print(f"[dim]执行命令: {' '.join(command)}[/]")
        start_time = time.time()
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        with console.status(f"[status]正在{process_name}..."):  # 动态状态提示
            while True:
                output = process.stdout.readline()
                if not output and process.poll() is not None:
                    break
                if output:
                    console.print(f"[dim]{output.strip()}[/]")

        if process.returncode == 0:
            console.print(
                f"✓ {success_msg} "
                f"[time](耗时: {format_duration(time.time()-start_time)})[/]",
                style="success"
            )
            return True
            
        raise subprocess.CalledProcessError(
            process.returncode, 
            command, 
            f"退出码: {process.returncode}"
        )
        
    except subprocess.CalledProcessError as e:
        console.print(f"✗ {error_msg}: {e}", style="error")
        return False

# ======================
# 核心功能
# ======================
def pre_check() -> bool:
    """打包前环境检查"""
    check_items = {
        "Python版本": (sys.version_info >= (3,8), "需要Python 3.8+"),
        "入口文件": (ENTRY_POINT.exists(), f"缺失入口文件 {ENTRY_POINT}"),
        "依赖文件": (Path(REQUIREMENTS).exists(), f"缺失依赖文件 {REQUIREMENTS}"),
        "数据目录": (DATA_DIR.exists(), f"缺失数据目录 {DATA_DIR}")
    }
    console.print("🔍 开始环境检查", style="status")
    all_ok = True
    for name, (condition, msg) in check_items.items():
        if not condition:
            console.print(f"✗ {name}检查失败: {msg}", style="error")
            all_ok = False
            
    return all_ok

def create_venv(venv_name: str = VENV_NAME) -> bool:
    """创建隔离的虚拟环境"""
    console.print("🌱 开始创建虚拟环境", style="status")
    command = [
        sys.executable,
        "-m", "venv",
        venv_name
    ]
    
    success = run_command(
        command=command,
        success_msg=f"虚拟环境 [bold]{venv_name}[/] 创建成功",
        error_msg="虚拟环境创建失败",
        process_name="创建虚拟环境"
    )
    
    if not success:
        console.print("⚠️ 建议检查：\n1. Python环境是否正常\n2. 磁盘空间是否充足\n3. 权限是否足够", style="warning")
        
    return success

def install_dependencies(venv_name: str = VENV_NAME) -> bool:
    """安装项目依赖"""
    pip_path = get_venv_tool(venv_name, "pip")
    
    if not pip_path.exists():
        console.print(f"✗ 找不到pip可执行文件: [underline]{pip_path}[/]", style="error")
        return False

    console.print("📦 开始安装依赖", style="status")
    
    return all([
        run_command(
            command=[str(pip_path), "install", "-r", REQUIREMENTS],
            success_msg="项目依赖安装完成",
            error_msg="项目依赖安装失败",
            process_name="安装项目依赖"
        ),
        run_command(
            command=[str(pip_path), "install", "pyinstaller"],
            success_msg="PyInstaller安装完成",
            error_msg="PyInstaller安装失败",
            process_name="安装PyInstaller"
        )
    ])

def run_pyinstaller(venv_name: str = VENV_NAME) -> bool:
    """使用PyInstaller打包应用程序"""
    pyinstaller_path = get_venv_tool(venv_name, "pyinstaller")
    
    if not pyinstaller_path.exists():
        console.print(f"✗ PyInstaller未正确安装: {pyinstaller_path}", style="error")
        return False

    # 打包参数配置
    args = [
        str(pyinstaller_path),
        *BUILD_CONFIG["common"],
        f"--name={PROJECT_NAME}",
        "--distpath=dist",
        "--workpath=build",
        "--specpath=build",
        "--add-data", f"{DATA_DIR.resolve()}{os.sep}*:.{os.sep}data",
        str(ENTRY_POINT.resolve())
    ]

    # 平台特定配置
    if os.name == 'nt' and ICON_FILE.exists():
        args.extend(["-i", str(ICON_FILE.resolve())])
    elif sys.platform == 'darwin':
        args.extend(BUILD_CONFIG["macos"])
    else:
        args.extend(BUILD_CONFIG["linux"])

    return run_command(
        command=args,
        success_msg=f"应用程序打包成功 → [bold underline]dist/{PROJECT_NAME}[/]",
        error_msg="打包失败",
        process_name="打包应用程序"
    )

def verify_pack() -> bool:
    """验证打包结果"""
    exe_path = Path("dist") / (PROJECT_NAME + (".exe" if os.name == "nt" else ""))
    
    checks = [
        (exe_path.exists(), "可执行文件未生成"),
        (exe_path.stat().st_size > 1024*1024, "可执行文件大小异常（<1MB）")
    ]
    
    all_ok = True
    for condition, msg in checks:
        if not condition:
            console.print(f"✗ 验证失败: {msg}", style="error")
            all_ok = False
            
    return all_ok

def clean_up():
    """清理打包环境"""
    try:
        # if Confirm.ask("⚠️  确定要清理打包环境吗？", default=True):
        # 清理打包产物
        for artifact in ["build", "__pycache__", VENV_NAME]:
            if Path(artifact).exists():
                shutil.rmtree(artifact)
                console.print(f"✓ 删除打包产物: {artifact}", style="info")
                
        # 清理spec文件
        for spec_file in Path().glob("*.spec"):
            spec_file.unlink()
            console.print(f"✓ 删除spec文件: {spec_file}", style="info")
            
        console.print("✓ 环境清理完成", style="success")
        return True
    except Exception as e:
        console.print(f"✗ 清理失败: {e}", style="error")
        return False

def modify_state_param(main_file, new_state):
    """修改主程序中的STATE参数，返回原始值"""
    try:
        with open(main_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if line.strip().startswith("STATE ="):
                original_line = line
                # 保留原有缩进和格式
                original_state = line.split("=")[1].strip()
                indent = line[:line.find("STATE")]
                lines[i] = f"{indent}STATE = '{new_state}'\n"
                break
        
        if original_line is None:
            console.print("✗ 找不到STATE定义", style="error")
            return False, None
        
        with open(main_file, "w", encoding="utf-8") as file:
            file.writelines(lines)
        
        console.print(f"✓ STATE参数已修改为 {new_state}", style="success")
        return True, original_state
    
    except Exception as e:
        console.print(f"✗ 修改STATE失败: {e}", style="error")
        return False, None

def restore_state_param(main_file, original_state):
    """恢复主程序中的STATE参数"""
    try:
        with open(main_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if line.strip().startswith("STATE ="):
                # 仅替换值部分，保留原有格式
                before = line.split("=")[0]
                lines[i] = f"{before}= {original_state}\n"
                break
        
        with open(main_file, "w", encoding="utf-8") as file:
            file.writelines(lines)
        
        console.print(f"✓ STATE参数已恢复为 {original_state}", style="success")
    
    except Exception as e:
        console.print(f"✗ 恢复STATE失败: {e}", style="error")

# ======================
# 主流程
# ======================
if __name__ == "__main__":
    new_state = "input"
    main_file = Path("./src/egasp/__main__.py")
    try:
        console.rule(f"[bold]🚀 {PROJECT_NAME} 打包系统[/]")
        
        if not pre_check():
            console.rule("[bold red]❌ 预检查失败，打包终止！[/]")
            sys.exit(1)
        
        success_modify, original_state = modify_state_param(main_file, new_state)
        if not success_modify:
            console.rule("[bold red]❌ 修改STATE参数失败，终止打包！[/]")
            sys.exit(1)

        success = all([
            create_venv(),
            install_dependencies(),
            run_pyinstaller(),
            verify_pack()
        ])

        if success:
            console.rule("[bold green]✅ 打包成功！[/]")
            console.print(f"生成的可执行文件位于：[bold underline]dist/{PROJECT_NAME}[/]")
            clean_up()
        else:
            console.rule("[bold red]❌ 打包失败！[/]")

    except PermissionError as e:
        console.print(f"✗ 权限错误: {e}", style="error")
        console.print("建议：尝试以管理员权限运行本脚本", style="warning")
    except FileNotFoundError as e:
        console.print(f"✗ 文件缺失: {e}", style="error")
    except Exception as e:
        console.rule("[bold red]💥 发生未捕获异常！[/]")
        console.print_exception(show_locals=True)
    finally:
        # 状态参数被恢复
        if original_state is not None:
            restore_state_param(main_file, original_state)