// State management
let tasks = []
let userId = null
let username = null

// DOM elements
const taskForm = document.getElementById("taskForm")
const taskList = document.getElementById("taskList")
const taskCount = document.getElementById("taskCount")
const optimizeBtn = document.getElementById("optimizeBtn")
const loadBtn = document.getElementById("loadBtn")
const themeToggle = document.getElementById("themeToggle")
const resultsSection = document.getElementById("resultsSection")
const availableTimeInput = document.getElementById("availableTime")
const optimizationMethodSelect = document.getElementById("optimizationMethod")
const footerText = document.getElementById("footerText")

// Theme toggle
themeToggle.addEventListener("click", () => {
  const isDark = document.body.classList.toggle("dark-mode")
  localStorage.setItem("theme", isDark ? "dark" : "light")
  console.log("[v0] Theme toggled to:", isDark ? "dark" : "light")
})

// Load saved theme
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode")
}

function waitForAuth() {
  return new Promise((resolve) => {
    const checkAuth = setInterval(() => {
      if (window.currentUserId && window.firebaseDb) {
        userId = window.currentUserId
        username = localStorage.getItem("username")
        db = window.firebaseDb // Assign db variable here
        console.log("[v0] User ID set from Firebase:", userId)
        console.log("[v0] Username:", username)
        console.log("[v0] Firebase Database ready")
        clearInterval(checkAuth)
        resolve()
      }
    }, 100)
  })
}

// Initialize after auth is ready
waitForAuth().then(() => {
  console.log("[v0] App initialized with user:", userId)
})

// Add task
taskForm.addEventListener("submit", (e) => {
  e.preventDefault()

  if (!userId) {
    console.error("[v0] Cannot add task: User not authenticated")
    alert("Please wait for authentication to complete")
    return
  }

  const task = {
    id: Date.now(),
    name: document.getElementById("taskName").value,
    duration: Number.parseInt(document.getElementById("taskDuration").value),
    priority: Number.parseInt(document.getElementById("taskPriority").value),
    category: document.getElementById("taskCategory").value,
  }

  console.log("[v0] Adding task:", task.name)
  tasks.push(task)
  renderTasks()
  taskForm.reset()
  updateButtons()
})

// Render tasks
function renderTasks() {
  if (tasks.length === 0) {
    taskList.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="9" y1="9" x2="15" y2="9"/>
          <line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <p>No tasks yet. Add your first task above!</p>
      </div>
    `
  } else {
    taskList.innerHTML = tasks
      .map(
        (task) => `
      <div class="task-item ${task.category}">
        <div class="task-info">
          <div class="task-name">${task.name}</div>
          <div class="task-details">
            <span class="task-badge">⏱️ ${task.duration} min</span>
            <span class="task-badge">⭐ Priority ${task.priority}</span>
            <span class="task-badge">${getCategoryIcon(task.category)} ${task.category}</span>
          </div>
        </div>
        <button class="btn btn-danger" onclick="removeTask(${task.id})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
      </div>
    `,
      )
      .join("")
  }

  taskCount.textContent = `${tasks.length} task${tasks.length !== 1 ? "s" : ""}`
}

// Remove task
function removeTask(id) {
  tasks = tasks.filter((task) => task.id !== id)
  renderTasks()
  updateButtons()
}

// Get category icon
function getCategoryIcon(category) {
  const icons = {
    work: "💼",
    health: "💪",
    learning: "📚",
    chore: "🧹",
    relaxation: "🧘",
  }
  return icons[category] || "📋"
}

// Update button states
function updateButtons() {
  const hasTasks = tasks.length > 0
  optimizeBtn.disabled = !hasTasks
}

// Optimize tasks
optimizeBtn.addEventListener("click", async () => {
  if (tasks.length === 0) return

  optimizeBtn.disabled = true
  optimizeBtn.innerHTML = `
    <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="12" y1="2" x2="12" y2="6"/>
      <line x1="12" y1="18" x2="12" y2="22"/>
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
      <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
      <line x1="2" y1="12" x2="6" y2="12"/>
      <line x1="18" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
      <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
    </svg>
    Optimizing...
  `

  try {
    const availableTime = Number.parseFloat(availableTimeInput.value) * 60
    const method = optimizationMethodSelect.value

    console.log("[v0] Starting optimization for", tasks.length, "tasks with", availableTime, "minutes available")
    console.log("[v0] Using optimization method:", method)

    const response = await fetch("/api/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tasks: tasks,
        available_time: availableTime,
        method: method,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }))
      console.error("[v0] Optimization failed:", errorData)
      throw new Error(errorData.error || "Optimization failed")
    }

    const result = await response.json()
    console.log("[v0] Optimization successful:", result)
    console.log("[v0] Optimized tasks:", result.optimized_tasks.length, "Skipped tasks:", result.skipped_tasks.length)

    displayResults(result, method)

    console.log("[v0] Auto-saving tasks to Firebase after optimization...")
    await saveTasksToFirebase()
  } catch (error) {
    console.error("[v0] Error optimizing tasks:", error)
    alert("Failed to optimize tasks: " + error.message)
  } finally {
    optimizeBtn.disabled = false
    optimizeBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
      Optimize My Day
    `
  }
})

