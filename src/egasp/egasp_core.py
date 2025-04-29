import logging
import sys
import bisect
from typing import Tuple

from egasp.data.data import EGP


class EG_ASP_Core:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _interpolate_linear(x1: float, y1: float, x2: float, y2: float, x: float) -> float:
        """线性插值计算"""
        try:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        except ZeroDivisionError:
            raise RuntimeError(f"插值节点间距为零 x1={x1}, x2={x2}")

    def _error_exit(self, msg: str) -> None:
        """记录错误日志并退出程序"""
        self.logger.error(msg)
        sys.exit()

    def _find_nearest_nodes(self, nodes: list, value: float, name: str) -> Tuple[int, int]:
        """查找最近的节点索引"""
        try:
            idx = bisect.bisect_right(nodes, value) - 1
            lower_idx = max(idx, 0)
            upper_idx = min(bisect.bisect_left(nodes, value), len(nodes) - 1)

            if not (nodes[lower_idx] <= value <= nodes[upper_idx]):
                self._error_exit(f"{name} {value} 超出有效范围 [{nodes[0]}, {nodes[-1]}]")

            return lower_idx, upper_idx
        except IndexError as e:
            self._error_exit(f"节点索引错误: {str(e)}")

    def get_props(self, temp: float, conc: float, egp_key: str, temp_range: Tuple[int, int] = (-35, 125), conc_range: Tuple[float, float] = (10.0, 90.0), temp_step: int = 5, conc_step: float = 10.0) -> float:
        """根据温度和浓度获取物性参数"""
        if egp_key not in ['rho', 'cp', 'k', 'mu']:
            self._error_exit(f"无效物性参数 {egp_key}，可选值: rho/cp/k/mu")

        # 生成数据节点
        try:
            temp_nodes = list(range(temp_range[0], temp_range[1] + 1, temp_step))
            conc_nodes = [round(conc_range[0] + i * conc_step, 1) for i in range(int((conc_range[1] - conc_range[0]) / conc_step) + 1)]
        except ValueError as e:
            self._error_exit(f"参数范围错误: {str(e)}")

        # 查找节点索引
        t_lower_idx, t_upper_idx = self._find_nearest_nodes(temp_nodes, temp, "温度")
        c_lower_idx, c_upper_idx = self._find_nearest_nodes(conc_nodes, conc, "浓度")


        # 获取数据矩阵
        data_matrix = EGP.get(egp_key)

        # 提取四个角点数据
        v11 = data_matrix[t_lower_idx][c_lower_idx]
        v12 = data_matrix[t_lower_idx][c_upper_idx]
        v21 = data_matrix[t_upper_idx][c_lower_idx]
        v22 = data_matrix[t_upper_idx][c_upper_idx]

        # 检查数据有效性
        if any(v is None for v in [v11, v12, v21, v22]):
            self._error_exit(f"温度 {temp}°C 浓度 {conc}% 附近存在数据缺失 (数据库本身缺失)")

        # 执行插值计算
        t_lower, t_upper = temp_nodes[t_lower_idx], temp_nodes[t_upper_idx]
        c_lower, c_upper = conc_nodes[c_lower_idx], conc_nodes[c_upper_idx]

        if t_lower == t_upper and c_lower == c_upper:
            return v11
        if t_lower == t_upper:
            return self._interpolate_linear(c_lower, v11, c_upper, v12, conc)
        if c_lower == c_upper:
            return self._interpolate_linear(t_lower, v11, t_upper, v21, temp)

        v1 = self._interpolate_linear(c_lower, v11, c_upper, v12, conc)
        v2 = self._interpolate_linear(c_lower, v21, c_upper, v22, conc)

        return self._interpolate_linear(t_lower, v1, t_upper, v2, temp)


    def get_fb_props(self, query: float, query_type: str = 'volume') -> Tuple[float, float, float, float]:
        """根据浓度查询物性参数"""
        if query_type not in ['mass', 'volume']:
            self._error_exit(f"无效查询类型 {query_type}，必须为 'mass' 或 'volume'")

        data = EGP.get('fb')

        # 排序数据
        sort_key = 1 if query_type == 'volume' else 0
        sorted_data = sorted(data, key=lambda x: x[sort_key])
        sorted_values = [item[sort_key] for item in sorted_data]

        # 查找相邻数据点
        try:
            idx = bisect.bisect_left(sorted_values, query)
            if idx == 0 or idx == len(sorted_data):
                self._error_exit(f"浓度 {query}% 超出数据范围 [{sorted_values[0]}, {sorted_values[-1]}]")

            prev, curr = sorted_data[idx - 1], sorted_data[idx]
            p_val, c_val = prev[sort_key], curr[sort_key]

            if not (p_val <= query <= c_val):
                self._error_exit(f"浓度 {query}% 不在相邻数据点之间 [{p_val}, {c_val}]")
        except Exception as e:
            self._error_exit(f"数据查询失败: {str(e)}")

        # 解包数据
        m1, v1, f1, b1 = prev
        m2, v2, f2, b2 = curr

        # 检查数据完整性
        if any(v is None for v in [m1, v1, f1, b1, m2, v2, f2, b2]):
            self._error_exit(f"浓度 {query}% 附近存在数据缺失 (数据库本身缺失)")

        # 执行插值
        if query_type == 'volume':
            mass = self._interpolate_linear(v1, m1, v2, m2, query)
            volume = query
            freezing = self._interpolate_linear(v1, f1, v2, f2, query)
            boiling = self._interpolate_linear(v1, b1, v2, b2, query)
        else:
            volume = self._interpolate_linear(m1, v1, m2, v2, query)
            mass = query
            freezing = self._interpolate_linear(m1, f1, m2, f2, query)
            boiling = self._interpolate_linear(m1, b1, m2, b2, query)

        return (mass, volume, freezing, boiling)
