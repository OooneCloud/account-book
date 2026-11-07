# report.py — 查看+统计模块(成员D 李莹莹)
# 负责「查看最近的几笔记录」和「收支统计」两个需求
# F 的图表数据全部由本模块提供,格式见 stats() 的返回值

import datetime
import storage
from collections import defaultdict


def recent_records(limit=10):
    # 最近N笔:按日期倒序、同日期再按id倒序,保证最新记录排最前
    records = sorted(storage.load_records(),
                     key=lambda r: (r["date"], r["id"]), reverse=True)
    return records[:limit]


def _filter(records, args):
    # 按条件过滤:日期范围 / 类别 / 类型 / 金额区间(任务书要求四个维度都支持)
    start = args.get("start", "")
    end = args.get("end", "")
    category = args.get("category", "")
    t = args.get("type", "all")

    rows = [r for r in records
            if (t == "all" or r["type"] == t)
            and (not start or r["date"] >= start)
            and (not end or r["date"] <= end)
            and (not category or r["category"] == category)]

    # 金额区间:参数不传就不过滤;传了非数字则忽略该条件
    try:
        min_amount = float(args.get("min_amount", ""))
        rows = [r for r in rows if r["amount"] >= min_amount]
    except ValueError:
        pass
    try:
        max_amount = float(args.get("max_amount", ""))
        rows = [r for r in rows if r["amount"] <= max_amount]
    except ValueError:
        pass
    return rows


def stats(args):
    # 统计:先过滤,再按 group 维度聚合(category=按类别 / date=按日期)
    # 返回格式(前后端约定):
    # {"total": 1234.5, "count": 20,
    #  "items": [{"key": "饮食", "total": 300.0, "count": 8}, ...]}  按金额降序
    rows = _filter(storage.load_records(), args)
    total = round(sum(r["amount"] for r in rows), 2)

    group = args.get("group", "category")
    groups = defaultdict(lambda: [0.0, 0])
    for r in rows:
        key = r["category"] if group == "category" else r["date"]
        groups[key][0] += r["amount"]
        groups[key][1] += 1

    items = [{"key": k, "total": round(v[0], 2), "count": v[1]}
             for k, v in sorted(groups.items(), key=lambda x: -x[1][0])]
    return {"total": total, "count": len(rows), "items": items}


def summary():
    # 首页顶部三张小结卡片:本月总支出 / 总收入 / 结余
    month_prefix = datetime.date.today().strftime("%Y-%m")
    rows = [r for r in storage.load_records()
            if r["date"].startswith(month_prefix)]
    income = round(sum(r["amount"] for r in rows if r["type"] == "income"), 2)
    expense = round(sum(r["amount"] for r in rows if r["type"] == "expense"), 2)
    return {"income": income, "expense": expense, "balance": round(income - expense, 2)}
