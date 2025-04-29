'''
 =======================================================================
 ····Y88b···d88P················888b·····d888·d8b·······················
 ·····Y88b·d88P·················8888b···d8888·Y8P·······················
 ······Y88o88P··················88888b·d88888···························
 ·······Y888P··8888b···88888b···888Y88888P888·888·88888b·····d88b·······
 ········888······"88b·888·"88b·888·Y888P·888·888·888·"88b·d88P"88b·····
 ········888···d888888·888··888·888··Y8P··888·888·888··888·888··888·····
 ········888··888··888·888··888·888···"···888·888·888··888·Y88b·888·····
 ········888··"Y888888·888··888·888·······888·888·888··888··"Y88888·····
 ·······························································888·····
 ··························································Y8b·d88P·····
 ···························································"Y88P"······
 =======================================================================

 -----------------------------------------------------------------------
Author       : 焱铭
Date         : 2025-04-22 10:43:55 +0800
LastEditTime : 2025-04-29 17:41:43 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /EG-ASP/src/egasp/__main__.py
Description  : 
 -----------------------------------------------------------------------
'''

import argparse
from rich import box
from rich import print
from rich.table import Table
from rich.prompt import Prompt
from rich.console import Console
from rich_argparse import RichHelpFormatter

from egasp.validate import Validate
from egasp.egasp_core import EG_ASP_Core
from egasp.logger_config import setup_logger
from egasp.check_version import UpdateChecker
# 版本信息
from egasp.version import script_name, __version__

logger = setup_logger(False)


def get_egasp(query_temp: float, query_type: str = 'volume', query_value: float = 50) -> tuple:
    """
    根据输入的查询类型、浓度和温度, 计算乙二醇水溶液的相关属性。

    Parameters
    ----------
    query_type : str
        查询浓度的类型, 可选值为 "volume" 或 "mass", 分别表示体积浓度和质量浓度, 默认值为 "volume"。
    query_value : float
        查询的浓度值, 范围为 10% 到 90%, 单位为百分比 (%), 默认值为 50。
    query_temp : float
        查询的温度值, 范围为 -35°C 到 125°C。

    Returns
    -------
    tuple
        返回一个包含以下属性的元组：
        - mass: 质量浓度 (%)
        - volume: 体积浓度 (%)
        - freezing: 冰点 (°C)
        - boiling: 沸点 (°C)
        - rho: 密度 (kg/m³)
        - cp: 比热容 (J/kg·K)
        - k: 导热率 (W/m·K)
        - mu: 动力粘度 (Pa·s)
    """

    eg = EG_ASP_Core()  # 初始化核心计算类实例
    va = Validate()  # 初始化校验类实例

    # 校验查询类型, 确保其为合法值 ("volume" 或 "mass")
    query_type = va.type_value(query_type)

    # 校验查询浓度, 确保其在 10% 到 90% 的范围内
    query_value = va.input_value(query_value, min_val=10, max_val=90)

    # 校验查询温度, 确保其在 -35°C 到 125°C 的范围内
    query_temp = va.input_value(query_temp, min_val=-35, max_val=125)

    # 根据查询类型调用相应的函数, 获取冰点和沸点属性
    mass, volume, freezing, boiling = eg.get_fb_props(query_value, query_type=query_type)

    # 获取密度 (rho), 单位为 kg/m³
    rho = eg.get_props(temp=query_temp, conc=volume, egp_key='rho')

    # 获取比热容 (cp), 单位为 J/kg·K
    cp = eg.get_props(temp=query_temp, conc=volume, egp_key='cp')

    # 获取导热率 (k), 单位为 W/m·K
    k = eg.get_props(temp=query_temp, conc=volume, egp_key='k')

    # 获取动力粘度 (mu), 单位为 Pa·s, 并将结果从 mPa·s 转换为 Pa·s
    mu = eg.get_props(temp=query_temp, conc=volume, egp_key='mu') / 1000000

    return mass, volume, freezing, boiling, rho, cp, k, mu


