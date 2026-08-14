# -*- coding: utf-8 -*-
"""
数据拉取层 —— 仅使用 akshare 接口。

铁律：任一接口失败，对应字段置 None，绝不模拟。
"""
import datetime
import re

import pandas as pd

from cache import cache_result
from industry_mapping import get_industry

BOND_YIELD_REF = 2.8


# ------------------------------------------------------------------ 工具函数

def _safe_float(val):
    if val is None or pd.isna(val):
        return None
    try:
        s = str(val).replace(',', '').replace('%', '').replace('倍', '').strip()
        # 处理"亿"/"万"等单位
        unit = 1.0
        if '亿' in s:
            unit = 1e8
            s = s.replace('亿', '')
        elif '万' in s:
            unit = 1e4
            s = s.replace('万', '')
        f = float(s) * unit
        return None if f in (float('inf'), float('-inf')) else f
    except (TypeError, ValueError):
        return None


def _find_col(df, *keywords):
    """按关键字（不区分大小写、子串匹配）查找列名。"""
    if df is None or df.empty:
        return None
    for col in df.columns:
        col_norm = str(col).lower().replace(' ', '').replace('（', '(').replace('）', ')')
        for kw in keywords:
            kw_norm = kw.lower().replace(' ', '').replace('（', '(').replace('）', ')')
            if kw_norm in col_norm:
                return col
    return None


def _get_value(row, df, *keywords):
    col = _find_col(df, *keywords)
    if col is None or row is None:
        return None
    try:
        return _safe_float(row[col])
    except Exception:
        return None


def _parse_financial_df(df):
    """解析 stock_financial_analysis_indicator 返回的 DataFrame。"""
    if df is None or df.empty:
        return None, None, None

    df = df.copy()
    date_col = _find_col(df, '日期', '报告期', '报告日期')
    if date_col is None:
        return None, None, None

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    if len(df) < 1:
        return None, None, None

    df = df.sort_values(date_col, ascending=False).reset_index(drop=True)
    latest = df.iloc[0]
    latest_date = latest[date_col]

    prev = None
    for _, row in df.iloc[1:].iterrows():
        if (row[date_col].month == latest_date.month and
                row[date_col].day == latest_date.day):
            prev = row
            break

    if prev is None and len(df) > 1:
        prev = df.iloc[1]

    return latest, prev, df


# ------------------------------------------------------------------ 代码标准化

def normalize_code(query):
    """输入 600519 / 贵州茅台 → {"code": "600519", "name": "贵州茅台"}。"""
    import akshare as ak
    q = str(query).strip()
    if not q:
        return None

    m = re.search(r'(\d{6})', q)
    if m:
        code = m.group(1)
        name = None
        try:
            spot = ak.stock_zh_a_spot()
            sina_code = ('sh' if code.startswith('6') else 'sz') + code
            hit = spot[spot['代码'] == sina_code]
            if not hit.empty:
                name = str(hit.iloc[0].get('名称', ''))
        except Exception:
            pass
        return {'code': code, 'name': name or code}

    try:
        spot = ak.stock_zh_a_spot()
        hit = spot[spot['名称'] == q]
        if hit.empty:
            hit = spot[spot['名称'].str.contains(q, na=False)]
        if hit.empty:
            return None
        code = str(hit.iloc[0]['代码']).replace('sh', '').replace('sz', '')
        name = str(hit.iloc[0]['名称'])
        return {'code': code, 'name': name}
    except Exception:
        return None


# ------------------------------------------------------------------ 数据源

def _fetch_spot(code):
    import akshare as ak
    try:
        spot = ak.stock_zh_a_spot_em()
        row = spot[spot['代码'] == code]
        if row.empty:
            return None
        return row.iloc[0]
    except Exception:
        return None


def _fetch_financial(code):
    import akshare as ak
    try:
        start_year = str(datetime.date.today().year - 5)
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year=start_year)
        return _parse_financial_df(df)
    except Exception:
        return None, None, None


def _fetch_financial_ths(code):
    """备选：同花顺财务摘要。
    返回 DataFrame（列=指标名，行=报告期，按日期倒序）。"""
    import akshare as ak
    try:
        df = ak.stock_financial_abstract_ths(symbol=code)
        if df is None or df.empty:
            return None
        # 按报告期排序（最新在前）
        date_col = _find_col(df, '报告期', '日期')
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.sort_values(date_col, ascending=False).reset_index(drop=True)
        return df
    except Exception:
        return None


