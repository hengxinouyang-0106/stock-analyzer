# -*- coding: utf-8 -*-
"""修复后诊断脚本 v6：验证 EPS 修正后的 PE/PEG。"""
import traceback
import sys
sys.path.insert(0, '.')

print("=" * 70)
print("修复后接口诊断 v6（以 600519 为例）")
print("=" * 70)

CODE = "600519"

print("\n【1】fetch_all_data('600519') 关键字段:")
try:
    from data_fetcher import fetch_all_data
    d = fetch_all_data(CODE)
    if d is None:
        print("  返回 None")
    else:
        for k in ['pe_ttm', 'pb_ttm', 'dividend_yield', 'pe_series', 'pb_series',
                  'gross_margin', 'industry_name', 'revenue_growth', 'profit_growth',
                  'volume_ratio', 'volume_price', 'latest_price']:
            v = d.get(k)
            if isinstance(v, list):
                print(f"  {k}: [list, len={len(v)}]")
            else:
                print(f"  {k}: {v}")
        print(f"  pe_source_note: {d.get('pe_source_note')}")
        print(f"  pb_source_note: {d.get('pb_source_note')}")
except Exception as e:
    print(f"  失败: {e}")
    traceback.print_exc()

print("\n【2】analyzer.run_analysis() 结果:")
try:
    from data_fetcher import fetch_all_data
    from analyzer import run_analysis
    d = fetch_all_data(CODE)
    if d is None:
        print("  fetch_all_data 返回 None")
    else:
        r = run_analysis(d)
        print(f"  股票: {r['stock_name']} ({r['stock_code']})")
        print(f"  报告期: {r['report_date']}")
        print(f"  评级: {r['stars']}星 ({r['star_desc']})")
        print(f"  总雷数: {r['total_mines']} / {r['max_mines']}")
        print(f"\n  各指标详情:")
        for dim in r['dimensions']:
            print(f"\n  【{dim['name']}】")
            for ind in dim['indicators']:
                status = f"{ind['mines']}雷" if ind['mines'] is not None else "数据暂缺"
                print(f"    {ind['name']}: {ind.get('display', '—')} ({status})")
except Exception as e:
    print(f"  失败: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
