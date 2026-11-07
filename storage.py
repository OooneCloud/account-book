# storage.py — 数据存储模块(成员B 林诗航)
# 全组的地基:所有记录的读写、校验、备份、CSV导出都由本模块负责
# 其他模块(record.py / report.py)只许通过这里的函数碰数据

import json
import os
import shutil
import datetime
import csv

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "records.json")
BAK_FILE = os.path.join(DATA_DIR, "records.bak")   # 自动备份文件(亮点②)
CSV_FILE = os.path.join(DATA_DIR, "records.csv")   # CSV导出文件(亮点③)

# 类别固定清单:与前端下拉框、record.py 共用,唯一出处在这里
CATEGORIES = ["饮食", "交通", "购物", "娱乐", "工资", "兼职", "其他"]

NOTE_MAX_LEN = 50


def load_records():
    # 读取全部记录;文件不存在、为空或损坏时返回 [],保证程序首次运行不报错
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
        return records if isinstance(records, list) else []
    except (json.JSONDecodeError, OSError):
        # 数据文件损坏时不去覆盖它,交给备份文件人工恢复
        return []


def save_records(records):
    # 写回 JSON。亮点②:写入前先把旧文件备份为 records.bak,
    # 防止写坏文件导致用户全部记账记录丢失
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DATA_FILE):
        shutil.copy(DATA_FILE, BAK_FILE)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False 保证中文原样写入不乱码;indent=2 方便调试查看
        json.dump(records, f, ensure_ascii=False, indent=2)


def next_id(records):
    # 自增 id:当前最大 id + 1,空数据从 1 开始
    return max((r["id"] for r in records), default=0) + 1


def validate(data):
    # 数据校验:不合法时返回 (False, 原因),调用方(前端)据此提示用户
    # 校验前置,保证落盘的数据永远是干净的
    if not isinstance(data, dict):
        return False, "数据格式不正确"

    try:
        datetime.datetime.strptime(data.get("date", ""), "%Y-%m-%d")
    except (ValueError, TypeError):
        return False, "日期格式应为 YYYY-MM-DD"

    if data.get("type") not in ("expense", "income"):
        return False, "类型只能是 expense 或 income"

    try:
        if float(data.get("amount", 0)) <= 0:
            return False, "金额必须大于0"
    except (ValueError, TypeError):
        return False, "金额必须是数字"

    if data.get("category") not in CATEGORIES:
        return False, "类别不合法,必须是:" + "、".join(CATEGORIES)

    note = data.get("note", "") or ""
    if not isinstance(note, str) or len(note) > NOTE_MAX_LEN:
        return False, "备注不能超过%d字" % NOTE_MAX_LEN

    return True, ""


def export_csv():
    # 亮点③:导出全部记录为 CSV。
    # 用 utf-8-sig 编码(带 BOM 头),Excel 双击打开中文不乱码
    os.makedirs(DATA_DIR, exist_ok=True)
    records = load_records()
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "日期", "类型", "金额", "类别", "备注"])
        for r in records:
            writer.writerow([
                r["id"], r["date"],
                "支出" if r["type"] == "expense" else "收入",
                r["amount"], r["category"], r.get("note", ""),
            ])
    return CSV_FILE


if __name__ == "__main__":
    # 自测块:python storage.py 直接跑,验证读写闭环
    # 1) 空数据首次运行
    print("首次读取(文件应不存在):", load_records())
    # 2) 新增→保存→重新读取
    demo = {"date": "2026-11-07", "type": "expense",
            "amount": 25.5, "category": "饮食", "note": "午饭"}
    ok, msg = validate(demo)
    print("校验通过:", ok, msg)
    records = load_records()
    demo["id"] = next_id(records)
    records.append(demo)
    save_records(records)
    print("保存后重新读取:", load_records())
    # 3) 非法数据校验
    bad = {"date": "2026/11/07", "type": "expense", "amount": -1, "category": "饮食"}
    print("非法数据校验:", validate(bad))
    # 4) CSV 导出
    print("CSV 导出至:", export_csv())
