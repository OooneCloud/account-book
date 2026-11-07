# seed.py — 演示数据一键生成(成员A 李嘉星)
# 演示前运行一次:python seed.py,生成 12 条真实感数据(金额避免全是整数)
# 注意:data/ 已在 .gitignore 中,演示数据不进仓库,换机器演示时重跑本脚本即可

import random
import storage

DEMO_RECORDS = [
    ("2026-11-07", "expense", 22.5,  "饮食", "食堂午饭"),
    ("2026-11-07", "expense", 4.0,   "交通", "地铁通勤"),
    ("2026-11-06", "expense", 15.8,  "饮食", "奶茶一杯"),
    ("2026-11-06", "income",  3200.0, "兼职", "家教课时费"),
    ("2026-11-05", "expense", 89.9,  "购物", "洗衣液等日用品"),
    ("2026-11-05", "expense", 42.0,  "娱乐", "电影票"),
    ("2026-11-04", "expense", 128.5, "购物", "秋冬长袖T恤"),
    ("2026-11-03", "expense", 35.0,  "交通", "打车去高铁站"),
    ("2026-11-01", "income",  1500.0, "工资", "实习补贴"),
    ("2026-10-28", "expense", 268.0, "娱乐", "演唱会门票(平摊)"),
    ("2026-10-25", "expense", 9.9,   "饮食", "早餐豆浆油条"),
    ("2026-10-20", "income",  200.0, "其他", "二手书出售"),
]


def main():
    records = []
    for i, (date, rtype, amount, category, note) in enumerate(DEMO_RECORDS, start=1):
        records.append({
            "id": i, "date": date, "type": rtype,
            "amount": amount, "category": category, "note": note,
        })
    storage.save_records(records)
    print("已生成%d条演示数据 -> %s" % (len(records), storage.DATA_FILE))


if __name__ == "__main__":
    main()
