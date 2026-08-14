# -*- coding: utf-8 -*-
"""
15 项排雷指标计算。

每项函数签名：calc_xxx(value, **ctx) -> (mines: int|None, explain: str)
value 为 None 时返回 (None, "数据暂缺，不计雷")
"""

MISSING = (None, "数据暂缺，不计雷。")


# ================================================================ 经营质量

def calc_debt_ratio(value, **ctx):
    """资产负债率（%）。"""
    if value is None:
        return MISSING
    if value < 40:
        return 0, "负债率极低，财务结构稳健。"
    if value < 55:
        return 1, "负债率适中。"
    if value < 65:
        return 2, "负债率偏高，关注偿债压力。"
    if value < 75:
        return 3, "负债率高企，财务风险上升。"
    if value < 85:
        return 4, "负债率危险区间，偿债能力堪忧。"
    return 5, "资不抵债边缘，极高债务风险。"


def calc_gross_margin_change(value, **ctx):
    """毛利率同比变化（pp）。"""
    if value is None:
        return MISSING
    if value >= 0:
        return 0, "毛利率提升，产品竞争力增强。"
    drop = -value
    if drop < 5:
        return 1, "毛利率小幅下滑，暂属正常波动。"
    if drop < 10:
        return 2, "毛利率明显下滑，盈利空间被压缩。"
    if drop < 20:
        return 3, "毛利率大幅下滑，警惕价格战或成本失控。"
    return 5, "毛利率断崖式下跌，商业模式经受严峻考验。"


def calc_ar_turnover(value, **ctx):
    """应收账款周转同比变化率（%）。"""
    if value is None:
        return MISSING
    if value >= 0:
        return 0, "应收账款周转加快，回款效率提升。"
    if value > -10:
        return 1, "周转率小幅下降，需关注回款节奏。"
    if value > -30:
        return 3, "周转率明显下降，回款压力加大，警惕坏账。"
    return 5, "周转率大幅恶化，资金占用严重，坏账风险陡增。"


def calc_inv_turnover(value, **ctx):
    """存货周转同比变化率（%）。"""
    if value is None:
        return MISSING
    if value >= 0:
        return 0, "存货周转加快，库存管理效率提升。"
    if value > -10:
        return 1, "周转率小幅下降，库存略有积压。"
    if value > -30:
        return 3, "周转率明显下降，产品滞销风险上升。"
    return 5, "周转率大幅恶化，存货严重积压，可能面临大额跌价计提。"


def calc_roe_change(value, **ctx):
    """ROE 同比变化（pp）。"""
    if value is None:
        return MISSING
    if value >= 0:
        return 0, "ROE 提升，股东回报能力增强。"
    drop = -value
    if drop < 5:
        return 1, "ROE 小幅下滑，盈利能力略有波动。"
    if drop < 15:
        return 2, "ROE 明显下滑，盈利质量需要关注。"
    # 当前 ROE 仍为正，但降幅较大
    current_roe = ctx.get('current_roe')
    if current_roe is not None and current_roe > 0:
        return 4, "ROE 大幅跳水但仍为正，盈利根基动摇。"
    return 5, "ROE 为负，公司陷入亏损，股东回报为负。"


def calc_ocf_per_share(value, **ctx):
    """每股经营现金流（元）。"""
    if value is None:
        return MISSING
    if value > 0.5:
        return 0, "经营现金流充沛，真金白银回报股东。"
    if value >= 0:
        return 1, "经营现金流尚可，但略显单薄。"
    if value >= -0.5:
        return 3, "经营现金流为负，利润含金量不足。"
    return 5, "经营现金流严重失血，公司可能靠融资续命。"


# ================================================================ 行业竞争

def calc_revenue_gap(value, revenue_growth=None, **ctx):
    """营收增速 vs 行业（pp）。"""
    if value is None:
        return MISSING
    # 连续两年负增长检测
    two_years_negative = False
    if revenue_growth is not None and revenue_growth < 0:
        prev_growth = ctx.get('prev_revenue_growth')
        if prev_growth is not None and prev_growth < 0:
            two_years_negative = True

    if two_years_negative:
        return 5, "营收连续两年负增长，行业地位严重恶化。"
    if value >= 5:
        return 0, "营收增速显著跑赢行业，竞争力强劲。"
    if value >= -2:
        return 1, "营收增速与行业基本持平。"
    if value >= -15:
        return 2, "营收增速落后行业，市场份额或被蚕食。"
    if value >= -30:
        return 3, "营收增速大幅落后行业，竞争地位明显恶化。"
    if revenue_growth is not None and revenue_growth < 0:
        return 4, "营收深度负增长且远逊行业，警惕行业性衰退。"
    return 3, "营收增速远逊行业均值。"