def _get_ths_value(ths_df, keyword):
    """从同花顺财务摘要中按列名关键字取最新值。
    注意：ths_df 的列是指标名，行是报告期（已按日期倒序）。
    """
    if ths_df is None or ths_df.empty:
        return None
    for col in ths_df.columns:
        if keyword in str(col):
            # 取最新报告期的值（第一行）
            return _safe_float(ths_df[col].iloc[0])
    return None


def _fetch_yjbb(report_date_str):
    """业绩报表（全市场），用于补充毛利率、行业、增速等字段。
    report_date_str: 如 '20260331'
    """
    import akshare as ak
    try:
        df = ak.stock_yjbb_em(date=report_date_str)
        if df is None or df.empty:
            return None
        return df
    except Exception:
        return None


def _fetch_spot_sina(code):
    """新浪财经实时行情（备选，可能绕过代理限制）。"""
    import akshare as ak
    try:
        df = ak.stock_zh_a_spot()
        if df is None or df.empty:
            return None
        # sina 代码格式: sh600519 / sz000001
        prefix = 'sh' if code.startswith('6') else 'sz'
        sina_code = f"{prefix}{code}"
        row = df[df['代码'] == sina_code]
        if row.empty:
            return None
        return row.iloc[0]
    except Exception:
        return None


# ------------------------------------------------------------------ 主函数

