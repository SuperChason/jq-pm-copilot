const modal = document.querySelector("[data-modal]");
const firstModalField = modal.querySelector("input");
const openButton = document.querySelector("[data-open-modal]");
const closeButtons = document.querySelectorAll("[data-close-modal]");
const createForm = document.querySelector("[data-create-form]");
const toast = document.querySelector("[data-toast]");
const tableView = document.querySelector("[data-table-view]");
const emptyView = document.querySelector("[data-empty-view]");
const toggleEmpty = document.querySelector("[data-toggle-empty]");
const clearEmpty = document.querySelector("[data-clear-empty]");
const filterForm = document.querySelector(".filters");
const resultCount = document.querySelector(".table-toolbar p");
let lastFocused = null;

function openModal() {
  lastFocused = document.activeElement;
  modal.hidden = false;
  firstModalField.focus();
}

function closeModal() {
  modal.hidden = true;
  if (lastFocused) lastFocused.focus();
}

function showToast(message) {
  toast.textContent = message;
  toast.hidden = false;
  window.setTimeout(() => {
    toast.hidden = true;
  }, 2600);
}

openButton.addEventListener("click", openModal);
closeButtons.forEach((button) => button.addEventListener("click", closeModal));

modal.addEventListener("click", (event) => {
  if (event.target === modal) closeModal();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modal.hidden) closeModal();
});

createForm.addEventListener("submit", (event) => {
  event.preventDefault();
  closeModal();
  showToast("任务已创建，可以继续配置审核规则。");
  createForm.reset();
});

filterForm.addEventListener("submit", (event) => {
  event.preventDefault();
  resultCount.textContent = "共 1 条记录（演示筛选）";
  showToast("筛选条件已应用。");
});

filterForm.addEventListener("reset", () => {
  window.requestAnimationFrame(() => {
    resultCount.textContent = "共 1286 条记录";
    showToast("筛选条件已重置。");
  });
});

toggleEmpty.addEventListener("click", () => {
  tableView.hidden = true;
  emptyView.hidden = false;
  clearEmpty.focus();
});

clearEmpty.addEventListener("click", () => {
  emptyView.hidden = true;
  tableView.hidden = false;
  toggleEmpty.focus();
});
