# -*- coding: utf-8 -*-
"""行业基准数据（仅用于对比参照，绝不用于个股数据填补）。"""

INDUSTRY_MAP = {
    "白酒": {"avg_growth": 12.0, "avg_gross_margin": 70.0},
    "银行": {"avg_growth": 5.0, "avg_gross_margin": 35.0},
    "保险": {"avg_growth": 6.0, "avg_gross_margin": 20.0},
    "证券": {"avg_growth": 8.0, "avg_gross_margin": 40.0},
    "房地产": {"avg_growth": -5.0, "avg_gross_margin": 20.0},
    "电力": {"avg_growth": 6.0, "avg_gross_margin": 22.0},
    "煤炭": {"avg_growth": 8.0, "avg_gross_margin": 35.0},
    "钢铁": {"avg_growth": 3.0, "avg_gross_margin": 10.0},
    "化工": {"avg_growth": 7.0, "avg_gross_margin": 18.0},
    "医药": {"avg_growth": 10.0, "avg_gross_margin": 50.0},
    "医疗器械": {"avg_growth": 12.0, "avg_gross_margin": 55.0},
    "半导体": {"avg_growth": 15.0, "avg_gross_margin": 40.0},
    "电子": {"avg_growth": 10.0, "avg_gross_margin": 20.0},
    "软件": {"avg_growth": 12.0, "avg_gross_margin": 45.0},
    "互联网": {"avg_growth": 15.0, "avg_gross_margin": 40.0},
    "新能源": {"avg_growth": 20.0, "avg_gross_margin": 22.0},
    "汽车": {"avg_growth": 8.0, "avg_gross_margin": 16.0},
    "家电": {"avg_growth": 6.0, "avg_gross_margin": 25.0},
    "食品饮料": {"avg_growth": 8.0, "avg_gross_margin": 35.0},
    "零售": {"avg_growth": 5.0, "avg_gross_margin": 18.0},
    "物流": {"avg_growth": 7.0, "avg_gross_margin": 12.0},
    "航空": {"avg_growth": 10.0, "avg_gross_margin": 15.0},
    "通信": {"avg_growth": 6.0, "avg_gross_margin": 28.0},
    "传媒": {"avg_growth": 5.0, "avg_gross_margin": 30.0},
    "建筑": {"avg_growth": 5.0, "avg_gross_margin": 12.0},
    "建材": {"avg_growth": 3.0, "avg_gross_margin": 20.0},
    "农业": {"avg_growth": 5.0, "avg_gross_margin": 15.0},
    "纺织": {"avg_growth": 3.0, "avg_gross_margin": 18.0},
    "有色金属": {"avg_growth": 8.0, "avg_gross_margin": 12.0},
    "石油": {"avg_growth": 5.0, "avg_gross_margin": 20.0},
}

DEFAULT_INDUSTRY = {"avg_growth": 6.0, "avg_gross_margin": 20.0}


def get_industry(name_or_code):
    """根据行业名称或代码前缀获取行业基准。"""
    if not name_or_code:
        return DEFAULT_INDUSTRY
    name = str(name_or_code).strip()
    # 先精确匹配
    if name in INDUSTRY_MAP:
        return INDUSTRY_MAP[name]
    # 再模糊匹配
    for key, val in INDUSTRY_MAP.items():
        if key in name or name in key:
            return val
    # 代码前缀兜底
    code = name.zfill(6) if name.isdigit() else name
    if code.startswith("300"):
        return INDUSTRY_MAP.get("半导体", DEFAULT_INDUSTRY)
    if code.startswith(("000", "001", "002")):
        return INDUSTRY_MAP.get("电子", DEFAULT_INDUSTRY)
    if code.startswith(("600", "601", "603", "605", "688")):
        return INDUSTRY_MAP.get("化工", DEFAULT_INDUSTRY)
    return DEFAULT_INDUSTRY
