// stats.js — 统计页逻辑(成员F 王清源)
// 数据全部来自李莹莹的 /api/stats 接口:
//   环形图  /api/stats?group=category&type=expense (+筛选条件)
//   柱状图  /api/stats?group=date&type=expense / type=income (红绿两根柱)
//   折线图  同柱状图口径,补零成连续时间轴(默认最近30天)
// 明细表与统计口径一致,占比 = 该项金额 / 总金额

const charts = {};   // 保存图表实例,刷新前销毁旧图避免叠加

// 把筛选栏的条件拼成查询字符串
function queryFor(extra = {}) {
  const params = new URLSearchParams(extra);
  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;
  const min = document.getElementById("min-amount").value;
  const max = document.getElementById("max-amount").value;
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  if (min) params.set("min_amount", min);
  if (max) params.set("max_amount", max);
  return params.toString();
}

// 日期框自定义占位提示:没选日期时显示"年/月/日",选了就隐藏
function bindDatePlaceholder(id) {
  const input = document.getElementById(id);
  const wrap = input.closest(".date-wrap");
  const sync = () => wrap.classList.toggle("empty", !input.value);
  input.addEventListener("input", sync);
  input.addEventListener("change", sync);
  sync();
}

async function fetchStats(extra = {}) {
  const res = await fetch("/api/stats?" + queryFor(extra));
  return res.json();
}

// 支出类别占比环形图(类型=收入时改为收入占比)
async function renderPie() {
  const type = document.getElementById("type").value === "income" ? "income" : "expense";
  const data = await fetchStats({ group: "category", type });
  if (charts.pie) charts.pie.destroy();
  charts.pie = new Chart(document.getElementById("pie"), {
    type: "doughnut",
    data: {
      labels: data.items.map(x => x.key),
      datasets: [{
        data: data.items.map(x => x.total),
        backgroundColor: ["#ef5350","#ab47bc","#5c6bc0","#29b6f6",
                          "#26a69a","#ffca28","#8d6e63"]
      }]
    },
  options: {
    maintainAspectRatio: false,   // 填满固定高度的容器,和柱状图保持等高
    plugins: {
      title: { display: true, text: (type === "expense" ? "支出" : "收入") + "构成占比" }
    }
  }
  });
  return data;
}

// 每日收支对比柱状图:支出红、收入绿,符合中文习惯
async function renderBar() {
  const [expense, income] = await Promise.all([
    fetchStats({ group: "date", type: "expense" }),
    fetchStats({ group: "date", type: "income" })
  ]);
  // 合并两组的日期作为横轴,统一排序
  const dates = [...new Set([...expense.items.map(x => x.key),
                             ...income.items.map(x => x.key)])].sort();
  const pick = (data, d) => {
    const item = data.items.find(x => x.key === d);
    return item ? item.total : 0;
  };
  if (charts.bar) charts.bar.destroy();
  charts.bar = new Chart(document.getElementById("bar"), {
    type: "bar",
    data: {
      labels: dates,
      datasets: [
        { label: "支出", data: dates.map(d => pick(expense, d)), backgroundColor: "#ef5350" },
        { label: "收入", data: dates.map(d => pick(income, d)), backgroundColor: "#66bb6a" }
      ]
    },
    options: {
      maintainAspectRatio: false,  // 填满固定高度的容器,和环形图保持等高
      plugins: { title: { display: true, text: "每日收支对比" } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

// 收支趋势折线图:横轴为日期(默认最近30天,筛选了起止日期则跟随筛选范围),
// 无记录的日期补0,保证曲线连续;类型筛选决定画哪条线
async function renderTrend() {
  const type = document.getElementById("type").value;
  const day = 24 * 60 * 60 * 1000;
  const endStr = document.getElementById("end").value
    || new Date().toLocaleDateString("sv-SE");            // sv-SE 直接得到 YYYY-MM-DD
  const startStr = document.getElementById("start").value
    || new Date(Date.parse(endStr) - 29 * day).toLocaleDateString("sv-SE");

  const days = Math.max(1, Math.round((Date.parse(endStr) - Date.parse(startStr)) / day) + 1);
  const dates = Array.from({ length: days }, (_, i) =>
    new Date(Date.parse(startStr) + i * day).toLocaleDateString("sv-SE"));

  const series = {};
  const types = type === "all" ? ["expense", "income"] : [type];
  await Promise.all(types.map(async t => {
    const data = await fetchStats({ group: "date", type: t });
    const byDate = new Map(data.items.map(x => [x.key, x.total]));
    series[t] = dates.map(d => byDate.get(d) || 0);       // 缺数据的日期补0
  }));

  const palette = { expense: "#ef5350", income: "#66bb6a" };
  const names = { expense: "支出", income: "收入" };
  if (charts.trend) charts.trend.destroy();
  charts.trend = new Chart(document.getElementById("trend"), {
    type: "line",
    data: {
      labels: dates,
      datasets: types.map(t => ({
        label: names[t],
        data: series[t],
        borderColor: palette[t],
        backgroundColor: palette[t],
        tension: 0.3,
        pointRadius: 2
      }))
    },
    options: {
      maintainAspectRatio: false,   // 与另外两张图统一等高风格
      plugins: { title: { display: true, text: `${startStr} ~ ${endStr} 收支趋势` } },
      scales: {
        x: { ticks: { maxTicksLimit: 10, autoSkip: true } },
        y: { beginAtZero: true }
      }
    }
  });
}

// 明细表:类别/日期、金额、笔数、占比
function renderTable(data) {
  const tbody = document.getElementById("stat-tbody");
  if (!data.items.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">
      所选范围内暂无数据</td></tr>`;
  } else {
    tbody.innerHTML = data.items.map(x => {
      const pct = data.total ? (x.total / data.total * 100).toFixed(1) : "0.0";
      return `<tr>
        <td>${x.key}</td>
        <td class="text-end">${x.total.toFixed(2)}</td>
        <td class="text-end">${x.count}</td>
        <td class="text-end">${pct}%</td>
      </tr>`;
    }).join("");
  }
  document.getElementById("stat-desc").textContent =
    `当前统计:${typeLabel()} · 共${data.count}笔 · 合计${data.total.toFixed(2)}元`;
}

function typeLabel() {
  return { all: "全部类型", expense: "支出", income: "收入" }[document.getElementById("type").value];
}

// 主刷新:四块内容并行更新
async function refreshAll() {
  const pieData = await renderPie();
  renderTable(pieData);   // 明细表与环形图同口径
  await renderBar();
  await renderTrend();
}

// 页面初始化 + 筛选条件变化自动刷新
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("refresh-btn").addEventListener("click", refreshAll);
  ["start", "end", "type", "min-amount", "max-amount"].forEach(id =>
    document.getElementById(id).addEventListener("change", refreshAll));
  bindDatePlaceholder("start");
  bindDatePlaceholder("end");
  refreshAll();
});
