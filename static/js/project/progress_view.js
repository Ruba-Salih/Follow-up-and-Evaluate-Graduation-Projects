document.addEventListener("DOMContentLoaded", async () => {
    const pathMatch = window.location.pathname.match(/\/project\/(\d+)\/progress\/?/);
    const projectId = pathMatch ? pathMatch[1] : null;
    if (!projectId) return;

    const taskList = document.getElementById("task-list");
    const goalFilter = document.getElementById("filter-goal");
    const statusFilter = document.getElementById("filter-status");
    const studentFilter = document.getElementById("filter-student");

    let goals = [];
    let tasks = [];
    let students = [];

    const res = await fetch(`/api/project/project/track/${projectId}/`);
    const data = await res.json();

    if (!res.ok) {
        taskList.innerHTML = `<p>❌ Failed to load project data</p>`;
        return;
    }

    goals = data.goals || [];
    students = data.students || [];

    tasks = goals.flatMap(goal =>
        goal.tasks.map(task => ({
            ...task,
            goal_id: goal.id,
            goal_name: goal.goal
        }))
    );

    goalFilter.innerHTML += goals.map(g => `<option value="${g.id}">${g.goal}</option>`).join("");
    studentFilter.innerHTML += students.map(s => {
    const fullName = [s.first_name, s.last_name].filter(Boolean).join(" ");
    return `<option value="${s.id}">${fullName || s.username}</option>`;
}).join("");


    function renderTasks() {
        const goalVal = goalFilter.value;
        const statusVal = statusFilter.value;
        const studentVal = studentFilter.value;

        const filtered = tasks.filter(t =>
            (!goalVal || String(t.goal_id) === goalVal) &&
            (!statusVal || t.task_status === statusVal) &&
            (!studentVal || String(t.assign_to ?? "") === String(studentVal))
        );

        taskList.innerHTML = "";

        if (!filtered.length) {
            taskList.innerHTML = `<p>No tasks found for selected filters.</p>`;
            return;
        }

        filtered.forEach(task => {
            const div = document.createElement("div");
            div.className = "proposal-card";

            const statusClass = (task.task_status || '').toLowerCase().replace(/\s/g, '-');

            div.innerHTML = `
                <div class="proposal-header">
                    <h4>${task.name}</h4>
                    <div class="status-group">
                        <span class="status ${statusClass}">${task.task_status || 'N/A'}</span>
                    </div>
                </div>
                <p><strong>Goal:</strong> ${task.goal_name}</p>
                <p><strong>Assigned To:</strong> ${task.assign_to_name || 'N/A'}</p>
                <p><strong>Created:</strong> ${task.created_at?.slice(0, 10) || '-'}  <strong>Updated:</strong> ${task.updated_at?.slice(0, 10) || '-'}</p>
                <div class="card-buttons">
                    <button class="view-btn view-task-btn" data-task-id="${task.id}">🔍 View</button>
                </div>
            `;
            taskList.appendChild(div);
        });

        document.querySelectorAll(".view-task-btn").forEach(btn => {
            btn.addEventListener("click", () => openTaskModal(btn.dataset.taskId));
        });
    }

    async function openTaskModal(taskId) {
        const modal = document.getElementById("task-modal");
        const modalContent = document.getElementById("task-detail-content");
        const closeBtn = modal.querySelector(".close-btn");

        const res = await fetch(`/api/project/tasks/${taskId}/`);
        const data = await res.json();

        if (!res.ok) {
            modalContent.innerHTML = `<p>❌ Failed to load task details</p>`;
        } else {
            const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfInput ? csrfInput.value : "";

            const sortedFeedbacks = (data.feedbacks || []).sort(
                (a, b) => new Date(a.created_at) - new Date(b.created_at)
            );

            const feedbackEntries = sortedFeedbacks.map(fb => `
                <div class="feedback-entry">
                    <p><strong>${fb.sender} (${fb.sender_role}):</strong> ${fb.feedback_text}</p>
                    <p class="timestamp">🕒 ${new Date(fb.created_at).toLocaleString()}</p>
                    ${fb.feedback_file ? `<p><a href="${fb.feedback_file}" target="_blank">📎 File</a></p>` : ""}
                </div>
            `).join("");

            modalContent.innerHTML = `
                <h3>Task Name: ${data.name}</h3>
                <p><strong> Project Goal:</strong> ${data.goal?.goal || '-'}</p>
                <p><strong> Task Goal:</strong> ${data.goals || '-'}</p>
                <p><strong> Expected Outputs:</strong> ${data.outputs || '-'}</p>
                <p><strong> Assigned To:</strong> ${data.assign_to_name || '-'}</p>
                <p><strong> Deadline:</strong> ${data.deadline_days || '-'} days</p>
                <p><strong> Deliverable:</strong> ${data.deliverable_text || '-'}</p>
                ${data.deliverable_file ? `<p><a href="${data.deliverable_file}" target="_blank">📎 Download File</a></p>` : ""}
                <hr>
                <h4>💬 Feedback Thread</h4>
                <div class="feedback-list">${feedbackEntries || '<p>No feedback yet.</p>'}</div>
                <hr>
                <h4>✍️ Reply / Add Feedback</h4>
                <form id="feedback-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <input type="hidden" name="project" value="${data.project}">
                    <input type="hidden" name="task_id" value="${taskId}">
                    <textarea name="feedback_text" id="feedback-comment" placeholder="Write your feedback or reply..." required></textarea>
                    <button type="submit" class="view-btn">Send</button>
                    <p id="feedback-message"></p>
                </form>
            `;

            attachFeedbackForm();
        }

        modal.classList.remove("hidden");
        closeBtn.onclick = () => modal.classList.add("hidden");
    }

    function attachFeedbackForm() {
    const form = document.getElementById("feedback-form");
    form?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value || "";

        const payload = {
            project: form.querySelector('[name=project]')?.value,
            task_id: form.querySelector('[name=task_id]')?.value,
            feedback_text: form.querySelector('#feedback-comment')?.value
        };

        const res = await fetch("/api/project/feedback/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });

        const msg = document.getElementById("feedback-message");
        if (res.ok) {
            msg.textContent = "✅ Feedback sent!";
            msg.style.color = "green";
            form.reset();
            await openTaskModal(payload.task_id); // reload modal with feedback
        } else {
            msg.textContent = "❌ Failed to send feedback.";
            msg.style.color = "red";
        }
    });
}

    goalFilter.addEventListener("change", renderTasks);
    statusFilter.addEventListener("change", renderTasks);
    studentFilter.addEventListener("change", renderTasks);

    renderTasks();
});
