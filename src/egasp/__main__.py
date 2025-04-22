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
LastEditTime : 2025-04-22 16:58:23 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /EG-ASP/src/egasp/__main__.py
Description  : 
 -----------------------------------------------------------------------
'''

import argparse
from rich import box
from rich import print
from rich.table import Table
from rich.console import Console
from rich_argparse import RichHelpFormatter

from egasp.validate import Validate
from egasp.core import EG_ASP_Core
from egasp.logger_config import setup_logger
from egasp.check_version import UpdateChecker
# 版本信息
from egasp.version import script_name, __version__
logger = setup_logger(True)

def get_egasp(query_type, query_value, query_temp):
    eg = EG_ASP_Core()
    va = Validate()

    # 校验查询类型
    query_type = va.type_value(query_type)

    # 校验查询浓度
    query_value = va.input_value(query_value, min_val=10, max_val=90)

    # 校验查询温度
    query_temp = va.input_value(query_temp, min_val=-35, max_val=125)

    print(f"查询类型: {query_type}")
    print(f"查询浓度: {query_value} %")
    print(f"查询温度: {query_temp} °C")

    # 根据查询类型调用相应的函数
    mass, volume, freezing, boiling = eg.get_fb_props(query_value, query_type=query_type)
    rho = eg.get_props(temp=query_temp, conc=volume, egp_key='rho')
    cp  = eg.get_props(temp=query_temp, conc=volume, egp_key='cp')
    k   = eg.get_props(temp=query_temp, conc=volume, egp_key='k')
    mu  = eg.get_props(temp=query_temp, conc=volume, egp_key='mu')/1000000

    return mass, volume, freezing, boiling, rho, cp, k, mu

def main():
    parser = argparse.ArgumentParser(
        prog='egasp', 
        description="[i]乙二醇水溶液属性查询程序  ---- 焱铭[/]",
        formatter_class = RichHelpFormatter,
        )
    parser.add_argument("--query_type", type=str, default="volume", help="浓度类型 (volume/mass or v/m), 默认值为 volume (体积浓度)")
    parser.add_argument("--query_value", type=float, default=50, help="查询浓度 %% (范围: 10 ~ 90), 默认值为 50")  # 修改此处
    parser.add_argument("query_temp", type=float, help="查询温度 °C (范围: -35 ~ 125)")  # 如果温度单位有%也需要转义

    args = parser.parse_args()

    console = Console(width=34)
    console.print(f"\n[bold green]{script_name} v{__version__}[/bold green]", justify="center")
    print('----------------------------------')
    mass, volume, freezing, boiling, rho, cp, k, mu = get_egasp(args.query_type, args.query_value, args.query_temp)
    print('----------------------------------\n')

    # 创建表格
    table = Table(show_header=True, header_style="bold dark_orange", box=box.ASCII_DOUBLE_HEAD, title="乙二醇水溶液查询结果")

    # 添加列
    table.add_column("属性", justify="left", style="cyan"   , no_wrap=True)
    table.add_column("单位", justify="left", style="magenta", no_wrap=True)
    table.add_column("数值", justify="left", style="green"  , no_wrap=True)

    # 添加行
    table.add_row("质量浓度" , "%"      , f"{mass:.2f}")
    table.add_row("体积浓度" , "%"      , f"{volume:.2f}")
    table.add_row("冰点"    , "°C"      , f"{freezing:.2f}")
    table.add_row("沸点"    , "°C"      , f"{boiling:.2f}")
    table.add_row("密度"    , "kg/m³"  , f"{rho:.2f}")
    table.add_row("比热容"  , "J/kg·K" , f"{cp:.2f}")
    table.add_row("导热率"  , "W/m·K"  , f"{k:.4f}")
    table.add_row("粘度"    , "Pa·s"   , f"{mu:.8f}")

    # 打印表格
    console.print(table)

    # 检查更新
    uc = UpdateChecker(1, 6)  # 访问超时, 单位: 秒;缓存时长, 单位: 小时
    uc.check_for_updates()
if __name__ == "__main__":
    main()