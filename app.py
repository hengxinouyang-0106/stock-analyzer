# -*- coding: utf-8 -*-
"""Flask 主程序。"""
from flask import Flask, render_template, request, jsonify

from data_fetcher import fetch_all_data
from analyzer import run_analysis

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json(force=True) or {}
        query = str(data.get('query', '')).strip()
        if not query:
            return jsonify({"code": 400, "msg": "请输入股票代码或名称"})

        raw = fetch_all_data(query)
        if raw is None:
            return jsonify({"code": 404, "msg": "未找到该股票"})

        result = run_analysis(raw)
        return jsonify({"code": 200, "data": result})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器异常: {str(e)}"})


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