// Display results
function displayResults(result, method) {
  resultsSection.style.display = "block"

  // Update summary
  document.getElementById("totalTime").textContent = `${result.total_time} min`
  document.getElementById("totalValue").textContent = result.total_value.toFixed(1)
  document.getElementById("tasksIncluded").textContent = result.optimized_tasks.length

  // Display optimized tasks
  const optimizedList = document.getElementById("optimizedTasksList")
  if (result.optimized_tasks.length > 0) {
    optimizedList.innerHTML = result.optimized_tasks
      .map(
        (task) => `
      <div class="result-task-item">
        <div class="task-name">${task.name}</div>
        <div class="task-details">
          <span class="task-badge">⏱️ ${task.duration} min</span>
          <span class="task-badge">⭐ Priority ${task.priority}</span>
          <span class="task-badge">${getCategoryIcon(task.category)} ${task.category}</span>
        </div>
      </div>
    `,
      )
      .join("")
  } else {
    optimizedList.innerHTML = '<p style="color: var(--text-tertiary);">No tasks could fit in the available time.</p>'
  }

  // Display skipped tasks
  const skippedList = document.getElementById("skippedTasksList")
  if (result.skipped_tasks.length > 0) {
    skippedList.innerHTML = result.skipped_tasks
      .map(
        (task) => `
      <div class="result-task-item skipped">
        <div class="task-name">${task.name}</div>
        <div class="task-details">
          <span class="task-badge">⏱️ ${task.duration} min</span>
          <span class="task-badge">⭐ Priority ${task.priority}</span>
          <span class="task-badge">${getCategoryIcon(task.category)} ${task.category}</span>
        </div>
      </div>
    `,
      )
      .join("")
  } else {
    skippedList.innerHTML = '<p style="color: var(--text-tertiary);">All tasks included!</p>'
  }

  // Display explanation
  document.getElementById("explanationText").textContent = result.explanation

  if (method === "fractional") {
    footerText.textContent = "Powered by Fractional Knapsack Algorithm"
  } else {
    footerText.textContent = "Powered by 0/1 Knapsack Dynamic Programming Algorithm"
  }

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" })
}

async function saveTasksToFirebase() {
  try {
    if (!userId) {
      console.error("[v0] Cannot save: User ID not available")
      throw new Error("User not authenticated")
    }

    if (!db) {
      console.error("[v0] Cannot save: Firebase Database not initialized")
      throw new Error("Firebase Database not available")
    }

    const username = localStorage.getItem("username") || window.currentUsername
    if (!username) {
      console.error("[v0] Cannot save: Username not available")
      throw new Error("Username not available")
    }

    console.log("[v0] Saving", tasks.length, "tasks to Firebase for username:", username)
    console.log("[v0] Tasks data:", JSON.stringify(tasks, null, 2))

    const tasksRef = db.ref(`users/${username}/tasks`)
    const saveData = {
      tasks: tasks,
      saved_at: Date.now(),
      task_count: tasks.length,
    }

    console.log("[v0] Writing to Firebase path: users/" + username + "/tasks")

    await tasksRef.set(saveData)

    console.log("[v0] ✅ Tasks successfully saved to Firebase!")
    console.log("[v0] Saved data:", JSON.stringify(saveData, null, 2))

    alert("Tasks saved successfully!")
  } catch (error) {
    console.error("[v0] ❌ Error saving tasks to Firebase:", error)
    console.error("[v0] Error details:", error.message, error.code)
    alert("Failed to save tasks: " + error.message)
  }
}

loadBtn.addEventListener("click", async () => {
  if (!userId) {
    console.error("[v0] Cannot load: User ID not available")
    alert("User not authenticated")
    return
  }

  if (!db) {
    console.error("[v0] Cannot load: Firebase Database not initialized")
    alert("Firebase Database not available")
    return
  }

  const username = localStorage.getItem("username") || window.currentUsername
  if (!username) {
    console.error("[v0] Cannot load: Username not available")
    alert("Username not available")
    return
  }

  loadBtn.disabled = true
  const originalText = loadBtn.innerHTML
  loadBtn.innerHTML = `
    <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="12" y1="2" x2="12" y2="6"/>
    </svg>
    Loading...
  `

  try {
    console.log("[v0] Loading tasks from Firebase for username:", username)
    console.log("[v0] Reading from Firebase path: users/" + username + "/tasks")

    const tasksRef = db.ref(`users/${username}/tasks`)
    const snapshot = await tasksRef.once("value")
    const data = snapshot.val()

    console.log("[v0] Firebase snapshot exists:", snapshot.exists())
    console.log("[v0] Data loaded from Firebase:", JSON.stringify(data, null, 2))

    if (data && data.tasks && data.tasks.length > 0) {
      tasks = data.tasks
      console.log("[v0] ✅ Loaded", tasks.length, "tasks from Firebase")
      console.log("[v0] Tasks:", JSON.stringify(tasks, null, 2))
      renderTasks()
      updateButtons()
      alert(`Tasks loaded successfully! (${tasks.length} tasks)`)
    } else {
      console.log("[v0] ⚠️ No saved tasks found in Firebase")
      alert("No saved tasks found.")
    }
  } catch (error) {
    console.error("[v0] ❌ Error loading tasks from Firebase:", error)
    console.error("[v0] Error details:", error.message, error.code)
    alert("Failed to load tasks: " + error.message)
  } finally {
    loadBtn.disabled = false
    loadBtn.innerHTML = originalText
  }
})

// Add spinner animation
const style = document.createElement("style")
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .spinner {
    animation: spin 1s linear infinite;
  }
`
document.head.appendChild(style)

// Make removeTask globally accessible
window.removeTask = removeTask

// Initial render
renderTasks()
updateButtons()