def calc_profit_gap(value, profit_growth=None, revenue_growth=None, **ctx):
    """盈利增速 vs 营收增速（pp）。"""
    if value is None:
        return MISSING
    if value > 0:
        return 0, "盈利增速快于营收，经营效率提升。"
    if value >= -10:
        return 1, "盈利与营收基本同步，效率稳定。"
    if value >= -30:
        return 2, "盈利增速明显滞后于营收，费用或成本失控。"
    if profit_growth is not None and profit_growth < 0 and revenue_growth is not None and revenue_growth > 0:
        return 5, "营收增长但利润下滑，典型的增收不增利，经营质量恶化。"
    if profit_growth is not None and profit_growth < 0:
        return 4, "盈利负增长且远逊营收，盈利能力堪忧。"
    return 3, "盈利增速显著落后于营收。"


def calc_gross_margin_gap(value, **ctx):
    """毛利率 vs 行业（pp）。"""
    if value is None:
        return MISSING
    if value >= 0:
        return 0, "毛利率高于行业均值，产品护城河稳固。"
    if value > -5:
        return 1, "毛利率与行业接近，竞争力正常。"
    if value > -15:
        return 3, "毛利率低于行业，定价权或成本控制能力偏弱。"
    return 5, "毛利率远低于行业，竞争劣势明显，生存空间受挤压。"


# ================================================================ 估值安全

def calc_pe_value(value, **ctx):
    """当前 PE-TTM（绝对值评估）。"""
    if value is None:
        return MISSING
    if value < 0:
        return 5, "PE 为负，公司亏损，估值失去基本面支撑。"
    if value < 10:
        return 0, "PE 低于 10 倍，估值极低，安全边际充足。"
    if value < 15:
        return 1, "PE 处于 10-15 倍，估值偏低。"
    if value < 25:
        return 2, "PE 处于 15-25 倍，估值适中合理。"
    if value < 40:
        return 3, "PE 处于 25-40 倍，估值偏高，需高成长支撑。"
    if value < 60:
        return 4, "PE 处于 40-60 倍，估值明显偏贵，透支未来预期。"
    return 5, "PE 超过 60 倍，估值泡沫化风险极高，基本面难以支撑。"


def calc_peg(value, profit_growth=None, **ctx):
    """PEG = PE / 净利润增长率。"""
    if value is None:
        return MISSING
    if profit_growth is not None and profit_growth <= 0:
        return 5, "净利润零增长或负增长，PEG 失效，估值失去基本面支撑。"
    if value < 0.5:
        return 0, "PEG 远低于 1，成长股被低估。"
    if value < 1:
        return 1, "PEG 小于 1，估值与成长匹配良好。"
    if value < 1.5:
        return 2, "PEG 略高，估值合理偏贵。"
    if value < 2.5:
        return 3, "PEG 偏高，成长溢价明显。"
    if value < 4:
        return 4, "PEG 高企，增长难以支撑当前估值。"
    return 5, "PEG 极端，估值严重脱离基本面。"


def calc_pb_value(value, **ctx):
    """当前 PB（绝对值评估）。"""
    if value is None:
        return MISSING
    if value < 0:
        return 5, "PB 为负，净资产为负，资不抵债风险。"
    if value < 1:
        return 0, "PB 低于 1，破净状态，资产安全边际高。"
    if value < 1.5:
        return 1, "PB 处于 1-1.5 倍，估值偏低。"
    if value < 2.5:
        return 2, "PB 处于 1.5-2.5 倍，估值适中合理。"
    if value < 4:
        return 3, "PB 处于 2.5-4 倍，估值偏高，资产溢价明显。"
    if value < 6:
        return 4, "PB 处于 4-6 倍，资产溢价过高，警惕泡沫。"
    return 5, "PB 超过 6 倍，资产泡沫化风险极高。"


# ================================================================ 综合评级

def calc_star_rating(mines_list):
    valid = [m for m in mines_list if m is not None]
    if not valid:
        return 0, "无数据", 0
    total = sum(valid)
    max_mines = len(valid) * 5
    ratio = total / max_mines if max_mines else 0
    if ratio <= 0.20:
        return 1, "低风险", max_mines
    if ratio <= 0.40:
        return 2, "中低风险", max_mines
    if ratio <= 0.60:
        return 3, "中等风险", max_mines
    if ratio <= 0.80:
        return 4, "高风险", max_mines
    return 5, "极高风险", max_mines


# ================================================================ 格式化

