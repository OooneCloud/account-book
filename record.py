# record.py — 记账模块(成员C 张炜鑫)
# 负责「基础记账」需求:新增、修改、删除一笔收支
# 所有数据落盘都经由 storage.py,本模块不做文件读写

import storage

# 类别清单供 app.py / 前端对齐使用,唯一出处仍在 storage.py
CATEGORIES = storage.CATEGORIES


def add_record(data):
    # 新增记账:先校验(防脏数据落盘),再分配自增id写入
    ok, msg = storage.validate(data)
    if not ok:
        return False, msg

    records = storage.load_records()
    # 归一化:金额统一转成两位小数的数字,备注缺省为空串
    data["amount"] = round(float(data["amount"]), 2)
    data["note"] = (data.get("note") or "").strip()
    data["id"] = storage.next_id(records)

    records.append(data)
    storage.save_records(records)
    return True, "记账成功"


def delete_record(rid):
    # 删除:按id过滤,未找到时如实返回,便于前端提示"记录不存在"
    records = storage.load_records()
    remaining = [r for r in records if r["id"] != rid]
    if len(remaining) == len(records):
        return False, "记录不存在"
    storage.save_records(remaining)
    return True, "删除成功"


def update_record(rid, data):
    # 修改:仅允许改日期/类型/金额/类别/备注,id不变
    # 注意:修改后的内容同样要走一遍校验
    records = storage.load_records()
    target = next((r for r in records if r["id"] == rid), None)
    if target is None:
        return False, "记录不存在"

    merged = {**target, **data}
    merged.pop("id", None)          # id 不许改
    ok, msg = storage.validate(merged)
    if not ok:
        return False, msg

    merged["id"] = rid
    merged["amount"] = round(float(merged["amount"]), 2)
    records[records.index(target)] = merged
    storage.save_records(records)
    return True, "修改成功"
