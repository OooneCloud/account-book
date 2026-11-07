# 查看与统计模块

`report.py` 只读取 `storage.load_records()`，不会写入或更改记录，无新增依赖。
目前主分支还没有 storage.py 和 app.py；测试使用隔离的模拟存储，不向正式代码注入演示账目。

## 数据约定

每条记录包含：`id`（整数或数字字符串）、`date`（YYYY-MM-DD）、
`type`（expense/income）、`category`（字符串）、`amount`（非负有限数值）。
storage 负责保证记录格式。存储读取异常会向上传递，避免把读取失败误报成空账本。

## 函数

- `recent_records(limit=10)`：日期倒序，同日按数字 id 倒序。支持 URL 中的非负整数字符串；0 返回空列表，非法 limit 抛出 ValueError。
- `stats(args)`：支持 start/end、category、min_amount/max_amount、type=all/expense/income、group=category/date，范围两端均包含。空参数不限制，默认全部类型、按类别。返回 total/count/items，每项包含 key/total/count。类别按总额降序、同额按类别名排序；日期按升序，便于画趋势图。all 的 total 为收支金额之和，结余使用 summary。
- `summary()`：返回 month、income、expense、balance，按服务器本地日历月统计；balance=income-expense。部署时请将服务器时区设置为业务时区。

金额使用 Decimal 累加，输出四舍五入至两位小数的 JSON 数字。
非法日期、类型、分组、负数/非有限金额及颠倒区间会抛出 ValueError。

## A 成员接入 Flask

将以下代码接入已有 app.py（不要重复创建 Flask app）：

```python
from flask import jsonify, request
import report

@app.get('/api/recent')
def api_recent():
    try:
        return jsonify(report.recent_records(request.args.get('limit', '10')))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

@app.get('/api/stats')
def api_stats():
    try:
        return jsonify(report.stats(request.args))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

@app.get('/api/summary')
def api_summary():
    return jsonify(report.summary())
```

## 自测

在仓库根目录执行：`python -m unittest discover -s tests -v`。
测试覆盖排序、全部筛选、金额精度、空记录、非法参数及跨年月份边界。

接入 app.py 和 storage.py 后再执行以下端到端检查：

```bash
curl "http://127.0.0.1:5000/api/recent?limit=10"
curl "http://127.0.0.1:5000/api/stats?group=category&type=expense&start=2026-11-01"
curl "http://127.0.0.1:5000/api/stats?group=date&type=all&min_amount=0&max_amount=100"
curl "http://127.0.0.1:5000/api/summary"
```

目前缺少 app.py/storage.py，以上 HTTP 检查尚未执行。