def _fmt(value, unit):
    if value is None:
        return None
    try:
        if unit == 'pct':
            return f"{value:.2f}%"
        if unit == 'pp':
            return f"{value:+.2f} pp"
        if unit == 'num':
            return f"{value:.2f}"
        if unit == 'x':
            return f"{value:.2f} 倍"
        if unit == 'currency':
            return f"{value:.2f} 元"
        if unit == 'text':
            return str(value)
        return str(value)
    except Exception:
        return None


# ================================================================ 编排

def run_analysis(d):
    """输入 fetch_all_data 的结果字典，输出前端报告 JSON 结构。"""

    # ---- 预计算派生指标 ----
    gross_margin = d.get('gross_margin')
    gross_margin_prev = d.get('gross_margin_prev')
    gross_margin_change = (gross_margin - gross_margin_prev
                           if gross_margin is not None and gross_margin_prev is not None else None)

    ar = d.get('ar_turnover')
    ar_prev = d.get('ar_turnover_prev')
    ar_change = ((ar - ar_prev) / abs(ar_prev) * 100
                 if ar is not None and ar_prev is not None and ar_prev != 0 else None)

    inv = d.get('inv_turnover')
    inv_prev = d.get('inv_turnover_prev')
    inv_change = ((inv - inv_prev) / abs(inv_prev) * 100
                  if inv is not None and inv_prev is not None and inv_prev != 0 else None)

    roe = d.get('roe')
    roe_prev = d.get('roe_prev')
    roe_change = (roe - roe_prev if roe is not None and roe_prev is not None else None)

    revenue_growth = d.get('revenue_growth')
    profit_growth = d.get('profit_growth')
    industry = d.get('industry', {})
    industry_growth = industry.get('avg_growth')
    industry_gross_margin = industry.get('avg_gross_margin')

    revenue_gap = (revenue_growth - industry_growth
                   if revenue_growth is not None and industry_growth is not None else None)
    profit_gap = (profit_growth - revenue_growth
                  if profit_growth is not None and revenue_growth is not None else None)
    gross_margin_gap = (gross_margin - industry_gross_margin
                        if gross_margin is not None and industry_gross_margin is not None else None)

    pe_ttm = d.get('pe_ttm')
    pb_ttm = d.get('pb_ttm')

    peg = (pe_ttm / profit_growth
           if pe_ttm is not None and profit_growth is not None and profit_growth > 0 else None)

    # ---- 构建指标 ----
    def item(name, value, unit, func, source, **ctx):
        mines, explain = func(value, **ctx)
        return {
            "name": name,
            "value": value,
            "display": _fmt(value, unit),
            "mines": mines,
            "source": source if mines is not None else "数据暂缺",
            "explain": explain,
        }

    dimensions = [
        {
            "name": "公司经营质量",
            "indicators": [
                item("资产负债率", d.get('debt_ratio'), 'pct', calc_debt_ratio, '财报'),
                item("毛利率同比变化", gross_margin_change, 'pp', calc_gross_margin_change, '财报'),
                item("应收周转同比", ar_change, 'pct', calc_ar_turnover, '财报'),
                item("存货周转同比", inv_change, 'pct', calc_inv_turnover, '财报'),
                item("ROE 同比变化", roe_change, 'pp', calc_roe_change, '财报', current_roe=roe),
                item("每股经营现金流", d.get('ocf_per_share'), 'currency', calc_ocf_per_share, '财报'),
            ],
        },
        {
            "name": "行业竞争环境",
            "indicators": [
                item("营收增速 vs 行业", revenue_gap, 'pp', calc_revenue_gap, '财报+行业基准',
                     revenue_growth=revenue_growth,
                     prev_revenue_growth=d.get('revenue_growth_prev')),
                item("盈利增速 vs 营收增速", profit_gap, 'pp', calc_profit_gap, '财报',
                     profit_growth=profit_growth, revenue_growth=revenue_growth),
                item("毛利率 vs 行业", gross_margin_gap, 'pp', calc_gross_margin_gap, '财报+行业基准'),
            ],
        },
        {
            "name": "估值安全边际",
            "indicators": [
                item("当前 PE-TTM", pe_ttm, 'x', calc_pe_value, '财报'),
                item("PEG", peg, 'num', calc_peg, '财报', profit_growth=profit_growth),
                item("当前 PB", pb_ttm, 'x', calc_pb_value, '财报'),
            ],
        },
    ]

    mines_list = [ind["mines"] for dim in dimensions for ind in dim["indicators"]]
    stars, star_desc, max_mines = calc_star_rating(mines_list)
    total_mines = sum(m for m in mines_list if m is not None)

    return {
        "stock_name": d.get("stock_name"),
        "stock_code": d.get("stock_code"),
        "report_date": d.get("report_date") or "未知",
        "total_mines": total_mines,
        "max_mines": max_mines,
        "stars": stars,
        "star_desc": star_desc,
        "dimensions": dimensions,
    }
