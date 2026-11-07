// theme.js — 暗色模式开关(全站共用)
// Bootstrap 5.3 原生 data-bs-theme,偏好存在 localStorage

const themeBtn = document.getElementById("theme-btn");

function applyTheme(t) {
  document.documentElement.setAttribute("data-bs-theme", t);
  if (themeBtn) themeBtn.textContent = t === "dark" ? "☀️" : "🌙";
  localStorage.setItem("theme", t);
}

if (themeBtn) {
  themeBtn.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-bs-theme");
    applyTheme(cur === "dark" ? "light" : "dark");
  });
}
// 按钮文案与 localStorage 里保存的偏好对齐(head 里的内联脚本已先设置属性)
applyTheme(document.documentElement.getAttribute("data-bs-theme") || "light");
