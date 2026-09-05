const listEl = document.getElementById("todo-list");
const formEl = document.getElementById("new-todo-form");
const inputEl = document.getElementById("new-todo-input");
const categoryEl = document.getElementById("new-todo-category");
const filterButtons = document.querySelectorAll(".filter-btn");

const filters = {
  completed: "all",
  category: "all",
};

async function fetchTodos() {
  const params = new URLSearchParams();
  if (filters.completed !== "all") params.set("completed", filters.completed);
  if (filters.category !== "all") params.set("category", filters.category);
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
    checkbox.setAttribute("aria-label", `Marquer ${todo.title} comme terminée`);
    checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

    const span = document.createElement("span");
    span.textContent = todo.title;

    const category = document.createElement("small");
    category.className = `todo-category category-${todo.category}`;
    category.textContent = todo.category;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "✕";
    deleteBtn.type = "button";
    deleteBtn.setAttribute("aria-label", `Supprimer ${todo.title}`);
    deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

    li.append(checkbox, span, category, deleteBtn);
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

  await fetch("/api/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, category: categoryEl.value }),
  });

  inputEl.value = "";
  fetchTodos();
});

filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const group = btn.dataset.filterGroup;
    document
      .querySelectorAll(`.filter-btn[data-filter-group="${group}"]`)
      .forEach((b) => {
        b.classList.remove("active");
        b.setAttribute("aria-pressed", "false");
      });
    btn.classList.add("active");
    btn.setAttribute("aria-pressed", "true");
    filters[group] = btn.dataset.filter;
    fetchTodos();
  });
});

fetchTodos();
