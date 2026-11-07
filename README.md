# 📒 轻松记账本

福州大学 2026秋软件工程现场编程作业 —— 个人记账本 Web 应用。
记录日常收支,按日期、类别、金额等维度查看统计,图表可视化。

## 运行环境

- Python 3.8+(开发使用 3.x)
- 依赖:flask(见 `requirements.txt`)
- 浏览器:Chrome / Edge 均可

## 启动步骤

```bash
pip install -r requirements.txt
python app.py            # 启动后访问 http://127.0.0.1:5000
```

首次使用数据为空属正常;演示前可运行 `python seed.py` 生成 12 条演示数据。

## 功能列表

| 功能 | 说明 | 入口 |
|---|---|---|
| 基础记账 | 记录日期、类型(支出/收入)、金额、类别、备注,带完整校验 | 主页左侧表单 |
| 查看数据 | 最近 10 笔记录、删除、本月收支小结卡片 | 主页 |
| 收支统计 | 按日期范围、类型、金额区间筛选,按类别/日期汇总 | /stats |
| 图表展示 | 支出构成环形图、每日收支对比柱状图(Chart.js) | /stats |
| 数据安全 | 每次写入前自动备份 `data/records.bak`;数据存本地 JSON 文件 | - |
| 导出 CSV | utf-8-sig 编码,Excel 双击打开中文不乱码 | 主页"导出CSV"按钮 |

## 项目结构(模块分工)

```
account-book/
├── app.py              # Flask 入口 + 路由(李嘉星)
├── storage.py          # 数据存储:JSON读写、校验、备份、CSV导出(林诗航)
├── record.py           # 记账模块:增/删/改(张炜鑫)
├── report.py           # 查看+统计:最近N笔、多维统计、本月小结(李莹莹)
├── templates/
│   ├── index.html      # 主页:记账表单+最近记录(谢玲洁)
│   └── stats.html      # 统计页+图表(王清源)
├── static/
│   ├── main.js         # 记录页逻辑(谢玲洁)
│   ├── stats.js        # 统计页逻辑(王清源)
│   └── style.css       # 全站样式
├── seed.py             # 演示数据一键生成(李嘉星)
├── data/records.json   # 数据文件(自动创建,不入库)
└── requirements.txt
```

## 前后端接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/records?limit=10` | 最近 N 笔记录 |
| POST | `/api/records` | 新增一笔,返回 `{ok, msg}` |
| DELETE | `/api/records/<id>` | 删除一笔,返回 `{ok, msg}` |
| GET | `/api/stats?start=&end=&type=&group=category\|date&min_amount=&max_amount=` | 多维统计 |
| GET | `/api/summary` | 本月支出/收入/结余 |
| GET | `/api/categories` | 类别固定清单 |
| GET | `/api/export/csv` | 导出 CSV 文件 |
