'''
一款用于获取乙二醇水溶液物性参数的工具
可用函数 get_egasp()
'''

import sys
from .__main__ import get_egasp

if sys.version_info[0] == 3:
    from .__main__ import main  # 显式导出 main() 供 CLI 入口使用
else:
    # Don't import anything.
    pass 