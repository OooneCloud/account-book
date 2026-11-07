// main.js — 记录页逻辑(成员E 谢玲洁)
// 与后端交互的三个点:类别下拉(/api/categories)、小结卡片(/api/summary)、
// 记录增删查(/api/records)

// 防止备注内容里的特殊字符破坏页面结构
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g,
    c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

// 填充类别下拉框:类别清单从后端取,保证和后端校验永远一致
async function loadCategories() {
  const res = await fetch("/api/categories");
  const categories = await res.json();
  const select = document.getElementById("category");
  select.innerHTML = categories
    .map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`)
    .join("");
}

// 本月小结三张卡片
async function loadSummary() {
  const res = await fetch("/api/summary");
  const s = await res.json();
  document.getElementById("sum-expense").textContent = s.expense.toFixed(2);
  document.getElementById("sum-income").textContent = s.income.toFixed(2);
  const balance = document.getElementById("sum-balance");
  balance.textContent = s.balance.toFixed(2);
  balance.className = s.balance >= 0 ? "text-success" : "text-danger";
}

// 最近10笔记录表格
async function loadRecent() {
  const res = await fetch("/api/records?limit=10");
  const records = await res.json();
  const tbody = document.getElementById("record-tbody");

  if (!records.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">
      还没有记录,先在左边记一笔吧</td></tr>`;
    return;
  }
  tbody.innerHTML = records.map(r => {
    const income = r.type === "income";
    return `<tr>
      <td>${r.date}</td>
      <td><span class="badge ${income ? "bg-success" : "bg-danger"}">
        ${income ? "收入" : "支出"}</span></td>
      <td>${escapeHtml(r.category)}</td>
      <td class="text-end ${income ? "text-success" : "text-danger"}">
        ${income ? "+" : "-"}${r.amount.toFixed(2)}</td>
      <td>${escapeHtml(r.note) || "-"}</td>
      <td><button class="btn btn-outline-danger btn-sm"
        onclick="removeRecord(${r.id})">删除</button></td>
    </tr>`;
  }).join("");
}

// 表单提交:POST 一笔新记录,后端校验失败时把原因 alert 给用户
async function addRecord(e) {
  e.preventDefault();
  const form = document.getElementById("record-form");
  const data = {
    date: form.date.value,
    type: form.type.value,
    amount: parseFloat(form.amount.value),
    category: form.category.value,
    note: form.note.value
  };
  const res = await fetch("/api/records", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  const json = await res.json();
  if (json.ok) {
    form.reset();
    form.date.value = new Date().toISOString().slice(0, 10);  // 日期重置为今天
    loadRecent();
    loadSummary();
  }
  alert(json.msg);
}

// 删除一笔记账,确认后调 DELETE 接口
async function removeRecord(id) {
  if (!confirm("确定删除这条记录吗?")) return;
  await fetch("/api/records/" + id, { method: "DELETE" });
  loadRecent();
  loadSummary();
}

// 页面初始化
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("record-form").addEventListener("submit", addRecord);
  document.getElementById("record-form").date.value = new Date().toISOString().slice(0, 10);
  loadCategories();
  loadSummary();
  loadRecent();
});

// ---------- 新增功能:月度环比 / 预算进度条 / 暗色模式 ----------

// 月度环比:支出较上月 📈/📉
async function loadTrend() {
  const t = await (await fetch("/api/trend")).json();
  const el = document.getElementById("mom-trend");
  if (!el) return;
  if (t.change_percent === null) {
    el.textContent = "上月暂无支出,暂无环比";
    return;
  }
  const up = t.change_percent > 0;
  el.textContent = `本月支出较上月 ${up ? "↑" : "↓"} ${Math.abs(t.change_percent)}%`;
}

// 本月预算进度条:<80%绿,80%~100%黄,超支红
async function loadBudget() {
  const b = await (await fetch("/api/budget")).json();
  const bar = document.getElementById("budget-bar");
  if (!bar) return;
  bar.style.width = Math.min(b.percent, 100) + "%";
  bar.className = "progress-bar " +
    (b.percent >= 100 ? "bg-danger" : b.percent >= 80 ? "bg-warning" : "bg-success");
  document.getElementById("budget-text").textContent =
    `已花 ¥${b.spent.toFixed(2)} / ¥${b.budget.toFixed(2)}`;
  const hint = document.getElementById("budget-hint");
  if (b.percent >= 100) {
    hint.textContent = "⚠️ 本月已超支,剁手前先冷静一下!";
  } else if (b.percent >= 80) {
    hint.textContent = `⚡ 预算快用完了,只剩 ¥${(b.budget - b.spent).toFixed(2)}`;
  } else {
    hint.textContent = `还剩 ¥${(b.budget - b.spent).toFixed(2)} 可花,已用 ${b.percent}%`;
  }
}

// 点击✏️修改预算
function bindBudgetEdit() {
  const btn = document.getElementById("budget-edit");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const cur = (await (await fetch("/api/budget")).json()).budget;
    const input = prompt("设置本月预算金额(元):", cur);
    if (input === null) return;   // 用户取消
    const res = await (await fetch("/api/budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount: parseFloat(input) })
    })).json();
    alert(res.msg);
    loadBudget();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadTrend();
  loadBudget();
  bindBudgetEdit();
});