@cache_result(expire_seconds=3600)
def fetch_all_data(query):
    codes = normalize_code(query)
    if not codes:
        return None

    code = codes['code']
    name = codes['name']

    d = {
        'stock_code': code,
        'stock_name': name,
        'report_date': None,
        'industry_name': None,
        'industry': None,
    }

    # ==================== 1. 实时行情（spot_em，用户网络可能失败）====================
    spot_row = _fetch_spot(code)
    if spot_row is not None:
        d['industry_name'] = str(spot_row.get('所属行业', '')) if '所属行业' in spot_row else None
        d['latest_price'] = _safe_float(spot_row.get('最新价'))
        d['turnover'] = _safe_float(spot_row.get('换手率'))
        d['pe_dynamic'] = _safe_float(spot_row.get('市盈率-动态'))
        d['pb_spot'] = _safe_float(spot_row.get('市净率'))
        d['total_mv'] = _safe_float(spot_row.get('总市值'))

    # ==================== 2. 季报财务指标（主）====================
    latest, prev, fin_df = _fetch_financial(code)

    if latest is not None and fin_df is not None:
        date_col = _find_col(fin_df, '日期', '报告期', '报告日期')
        if date_col:
            d['report_date'] = str(latest[date_col])[:10]

        d['debt_ratio'] = _get_value(latest, fin_df, '资产负债率')
        d['gross_margin'] = _get_value(latest, fin_df, '销售毛利率', '毛利率')
        d['gross_margin_prev'] = _get_value(prev, fin_df, '销售毛利率', '毛利率') if prev is not None else None
        d['ar_turnover'] = _get_value(latest, fin_df, '应收账款周转率')
        d['ar_turnover_prev'] = _get_value(prev, fin_df, '应收账款周转率') if prev is not None else None
        d['inv_turnover'] = _get_value(latest, fin_df, '存货周转率')
        d['inv_turnover_prev'] = _get_value(prev, fin_df, '存货周转率') if prev is not None else None
        d['roe'] = _get_value(latest, fin_df, '净资产收益率')
        d['roe_prev'] = _get_value(prev, fin_df, '净资产收益率') if prev is not None else None
        d['ocf_per_share'] = _get_value(latest, fin_df, '每股经营性现金流', '每股经营现金流')
        d['revenue_growth'] = _get_value(latest, fin_df, '主营业务收入增长率', '营业收入增长率', '营收增长率')
        d['profit_growth'] = _get_value(latest, fin_df, '净利润增长率', '利润增长率')

    # ==================== 2b. 同花顺财务摘要（备选：填补毛利率等）====================
    if d.get('gross_margin') is None:
        ths_df = _fetch_financial_ths(code)
        if ths_df is not None:
            if d.get('gross_margin') is None:
                d['gross_margin'] = _get_ths_value(ths_df, '销售毛利率')
            if d.get('gross_margin_prev') is None and d.get('gross_margin') is not None:
                # 尝试取第二行（去年同期）
                for col in ths_df.columns:
                    if '销售毛利率' in str(col):
                        if len(ths_df) > 1:
                            d['gross_margin_prev'] = _safe_float(ths_df[col].iloc[1])
                        break

    # ==================== 2c. 业绩报表（备选：填补毛利率、行业、增速、EPS等）====================
    # 主接口可能缺失毛利率，用业绩报表兜底
    yjbb_eps = None
    if d.get('gross_margin') is None or d.get('industry_name') is None or d.get('pe_ttm') is None:
        report_date = d.get('report_date')
        if report_date:
            yjbb_date = report_date.replace('-', '')
            yjbb_df = _fetch_yjbb(yjbb_date)
            if yjbb_df is not None:
                row = yjbb_df[yjbb_df['股票代码'] == code]
                if not row.empty:
                    r = row.iloc[0]
                    if d.get('gross_margin') is None:
                        d['gross_margin'] = _safe_float(r.get('销售毛利率'))
                    if d.get('industry_name') is None:
                        d['industry_name'] = str(r.get('所处行业', ''))
                    if d.get('revenue_growth') is None:
                        d['revenue_growth'] = _safe_float(r.get('营业总收入-同比增长'))
                    if d.get('profit_growth') is None:
                        d['profit_growth'] = _safe_float(r.get('净利润-同比增长'))
                    if d.get('roe') is None:
                        d['roe'] = _safe_float(r.get('净资产收益率'))
                    if d.get('ocf_per_share') is None:
                        d['ocf_per_share'] = _safe_float(r.get('每股经营现金流量'))
                    # 保存 yjbb 的 EPS（更准确的单季度数据）
                    yjbb_eps = _safe_float(r.get('每股收益'))

    # ==================== 2d. 新浪财经实时行情（备选：最新价/PE/PB）====================
    sina_row = _fetch_spot_sina(code)
    if sina_row is not None:
        # 始终保存最新价（spot_em 失败时的兜底）
        if d.get('latest_price') is None:
            d['latest_price'] = _safe_float(sina_row.get('最新价'))
        if d.get('pe_ttm') is None:
            d['pe_ttm'] = _safe_float(sina_row.get('市盈率'))
        if d.get('pb_ttm') is None:
            d['pb_ttm'] = _safe_float(sina_row.get('市净率'))

    # ==================== 3. 自行估算 PE/PB（所有外部估值接口失败时的兜底）====================
    # PE = 最新价 / 每股收益(TTM近似)
    # PB = 最新价 / 每股净资产
    price_for_calc = d.get('latest_price')
    if price_for_calc is not None and price_for_calc > 0:
        # 优先用业绩报表的 EPS（更准确），其次用主接口财务数据
        if yjbb_eps is not None and yjbb_eps > 0:
            # yjbb 的 EPS 是单季度，粗略估算全年 = Q1 × 4
            eps = yjbb_eps * 4
            pe_note = '估算(最新价/业绩报表EPS×4)'
        elif latest is not None and fin_df is not None:
            eps = _get_value(latest, fin_df, '摊薄每股收益', '加权每股收益', '每股收益', '基本每股收益')
            pe_note = '估算(最新价/财报每股收益)'
        else:
            eps = None
            pe_note = None

        navps = None
        if latest is not None and fin_df is not None:
            navps = _get_value(latest, fin_df, '每股净资产', '每股净资产_调整前', '每股净资产_调整后')

        if d.get('pe_ttm') is None and eps is not None and eps > 0:
            d['pe_ttm'] = price_for_calc / eps
            d['pe_source_note'] = pe_note
        if d.get('pb_ttm') is None and navps is not None and navps > 0:
            d['pb_ttm'] = price_for_calc / navps
            d['pb_source_note'] = '估算(最新价/每股净资产)'

    # ==================== 4. 行业基准 ====================
    d['industry'] = get_industry(d.get('industry_name') or code)
    d['bond_yield'] = BOND_YIELD_REF

    return d
