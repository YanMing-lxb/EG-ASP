<!--
 *  =======================================================================
 *  ····Y88b···d88P················888b·····d888·d8b·······················
 *  ·····Y88b·d88P·················8888b···d8888·Y8P·······················
 *  ······Y88o88P··················88888b·d88888···························
 *  ·······Y888P··8888b···88888b···888Y88888P888·888·88888b·····d88b·······
 *  ········888······"88b·888·"88b·888·Y888P·888·888·888·"88b·d88P"88b·····
 *  ········888···d888888·888··888·888··Y8P··888·888·888··888·888··888·····
 *  ········888··888··888·888··888·888···"···888·888·888··888·Y88b·888·····
 *  ········888··"Y888888·888··888·888·······888·888·888··888··"Y88888·····
 *  ·······························································888·····
 *  ··························································Y8b·d88P·····
 *  ···························································"Y88P"······
 *  =======================================================================
 * 
 *  -----------------------------------------------------------------------
 * Author       : 焱铭
 * Date         : 2025-04-22 10:43:55 +0800
 * LastEditTime : 2025-05-06 14:41:13 +0800
 * Github       : https://github.com/YanMing-lxb/
 * FilePath     : /egasp/README.md
 * Description  : 
 *  -----------------------------------------------------------------------
 -->

# 乙二醇水溶液物性参数查询程序 | egasp (Ethylene Glycol Aqueous Solution Properties)

[![GitHub](https://img.shields.io/badge/Github-EGASP-000000.svg)](https://github.com/YanMing-lxb/egasp) [![License](https://img.shields.io/badge/license-GPLv3-aff)](https://www.latex-project.org/lppl/) ![OS](https://img.shields.io/badge/OS-Linux%2C%20Win%2C%20Mac-pink.svg) [![GitHub release](https://img.shields.io/github/release/YanMing-lxb/egasp.svg?color=blueviolet&label=version&style=popout)](https://github.com/YanMing-lxb/egasp/releases/latest) [![Last Commit](https://img.shields.io/github/last-commit/YanMing-lxb/egasp)](https://github.com/YanMing-lxb/egasp/zipball/master) [![Issues](https://img.shields.io/github/issues/YanMing-lxb/egasp)](https://github.com/YanMing-lxb/egasp/issues) [![PyPI version](https://img.shields.io/pypi/v/egasp.svg)](https://pypi.python.org/pypi/egasp/) [![PyPI Downloads](https://img.shields.io/pypi/dm/egasp.svg?label=PyPI%20downloads)](https://pypi.org/project/egasp/) ![GitHub repo size](https://img.shields.io/github/repo-size/YanMing-lxb/egasp)

## 安装

官方版本 egasp 发布在 [PyPI](https://pypi.org/project/egasp/) 上，并且可以通过 pip 包管理器从 PyPI 镜像轻松安装。

请注意，您必须使用 Python 3 版本 pip：

```
pip3 install egasp
```

## 升级

```
pip3 install --upgrade egasp
```

## EXCEL 加载项使用说明

### 设置 Excel 插件

如需在 Excel 中使用 `egasp.exe` 提供的功能，请按照以下步骤进行设置：

1. **文件路径**  
   确保 `EgaspAddin.xlam` 文件与 `egasp.exe` 文件位于相同的文件夹路径下。

2. **加载插件**  
   在 Excel 中依次点击：  
   `文件` → `选项` → `加载项` → 在底部选择 `转到...` → 点击 `浏览` → 选择 `EgaspAddin.xlam` 文件 → 确定加载。
3. **使用示例**
   见 `EgaspAddin.xlsx` 文件

### 错误提示说明

- `#NO_OUTPUT`：表明输入存在错误或者输入范围超出了数据库支持的范围，请检查并重新调整输入

## 未来计划

- [X] 打包成独立可执行程序
- [X] 支持 excel 调用
- [ ] 改进EXCEL加载项的计算速度

## 来源

https://www.glycolsales.com.au/dowtherm/dowtherm-sr-1/
