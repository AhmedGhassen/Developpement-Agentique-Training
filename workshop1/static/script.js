const listEl = document.getElementById("todo-list");
const formEl = document.getElementById("new-todo-form");
const inputEl = document.getElementById("new-todo-input");
const categorySelectEl = document.getElementById("new-todo-category");
const categoryFiltersEl = document.getElementById("category-filters");
const filterButtons = document.querySelectorAll(".filter-btn:not(.category-filter-btn)");

let currentFilter = "all";
let currentCategory = "all";

async function fetchCategories() {
  const res = await fetch("/api/categories");
  const categories = await res.json();

  // Peuple le <select> du formulaire d'ajout
  categorySelectEl.innerHTML = "";
  categories.forEach((cat) => {
    const option = document.createElement("option");
    option.value = cat;
    option.textContent = cat;
    categorySelectEl.appendChild(option);
  });

  // Peuple la rangée de boutons de filtre catégorie
  // (le bouton "Toutes catégories" est déjà présent dans le HTML)
  categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className = "filter-btn category-filter-btn";
    btn.dataset.category = cat;
    btn.textContent = cat;
    categoryFiltersEl.appendChild(btn);
  });

  categoryFiltersEl.querySelectorAll(".category-filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      categoryFiltersEl
        .querySelectorAll(".category-filter-btn")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentCategory = btn.dataset.category;
      fetchTodos();
    });
  });
}

async function fetchTodos() {
  const params = new URLSearchParams();
  if (currentFilter !== "all") params.set("completed", currentFilter);
  if (currentCategory !== "all") params.set("category", currentCategory);

  const query = params.toString();
  const url = query ? `/api/todos?${query}` : "/api/todos";

  const res = await fetch(url);
  const todos = await res.json();
  renderTodos(todos);
}

function renderTodos(todos) {
  listEl.innerHTML = "";
  todos.forEach((todo) => {
    const li = document.createElement("li");
    li.className = todo.completed ? "completed" : "";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.completed;
    checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

    const span = document.createElement("span");
    span.className = "todo-title";
    span.textContent = todo.title;

    const badge = document.createElement("span");
    badge.className = `category-badge category-${todo.category || "autre"}`;
    badge.textContent = todo.category || "autre";

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "✕";
    deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

    li.append(checkbox, span, badge, deleteBtn);
    listEl.appendChild(li);
  });
}

async function toggleTodo(id, completed) {
  await fetch(`/api/todos/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed }),
  });
  fetchTodos();
}

async function deleteTodo(id) {
  await fetch(`/api/todos/${id}`, { method: "DELETE" });
  fetchTodos();
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = inputEl.value.trim();
  if (!title) return;

  const category = categorySelectEl.value;

  await fetch("/api/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, category }),
  });

  inputEl.value = "";
  fetchTodos();
});

filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.filter;
    fetchTodos();
  });
});

async function init() {
  await fetchCategories();
  await fetchTodos();
}

init();
