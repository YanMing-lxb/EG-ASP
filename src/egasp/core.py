import logging

from egasp.data import EGP



class EG_ASP_Core:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _interpolate_linear(self, x1: float, y1: float, x2: float, y2: float, x: float) -> float:
        """线性插值函数
        
        根据两点 (x1,y1) 和 (x2,y2) 计算x处的插值y
        
        Parameters
        ----------
        x1 : float
            第一个点的x坐标
        y1 : float
            第一个点的y坐标
        x2 : float
            第二个点的x坐标
        y2 : float
            第二个点的y坐标
        x : float
            插值点的x坐标

        Returns
        -------
        float
            插值结果y
        """
        return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


    def get_props(self, temp: float, conc: float, egp_key: str, 
                    temp_range: tuple = (-35, 125), conc_range: tuple = (10, 90),
                    temp_step: int = 5, conc_step: float = 10) -> float | None:
        """根据温度和浓度获取乙二醇水溶液的物性参数

        Parameters
        ----------
        temp : float
            温度, 单位摄氏度
        conc : float
            浓度, 质量分数 (10%~90%)
        egp_key : str
            物性关键词: rho cp k mu 分别对应密度、比热容、导热率和动力粘度
        temp_range : tuple, optional
            温度范围, 默认(-35, 125)
        conc_range : tuple, optional
            浓度范围, 默认(10, 90)
        temp_step : int, optional
            温度步长, 默认5
        conc_step : float, optional
            浓度步长, 默认10

        Returns
        -------
        float | None
            对应的物性参数值, 如果输入超出范围或数据中存在None, 返回None
        """
        # data_matrix: 二维列表, 行对应温度, 列对应浓度, 存储物性参数值
        data_matrix = EGP.get(egp_key)
        # 生成温度节点列表
        temp_nodes = list(range(temp_range[0], temp_range[1] + 1, temp_step))
        # 生成浓度节点列表, 避免浮点精度问题
        conc_nodes = [round(conc_range[0] + i * conc_step, 1) 
                    for i in range(int((conc_range[1] - conc_range[0]) / conc_step) + 1)]
        
        # 检查输入参数是否在有效范围内
        if (temp < temp_nodes[0] or temp > temp_nodes[-1] or
            conc < conc_nodes[0] or conc > conc_nodes[-1]):
            self.logger.error(f"查询温度 {temp} °C 浓度 {conc} % 在数据库范围之外")
        
        # 找到相邻温度节点
        t_lower = max(t for t in temp_nodes if t <= temp)
        t_upper = min(t for t in temp_nodes if t >= temp)
        
        # 找到相邻浓度节点
        c_lower = max(c for c in conc_nodes if c <= conc)
        c_upper = min(c for c in conc_nodes if c >= conc)
        
        # 获取索引位置
        t_lower_idx = temp_nodes.index(t_lower)
        t_upper_idx = temp_nodes.index(t_upper)
        c_lower_idx = conc_nodes.index(c_lower)
        c_upper_idx = conc_nodes.index(c_upper)
        
        # 提取四个角点的值
        v11 = data_matrix[t_lower_idx][c_lower_idx]
        v12 = data_matrix[t_lower_idx][c_upper_idx]
        v21 = data_matrix[t_upper_idx][c_lower_idx]
        v22 = data_matrix[t_upper_idx][c_upper_idx]
        
        # 检查数据有效性
        if any(v is None for v in [v11, v12, v21, v22]):
            self.logger.error(f"查询温度 {temp} °C 浓度 {conc} % 在数据库缺失数据范围之内, 请调整输入值。")
            exit()
        
        # 执行双线性插值
        if t_lower == t_upper and c_lower == c_upper:
            return v11
        elif t_lower == t_upper:
            return self._interpolate_linear(c_lower, v11, c_upper, v12, conc)
        elif c_lower == c_upper:
            return self._interpolate_linear(t_lower, v11, t_upper, v21, temp)
        else:
            v1 = self._interpolate_linear(c_lower, v11, c_upper, v12, conc)
            v2 = self._interpolate_linear(c_lower, v21, c_upper, v22, conc)
            return self._interpolate_linear(t_lower, v1, t_upper, v2, temp)


    def get_fb_props(self, query: float, query_type: str = 'volume') -> tuple[float, float, float, float] | None:
        """根据质量浓度或体积浓度查询乙二醇溶液的属性

        Parameters
        ----------
        query : float
            查询的浓度值
        query_type : str, optional
            查询类型, 'mass' 或 'volume', 默认为 'volume'

        Returns
        -------
        tuple[float, float, float, float] | None
            返回对应的质量浓度、体积浓度、冰点、沸点, 如果查询值超出范围返回None

        Raises
        ------
        ValueError
            当query_type不是'mass'或'volume'时抛出
        """

        # 每个元素为 (mass_conc, volume_conc, freezing, boiling)
        data = EGP.get('fb')

        # 根据查询类型排序数据
        sort_key = 1 if query_type == 'volume' else 0
        sorted_data = sorted(data, key=lambda x: x[sort_key])
        
        # 遍历寻找相邻数据点
        for i in range(len(sorted_data) - 1):
            current = sorted_data[i]
            next_item = sorted_data[i + 1]
            
            current_val = current[sort_key]
            next_val = next_item[sort_key]
            
            if current_val <= query <= next_val:
                # 解包数据点
                m1, v1, f1, b1 = current
                m2, v2, f2, b2 = next_item
                
                # 检查数据有效性
                if any(v is None for v in [m1, v1, f1, b1, m2, v2, f2, b2]):
                    self.logger.error(f"查询浓度 {query} % 在数据库缺失数据范围之内, 请调整输入值。")
                    exit()
                
                # 执行插值计算
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
        
        # 查询值超出数据范围
        self.logger.error(f"查询浓度 {query} % 超出数据")
        exit()