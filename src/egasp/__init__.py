'''
一款用于获取乙二醇水溶液物性参数的工具
可用函数 get_egasp()
'''

import sys
from .egasp_core import EG_ASP_Core

# 实例化核心类
eg = EG_ASP_Core()

# 将 get_egasp 方法暴露为模块级别的函数
get_egasp = eg.get_egasp  # 修改点：直接暴露 get_egasp 函数

if sys.version_info[0] == 3:
    from .__main__ import main  # 显式导出 main() 供 CLI 入口使用
else:
    # Don't import anything.
    pass