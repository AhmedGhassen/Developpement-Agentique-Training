const listEl = document.getElementById("todo-list");
const formEl = document.getElementById("new-todo-form");
const inputEl = document.getElementById("new-todo-input");
const filterButtons = document.querySelectorAll(".filter-btn");

let currentFilter = "all";

async function fetchTodos() {
  const url = currentFilter === "all"
    ? "/api/todos"
    : `/api/todos?completed=${currentFilter}`;

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
    span.textContent = todo.title;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "✕";
    deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

    li.append(checkbox, span, deleteBtn);
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
    body: JSON.stringify({ title }),
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

fetchTodos();
