# app.py — Flask 入口与路由(成员A 李嘉星)
# 骨架阶段:所有路由已接通,业务函数指向 record.py / report.py / storage.py
# 联调时只需对齐各模块的函数名,路由层不再改动

from flask import Flask, jsonify, render_template, request, send_file
import storage
import record
import report

app = Flask(__name__)


# ---------- 页面路由 ----------

@app.route("/")
def index():
    # 主页:记账表单 + 最近记录(谢玲洁负责,占位页待其替换)
    return render_template("index.html")


@app.route("/stats")
def stats_page():
    # 统计页:图表 + 明细表(王清源负责,占位页待其替换)
    return render_template("stats.html")


# ---------- REST API ----------

@app.route("/api/records", methods=["GET"])
def api_list():
    # 最近N笔,默认10条:?limit=20
    limit = request.args.get("limit", 10, type=int)
    return jsonify(report.recent_records(limit))


@app.route("/api/records", methods=["POST"])
def api_add():
    # 新增一笔记账,body 为 JSON:
    # {"date":"2026-11-07","type":"expense","amount":25.5,"category":"饮食","note":"午饭"}
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"ok": False, "msg": "请求体必须是JSON"})
    ok, msg = record.add_record(data)
    return jsonify({"ok": ok, "msg": msg})


@app.route("/api/records/<int:rid>", methods=["DELETE"])
def api_delete(rid):
    ok, msg = record.delete_record(rid)
    return jsonify({"ok": ok, "msg": msg})


@app.route("/api/stats")
def api_stats():
    # 统计:?start=&end=&category=&min_amount=&max_amount=&type=&group=category|date
    return jsonify(report.stats(request.args))


@app.route("/api/summary")
def api_summary():
    # 首页顶部小结卡片:本月总支出/总收入/结余
    return jsonify(report.summary())


@app.route("/api/categories")
def api_categories():
    # 类别清单,前端下拉框从这里取,保证和后端校验永远一致
    return jsonify(storage.CATEGORIES)


@app.route("/api/export/csv")
def api_export_csv():
    # 一键导出CSV(亮点③):utf-8-sig 编码,Excel 打开不乱码
    path = storage.export_csv()
    return send_file(path, as_attachment=True, download_name="records.csv")


@app.route("/api/budget", methods=["GET"])
def api_budget():
    # 月度预算进度(亮点④):预算/本月已花/百分比,前端画进度条
    spent = report.summary()["expense"]
    budget = storage.load_budget()
    percent = round(spent / budget * 100, 1) if budget > 0 else 0
    return jsonify({"budget": budget, "spent": spent, "percent": percent})


@app.route("/api/budget", methods=["POST"])
def api_set_budget():
    # 设置本月预算,非法值直接拒绝并给原因
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "msg": "预算必须是数字"})
    if amount <= 0:
        return jsonify({"ok": False, "msg": "预算必须大于0"})
    storage.save_budget(amount)
    return jsonify({"ok": True, "msg": "预算已设置为 ¥%.2f" % amount})


@app.route("/api/trend")
def api_trend():
    # 月度环比(亮点):本月支出 vs 上月,前端画 📈/📉
    return jsonify(report.trend())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
