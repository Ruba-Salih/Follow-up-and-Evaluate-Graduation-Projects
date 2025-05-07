document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const departmentFilter = document.getElementById("department-filter");
    const projectList = document.getElementById("project-list");
    const modal = document.getElementById("coord-modal");
    const closeBtn = document.querySelector(".close-btn");

    const modalTitle = document.getElementById("modal-title-text");
    const modalField = document.getElementById("modal-field");
    const modalDescription = document.getElementById("modal-description");
    const modalTeamCount = document.getElementById("modal-team-count");
    const modalTeamMembers = document.getElementById("modal-team-members");
    const modalSupervisor = document.getElementById("modal-supervisor");
    const modalReader = document.getElementById("modal-reader");
    const modalJudges = document.getElementById("modal-judges");
    const modalFile = document.getElementById("modal-file");

    const modalCompletion = document.getElementById("completion-status");
    const tasksList = document.getElementById("tasks-list");
    const logsList = document.getElementById("logs-list");

    // 🆕 Correct feedback IDs
    const feedbackInput = document.getElementById("coord-feedback-input");
    const submitFeedbackBtn = document.getElementById("submit-feedback-btn");
    const feedbackMessage = document.getElementById("feedback-message");

    let currentProjectId = null;

    const container = document.getElementById("project-container");
    const IS_SUPER_COORD = container ? container.dataset.superCoord === "true" : false;

    async function loadProjects() {
        try {
            const res = await fetch("/api/project/project/track/");
            const data = await res.json();
            renderProjects(data.projects || []);
            if (IS_SUPER_COORD && departmentFilter) {
                departmentFilter.style.display = "inline-block";
                populateDepartmentFilter(data.departments || []);
            }
        } catch (err) {
            console.error("Error loading projects:", err);
            projectList.innerHTML = `<p class="text-danger">⚠️ Failed to load projects.</p>`;
        }
    }

    function populateDepartmentFilter(departmentsList) {
        departmentFilter.innerHTML = `<option value="">All Departments</option>`;
        departmentsList.forEach(dep => {
            const option = document.createElement("option");
            option.value = dep.name;
            option.textContent = dep.name;
            departmentFilter.appendChild(option);
        });
    }

    function renderProjects(projects) {
        projectList.innerHTML = "";
        if (projects.length === 0) {
            projectList.innerHTML = `<p class="text-muted">No projects found.</p>`;
            return;
        }
        projects.forEach(project => {
            const card = document.createElement("div");
            card.className = "proposal-card";
            card.dataset.id = project.id;
            card.dataset.department = project.department?.name?.toLowerCase() || "";
            card.dataset.name = project.name?.toLowerCase() || "";
            card.dataset.academicyear = project.academic_year?.toLowerCase() || "";
            card.innerHTML = `
                <h4>${project.name || "N/A"}</h4>
                <p><strong>Field:</strong> ${project.field || "N/A"}</p>
                ${IS_SUPER_COORD ? `<p><strong>Department:</strong> ${project.department?.name || "N/A"}</p>` : ""}
                <p><strong>Academic Year:</strong> ${project.academic_year || "N/A"}</p>
                <div class="project-card-buttons">
                    <button class="btn btn-primary view-btn">🔍 View Details</button>
                </div>
            `;
            projectList.appendChild(card);
        });
        setTimeout(attachViewButtons, 0);
    }

    function attachViewButtons() {
        document.querySelectorAll(".view-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const card = btn.closest(".proposal-card");
                const projectId = card.dataset.id;
                currentProjectId = projectId;

                try {
                    const res = await fetch(`${window.location.origin}/api/project/project/track/${projectId}/`);
                    const detail = await res.json();
                    const projectData = detail.project || {};
                    const members = detail.members || [];
                    const tasks = detail.tasks || [];
                    const logs = detail.logs || [];
                    const feedbacks = detail.feedbacks || [];
                    const completionStatus = detail.completion_status;

                    modalTitle.textContent = projectData.name || "N/A";
                    modalField.textContent = projectData.field || "N/A";
                    modalDescription.textContent = projectData.description || "No description provided.";
                    modalTeamCount.textContent = projectData.team_member_count || "0";

                    const students = detail.students || [];
                    modalTeamMembers.textContent = students.length > 0 ? students.map(s => s.username).join(", ") : "N/A";

                    modalSupervisor.textContent = members.find(m => m.role.toLowerCase() === "supervisor")?.username || "N/A";
                    modalReader.textContent = members.find(m => m.role.toLowerCase() === "reader")?.username || "N/A";
                    modalJudges.textContent = members.filter(m => m.role.toLowerCase() === "judge").map(j => j.username).join(", ") || "N/A";

                    modalFile.innerHTML = projectData.file ? `<a href="${projectData.file}" target="_blank">📄 View File</a>` : "No file attached.";
                    modalCompletion.textContent = completionStatus !== null ? completionStatus : "N/A";

                    tasksList.innerHTML = tasks.length ? "" : "<p>No tasks available.</p>";
                    tasks.forEach(task => {
                        const taskCard = document.createElement("div");
                        taskCard.className = "task-card";
                        taskCard.innerHTML = `
                            <p><strong>Task:</strong> ${task.name}</p>
                            <p><strong>Goals:</strong> ${task.goals || "N/A"}</p>
                            <p><strong>Outputs:</strong> ${task.outputs || "N/A"}</p>
                            <p><strong>Status:</strong> ${task.task_status}</p>
                            <p><strong>Assigned To:</strong> ${task.assign_to || "N/A"}</p>
                            <p><strong>Deadline (days):</strong> ${task.deadline_days || "N/A"}</p>
                            ${task.deliverable_file ? `<p><a href="${task.deliverable_file}" target="_blank">📎 Deliverable</a></p>` : ""}
                        `;
                        tasksList.appendChild(taskCard);
                    });

                    logsList.innerHTML = logs.length ? "" : "<p>No logs available yet.</p>";
                    logs.forEach(log => {
                        const logItem = document.createElement("div");
                        logItem.className = "log-entry";
                        logItem.innerHTML = `
                            <p><strong>${log.timestamp}:</strong> ${log.user} - ${log.message}</p>
                            ${log.attachment ? `<p><a href="${log.attachment}" target="_blank">📎 Attachment</a></p>` : ""}
                        `;
                        logsList.appendChild(logItem);
                    });

                    feedbackInput.value = feedbacks.length > 0 ? feedbacks[0].feedback_text : "";

                    modal.classList.add("show");
                    modal.classList.remove("hidden");
                } catch (err) {
                    console.error("Failed to fetch project details:", err);
                }
            });
        });
    }

    submitFeedbackBtn?.addEventListener("click", async () => {
        const feedbackText = feedbackInput.value.trim();
        if (!feedbackText) {
            feedbackMessage.textContent = "⚠️ Please write something before submitting.";
            feedbackMessage.style.color = "red";
            return;
        }
        try {
            const res = await fetch("/api/project/feedback-exchange/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({
                    project: currentProjectId,
                    feedback_text: feedbackText,
                }),
            });
            if (res.ok) {
                feedbackMessage.textContent = "✅ Feedback submitted successfully!";
                feedbackMessage.style.color = "green";
                feedbackInput.value = "";
            } else {
                const error = await res.json();
                feedbackMessage.textContent = `❌ Failed to submit feedback: ${error.detail || "Unknown error"}`;
                feedbackMessage.style.color = "red";
            }
        } catch (err) {
            console.error("Failed to submit feedback:", err);
            feedbackMessage.textContent = "❌ Failed to submit feedback.";
            feedbackMessage.style.color = "red";
        }
    });

    function getCSRFToken() {
        const cookieValue = document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    closeBtn?.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.classList.remove("show");
    });

    function applyFilters() {
        const query = searchInput?.value?.toLowerCase() || "";
        const selectedDept = departmentFilter?.value?.toLowerCase() || "";
        document.querySelectorAll(".proposal-card").forEach(card => {
            const name = card.dataset.name;
            const academicYear = card.dataset.academicyear;
            const department = card.dataset.department;
            const matchesSearch = name.includes(query) || academicYear.includes(query);
            const matchesDepartment = !selectedDept || department.includes(selectedDept);
            card.style.display = matchesSearch && matchesDepartment ? "block" : "none";
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", applyFilters);
    }
    if (departmentFilter) {
        departmentFilter.addEventListener("change", applyFilters);
    }

    loadProjects();
});
