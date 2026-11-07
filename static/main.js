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