def print_table(result: dict):
    console = Console(width=59)
    # 创建表格
    table = Table(show_header=True, header_style="bold dark_orange", box=box.ASCII_DOUBLE_HEAD, title="乙二醇水溶液查询结果")

    # 添加列
    table.add_column("属性", justify="left", style="cyan", no_wrap=True)
    table.add_column("单位", justify="left", style="magenta", no_wrap=True)
    table.add_column("数值", justify="left", style="green", no_wrap=True)
    table.add_column("属性", justify="left", style="cyan", no_wrap=True)
    table.add_column("单位", justify="left", style="magenta", no_wrap=True)
    table.add_column("数值", justify="left", style="green", no_wrap=True)

    # 添加行
    table.add_row("质量浓度", "%", f"{result['mass']:.2f}", "密度", "kg/m³", f"{result['rho']:.2f}")
    table.add_row("体积浓度", "%", f"{result['volume']:.2f}", "比热容", "J/kg·K", f"{result['cp']:.2f}")
    table.add_row("冰点", "°C", f"{result['freezing']:.2f}", "导热率", "W/m·K", f"{result['k']:.4f}")
    table.add_row("沸点", "°C", f"{result['boiling']:.2f}", "粘度", "Pa·s", f"{result['mu']:.8f}")

    # 打印表格
    console.print(table)


def cli_main():
    parser = argparse.ArgumentParser(
        prog='egasp',
        description="[i]乙二醇水溶液属性查询程序  ---- 焱铭[/]",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("-qt", "--query_type", type=str, default="volume", help="浓度类型 (volume/mass or v/m), 默认值为 volume (体积浓度)")
    parser.add_argument("-qv", "--query_value", type=float, default=50, help="查询浓度 %% (范围: 10 ~ 90), 默认值为 50")  # 修改此处
    parser.add_argument("query_temp", type=float, help="查询温度 °C (范围: -35 ~ 125)")  # 如果温度单位有%也需要转义

    args = parser.parse_args()

    console = Console(width=59)
    console.print(f"\n[bold green]{script_name}[/bold green]", justify="center")
    print('-----+-----------------------------------------------+-----')
    # 打印校验后的查询参数
    print(f"查询类型: {args.query_type}")
    print(f"查询浓度: {args.query_value} %")
    print(f"查询温度: {args.query_temp} °C")
    mass, volume, freezing, boiling, rho, cp, k, mu = get_egasp(args.query_temp, args.query_type, args.query_value)
    print('-----+-----------------------------------------------+-----\n')

    result = {"mass": mass, "volume": volume, "freezing": freezing, "boiling": boiling, "rho": rho, "cp": cp, "k": k, "mu": mu}

    print_table(result)  # 调用print_table函数

    # 检查更新
    uc = UpdateChecker(1, 6)  # 访问超时, 单位: 秒;缓存时长, 单位: 小时
    uc.check_for_updates()


def input_main():
    try:
        # 初始化控制台输出
        console = Console(width=59)
        console.print(f"\n[bold green]{script_name}[/bold green]", justify="center")
        print('-----+-----------------------------------------------+-----')

        # 交互式输入参数
        while True:
            try:
                console.print("[bold cyan]参数输入[/]")
                query_type = Prompt.ask("[bold]1. 浓度类型 [dim](volume/mass)[/]", default="volume")
                console.print(f"[green]✓ 已选择类型: {query_type}[/]")

                query_value = float(Prompt.ask("[bold]2. 输入浓度 [dim](10-90%)[/]", default="50"))
                console.print(f"[green]✓ 浓度已确认: {query_value}%[/]")

                query_temp = float(Prompt.ask("[bold]3. 输入温度 [dim](-35-125°C)[/]"))
                console.print(f"[green]✓ 温度已确认: {query_temp}°C[/]\n")
            except ValueError as e:
                console.print(f"[red]输入格式错误: {str(e)}，请重新输入[/red]")

            # 获取计算结果（复用原有核心逻辑）
            mass, volume, freezing, boiling, rho, cp, k, mu = get_egasp(query_temp, query_type, query_value)

            # 打印结果表格
            print('-----+-----------------------------------------------+-----\n')
            result = {"mass": mass, "volume": volume, "freezing": freezing, "boiling": boiling, "rho": rho, "cp": cp, "k": k, "mu": mu}
            print_table(result)

            # 检查更新（复用原有更新逻辑）
            uc = UpdateChecker(1, 6)
            uc.check_for_updates()

            console.input("[green]按任意键退出...[/]")

            break

    except Exception as e:
        logger.exception("程序发生异常:")
        console.input("[red]程序运行出错，按任意键退出...[/red]")


def main():
    STATE = 'input'  # 修改此处切换模式
    if STATE == 'cli':
        cli_main()
    elif STATE == 'input':
        input_main()


if __name__ == "__main__":
    main()
