document.addEventListener("DOMContentLoaded", async () => {
    const BASE_URL = "/api/project/project/track";
    let projectId = null;
    let tasks = [];
    let goals = [];
    let students = [];

    const taskList = document.getElementById("task-list");
    const goalFilter = document.getElementById("filter-goal");
    const statusFilter = document.getElementById("filter-status");

    const modal = document.getElementById("task-modal");
    const closeBtn = modal.querySelector(".close-btn");
    const assignedToSelect = document.getElementById("update-assigned-to");

    let currentTask = null;

    async function loadProjectId() {
        const res = await fetch(`${BASE_URL}/`);
        const data = await res.json();
        if (data.projects?.length > 0) {
            projectId = data.projects[0].id;
            students = data.students || [];
        }
    }

    async function loadGoalsAndTasks() {
        const res = await fetch(`${BASE_URL}/${projectId}/`);
        const data = await res.json();
        goals = data.goals || [];
        tasks = goals.flatMap(g => g.tasks.map(t => ({
            ...t,
            goal_id: g.id,
            goal_name: g.goal,
            goals: t.goals || ""
        })));
        populateGoalFilter();
        renderTasks();
    }

    function populateGoalFilter() {
        goalFilter.innerHTML = `<option value="">🎯 All Goals</option>`;
        goals.forEach(goal => {
            goalFilter.innerHTML += `<option value="${goal.id}">${goal.goal}</option>`;
        });
    }

    function renderTasks() {
        const goalVal = goalFilter.value;
        const statusVal = statusFilter.value;

        const filtered = tasks.filter(t => {
            return (!goalVal || String(t.goal_id) === goalVal) &&
                   (!statusVal || t.task_status === statusVal);
        });

        taskList.innerHTML = "";

        filtered.forEach(task => {
            const div = document.createElement("div");
            div.className = "proposal-card";
            div.innerHTML = `
                <div class="proposal-header">
                    <h4>${task.name}</h4>
                    <div class="status-group">
                        <span class="status ${task.task_status.replace(' ', '-')}">${task.task_status}</span>
                    </div>
                </div>
                <p><strong>Assigned To:</strong> ${
  students.find(s => s.id === task.assign_to)?.first_name + ' ' + students.find(s => s.id === task.assign_to)?.last_name || 'N/A'
}</p>
                <div class="card-buttons">
                    <button class="view-btn btn-edit" data-id="${task.id}">🔍 View</button>
                    <button class="btn btn-delete btn-delete-task" data-id="${task.id}">🗑️ Delete</button>
                </div>
            `;
            taskList.appendChild(div);
        });

        document.querySelectorAll(".view-btn").forEach(btn => {
            btn.addEventListener("click", () => openModal(btn.dataset.id));
        });

        document.querySelectorAll(".btn-delete-task").forEach(btn => {
            btn.addEventListener("click", () => handleDelete(btn.dataset.id));
        });
    }

    async function openModal(taskId) {
        currentTask = tasks.find(t => t.id == taskId);
        if (!currentTask) return;

        document.getElementById("update-task-name").value = currentTask.name || "";
        document.getElementById("update-task-goal").value = currentTask.goals || "";
        document.getElementById("update-outputs").value = currentTask.outputs || "";
        document.getElementById("update-deliverable").value = currentTask.deliverable_text || "";
        document.getElementById("update-deadline").value = currentTask.deadline_days || "";
        document.getElementById("update-status").value = currentTask.task_status;

        const goalSelect = document.getElementById("update-goal");
        goalSelect.innerHTML = goals.map(g => 
            `<option value="${g.id}" ${g.id == currentTask.goal_id ? "selected" : ""}>${g.goal}</option>`
        ).join("");

        assignedToSelect.innerHTML = students.map(s => {
        const fullName = [s.first_name, s.last_name].filter(Boolean).join(" ");
        return `<option value="${s.id}" ${s.id == currentTask.assign_to ? "selected" : ""}>${fullName}</option>`;
        }).join("");


        const fileDiv = document.getElementById("current-file-download");
        if (currentTask.deliverable_file_url) {
            fileDiv.innerHTML = `<a href="${currentTask.deliverable_file_url}" target="_blank" download>📎 Download Current File</a>`;
        } else {
            fileDiv.innerHTML = `<em>No file uploaded</em>`;
        }

        document.querySelectorAll("#task-update-form input, #task-update-form select, #task-update-form textarea").forEach(el => {
            el.setAttribute("disabled", true);
        });

        const feedbackContainer = document.getElementById("feedback-list");
        const feedbackRes = await fetch(`/api/project/tasks/${taskId}/`);
        const feedbackData = await feedbackRes.json();

        const sortedFeedbacks = (feedbackData.feedbacks || []).sort((a, b) =>
            new Date(a.created_at) - new Date(b.created_at)
        );
        
        feedbackContainer.innerHTML = sortedFeedbacks.length
          ? sortedFeedbacks.map(fb => `
              <div class="feedback-entry">
                <p><strong>${fb.sender} (${fb.sender_role}):</strong> ${fb.feedback_text}</p>
                <p class="timestamp">🕒 ${new Date(fb.created_at).toLocaleString()}</p>
                ${fb.feedback_file ? `<p><a href="${fb.feedback_file}" target="_blank">📎 File</a></p>` : ""}
              </div>
            `).join("")
          : "<p>No feedback yet.</p>";
    
        modal.classList.remove("hidden");
    }

    const feedbackForm = document.getElementById("student-feedback-form");
    feedbackForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(feedbackForm);
        formData.append("project", projectId);
        formData.append("task_id", currentTask.id);

        const res = await fetch("/api/project/feedback/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: formData
        });

        if (res.ok) {
            showAlert("✅ Reply sent!", "success");
            feedbackForm.reset();
            await openModal(currentTask.id); // Refresh feedback
        } else {
            showAlert("❌ Failed to send reply.", "error");
        }
        
    };

    async function handleDelete(taskId) {
        if (!confirm("Are you sure you want to delete this task?")) return;

        const formData = new FormData();
        formData.append("task_id", taskId);

        const res = await fetch(`${BASE_URL}/${projectId}/`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: formData
        });

        if (res.ok) {
            showAlert("🗑️ Task deleted.", 'success');
            await loadGoalsAndTasks();
        } else {
            showAlert("⚠️ Failed to delete task.", 'error');
        }
    }

    closeBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
        currentTask = null;
    });

    goalFilter.addEventListener("change", renderTasks);
    statusFilter.addEventListener("change", renderTasks);

    await loadProjectId();
    await loadGoalsAndTasks();
});
