document.addEventListener("DOMContentLoaded", async () => {
    const BASE_URL = "/api/project/project/track";
    const i18n = document.getElementById("i18n-js-labels")?.dataset || {};

    const projectTitle = document.getElementById("project-title");
    const projectField = document.getElementById("project-field");
    const projectSupervisor = document.getElementById("project-supervisor");
    const projectDuration = document.getElementById("project-duration");
    const projectStatus = document.getElementById("project-status");
    const saveStatusBtn = document.getElementById("save-status-btn");

    const goalList = document.getElementById("goal-list");
    const addGoalBtn = document.getElementById("add-goal-btn");
    const newGoalText = document.getElementById("new-goal-text");
    const newGoalDuration = document.getElementById("new-goal-duration");

    const reportForm = document.getElementById("weekly-report-form");
    const progressForm = document.getElementById("progress-form");


    let projectId = null;

    function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

    let taskCounter = 0;
    let tasks = [];
    let students = [];
    
    function closeModal(selector) {
        const modal = document.querySelector(selector);
        if (modal) {
            modal.classList.remove("show");
        }
    }
    document.querySelectorAll(".close-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".modal");
            if (modal) {
                modal.classList.remove("show");
            }
        });
    });

const researchBtn = document.getElementById("research-btn");
const researchModal = document.getElementById("researchUploadModal");
const researchFeedbackList = document.getElementById("research-feedback-list");
const researchFeedbackForm = document.getElementById("research-feedback-form");
const researchUploadForm = document.getElementById("research-upload-form");

researchUploadForm?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = researchUploadForm.querySelector("input[type='file']");
    const file = fileInput.files[0];

    if (!file) {
        alert("⚠️ Please select a file to upload.");
        return;
    }

    const formData = new FormData();
    formData.append("research_file", file);

    const res = await fetch(`/api/project/projects/${projectId}/`, {
        method: "PUT",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: formData
    });

    if (res.ok) {
        alert("✅ Research file uploaded successfully!");
        researchModal.classList.remove("show");
        window.location.reload();
    } else {
        alert("❌ Failed to upload research file.");
    }
});

researchBtn?.addEventListener("click", async () => {
    researchModal.classList.add("show");

    projectId = researchBtn.dataset.projectId || projectId; // se

    const res = await fetch(`/api/project/project/track/${projectId}/`);
    const data = await res.json();

    const researchFileContainer = document.getElementById("research-file-link");
    if (researchFileContainer) {
        if (data.research_file) {
            researchFileContainer.innerHTML = `
                <p><strong>📄 Existing File:</strong> 
                    <a href="${data.research_file}" target="_blank">View Uploaded File</a>
                </p>`;
        } else {
            researchFileContainer.innerHTML = "<p>No research file uploaded yet.</p>";
        }
    }

    // 🔁 Show feedbacks (from teachers/committee only)
    researchFeedbackList.innerHTML = "";
    const allowedRoles = ["Reader", "Judgement Committee"];
    const visibleFeedbacks = (data.feedbacks || []).filter(fb => allowedRoles.includes(fb.sender_role));

    if (visibleFeedbacks.length > 0) {
        visibleFeedbacks.forEach(fb => {
            const fbDiv = document.createElement("div");
            fbDiv.classList.add("feedback-entry");
            fbDiv.innerHTML = `
                <p><strong>${fb.sender} (${fb.sender_role}):</strong> ${fb.feedback_text}</p>
                <p class="timestamp">🕒 ${fb.created_at}</p>
                ${fb.feedback_file ? `<p><a href="${fb.feedback_file}" target="_blank">📎 File</a></p>` : ""}
                <hr>
            `;
            researchFeedbackList.appendChild(fbDiv);
        });
    } else {
        researchFeedbackList.innerHTML = "<p>No feedback yet.</p>";
    }

    // ❌ Hide feedback form if user is student
    const isStudent = data.role === "Student";
    const feedbackForm = document.getElementById("research-feedback-form");
    if (feedbackForm) {
        feedbackForm.style.display = isStudent ? "none" : "block";
    }
});

researchFeedbackForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const comment = document.getElementById("research-feedback-text")?.value.trim();
    const file = document.getElementById("research-feedback-file")?.files[0];

    if (!comment && !file) {
        alert("Please write feedback or upload a file.");
        return;
    }

    const formData = new FormData();
    formData.append("project", projectId);
    formData.append("feedback_text", comment);
    if (file) {
        formData.append("feedback_file", file);
    }

    const res = await fetch(`/api/project/feedback/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: formData
    });

    if (res.ok) {
        alert("✅ Feedback submitted!");
        researchModal.classList.remove("show");
        window.location.reload();
    } else {
        alert("❌ Failed to submit feedback.");
    }
});

    
    async function loadProject() {
        try {
            const response = await fetch(`${BASE_URL}/`);
            if (!response.ok) throw new Error("Failed to fetch project.");
            const data = await response.json();

            const studentList = document.getElementById("project-students");
            if (studentList && data.students) {
                studentList.innerHTML = "";
                data.students.forEach(s => {
                    const fullName = `${s.first_name || ""} ${s.last_name || ""}`.trim();
            studentList.innerHTML += `
            <li>
                ${s.first_name} ${s.last_name} | 📧 ${s.email} | ☎️ ${s.phone || "N/A"}
            </li>`;
                });
            }
            
            if (data.projects && data.projects.length > 0) {
                const project = data.projects[0];
                projectId = project.id;

                if (projectTitle) projectTitle.textContent = project.name || "Unnamed Project";
                if (projectField) projectField.textContent = project.field || "—";
                if (projectSupervisor) projectSupervisor.textContent = data.supervisor_name || "—";
                if (projectDuration) projectDuration.textContent = project.duration ? `${project.duration} months` : "N/A";
                // Fetch the full project using the projectId to get the completion_status
                const detailedRes = await fetch(`${BASE_URL}/${project.id}/`);
                if (detailedRes.ok) {
                    const detailedData = await detailedRes.json();

                    const teacherList = document.getElementById("project-teachers");
                    if (teacherList && detailedData.project?.members) {
                        teacherList.innerHTML = "";
                        detailedData.project.members.forEach(m => {
                            teacherList.innerHTML += `
                                <li>
                                    <strong>${m.role}</strong>: ${m.first_name} ${m.last_name} |
                                    📧 ${m.email} | ☎️ ${m.phone_number || "N/A"}
                                </li>`;
                        });
                    }

                    const percent = detailedData.completion_status ?? 0;

                    if (projectStatus) projectStatus.value = percent;
                    const statusText = document.getElementById("project-status-text");
                    const progressBar = document.getElementById("completion-bar");
                    if (statusText) statusText.textContent = `${percent}%`;
                    if (progressBar) progressBar.style.width = `${percent}%`;

                } else {
                    console.warn("⚠️ Could not fetch completion_status.");
                }
                students = data.students || [];

                await loadGoals();
                await loadReports();
                await loadTasks();
                
            }
             else {
                    document.querySelector(".container").innerHTML = `
                        <div class="no-project-message">
                            <h3>😢 You are not assigned to any project yet.</h3>
                            <p>Please contact your coordinator or check back later.</p>
                        </div>
                    `;
                }
        } catch (error) {
            console.error("Error loading project:", error);
        }
    }

    async function loadReports() {
        try {
            const res = await fetch(`${BASE_URL}/${projectId}/`);
            if (!res.ok) throw new Error("Failed to load reports.");
            const data = await res.json();

        } catch (error) {
            console.error("Error loading reports:", error);
        }
    }

    async function loadGoals() {
        if (!projectId) return;
        try {
            const res = await fetch(`${BASE_URL}/${projectId}/`);
            if (!res.ok) throw new Error("Failed to load goals.");
            const data = await res.json();
    
            goalList.innerHTML = "";
    
            (data.goals || []).forEach(goal => {
                const goalDiv = document.createElement("div");
                goalDiv.className = "goal-entry";
                goalDiv.innerHTML = `
                    <strong>Goal:</strong> <input type="text" value="${goal.goal}" data-goal-id="${goal.id}" class="form-control goal-text" style="margin-bottom:5px;">
                    <strong>Duration:</strong> <input type="number" value="${goal.duration || ''}" data-goal-id="${goal.id}" class="form-control goal-duration" style="margin-bottom:10px;">
                    <button class="btn btn-edit save-goal-btn btn-edit" data-goal-id="${goal.id}" style="margin-right:5px;">💾 Save</button>
                    <button class="btn btn-delete  delete-goal-btn" data-goal-id="${goal.id}">🗑️ Delete</button>
                `;
                goalList.appendChild(goalDiv);

                const goalSelect = document.getElementById("selected-goal-for-task");
                if (goalSelect) {
                    goalSelect.innerHTML = '<option value="">-- Select Goal --</option>';
                    (data.goals || []).forEach(goal => {
                        goalSelect.innerHTML += `<option value="${goal.id}">${goal.goal}</option>`;
                    });
                }

                const progressGoalSelect = document.getElementById("goal-progress-filter");
                if (progressGoalSelect) {
                    progressGoalSelect.innerHTML = '<option value="">-- Filter by Goal --</option>';
                    (data.goals || []).forEach(goal => {
                        progressGoalSelect.innerHTML += `<option value="${goal.id}">${goal.goal}</option>`;
                    });
                }
            });
    
            // Attach event listeners
            document.querySelectorAll(".save-goal-btn").forEach(btn => {
                btn.addEventListener("click", async function () {
                    const id = this.getAttribute("data-goal-id");
                    const goalTextInput = document.querySelector(`.goal-text[data-goal-id="${id}"]`);
                    const goalDurationInput = document.querySelector(`.goal-duration[data-goal-id="${id}"]`);
    
                    const formData = new FormData();
                    formData.append("goal_id", id);
                    formData.append("goal_text", goalTextInput.value);
                    formData.append("duration", goalDurationInput.value);
    
                    try {
                        const res = await fetch(`${BASE_URL}/${projectId}/`, {
                            method: "PUT",
                            headers: {
                                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                            },
                            body: formData
                        });
    
                        if (res.ok) {
                            alert("✅ Goal updated successfully!");
                            await loadGoals();
                        } else {
                            alert("⚠️ Failed to update goal.");
                        }
                    } catch (error) {
                        console.error("Update goal error:", error);
                    }
                });
            });
    
            document.querySelectorAll(".delete-goal-btn").forEach(btn => {
                btn.addEventListener("click", async function () {
                    if (!confirm("Are you sure you want to delete this goal?")) return;
    
                    const id = this.getAttribute("data-goal-id");
                    const formData = new FormData();
                    formData.append("goal_id", id);
    
                    try {
                        const res = await fetch(`${BASE_URL}/${projectId}/`, {
                            method: "DELETE",
                            headers: {
                                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                            },
                            body: formData
                        });
    
                        if (res.ok) {
                            alert("✅ Goal deleted successfully!");
                            await loadGoals();
                        } else {
                            alert("⚠️ Failed to delete goal.");
                        }
                    } catch (error) {
                        console.error("Delete goal error:", error);
                    }
                });
            });
    
        } catch (error) {
            console.error("Error loading goals:", error);
        }
    }
    
    async function loadTasks() {
        try {
            const res = await fetch(`${BASE_URL}/${projectId}/`);
            if (!res.ok) throw new Error("Failed to load tasks.");
            const data = await res.json();

            tasks = data.tasks || [];
            loadProgressTasks();
        } catch (error) {
            console.error("Error loading tasks:", error);
        }
    }

    const goalProgressSelect = document.getElementById("goal-progress-filter");

    goalProgressSelect?.addEventListener("change", () => {
        const selectedGoalId = goalProgressSelect.value;
        const filtered = tasks.filter(t => String(t.goal) === selectedGoalId);

        loadProgressTasks(filtered);
    });

    function loadProgressTasks(filteredTasks = null) {
        const progressTaskEntries = document.getElementById("progress-task-entries");
        progressTaskEntries.innerHTML = "";
    
        const taskList = filteredTasks ?? tasks;
        taskList.filter(task => task.task_status !== "done").forEach((task, index) => {
            const taskDiv = document.createElement("div");
            taskDiv.className = "progress-task-entry";
            taskDiv.innerHTML = `
                <h5>Task ${index + 1}</h5>
                <input type="hidden" name="task_id_${task.id}" value="${task.id}">
                <label>Task Name:</label>
                <input type="text" class="form-control" value="${task.name}" readonly>
                <label>Deliverable (Text):</label>
                <input type="text" class="form-control" name="deliverable_text_${task.id}">
                <label>Or Upload Deliverable File:</label>
                <input type="file" class="form-control" name="deliverable_file_${task.id}">
                <label>Task Status:</label>
                <select name="task_status_${task.id}" class="form-control">
                    <option value="to do" ${task.task_status === "to do" ? "selected" : ""}>To Do</option>
                    <option value="in progress" ${task.task_status === "in progress" ? "selected" : ""}>In Progress</option>
                    <option value="done" ${task.task_status === "done" ? "selected" : ""}>Done</option>
                </select>
                <hr>
            `;
            progressTaskEntries.appendChild(taskDiv);
        });
    }


    addGoalBtn?.addEventListener("click", async () => {
    if (!projectId) {
        console.warn("🚫 Project ID not set. Cannot add goal.");
        return;
    }

    const goalText = newGoalText.value.trim();
    const goalDuration = newGoalDuration.value.trim();

    if (!goalText) {
        showAlert("⚠️ Please enter a goal text.", 'warning');
        return;
    }

    const formData = new FormData();
    formData.append("goal_text", goalText);
    formData.append("duration", goalDuration);

    console.log("🚀 Submitting new goal:", { goalText, goalDuration });

    try {
        const res = await fetch(`${BASE_URL}/${projectId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value,
            },
            body: formData
        });

        if (res.ok) {
            alert("✅ Goal added successfully!");
            newGoalText.value = "";
            newGoalDuration.value = "";
            await loadGoals();
        } else {
            const errorText = await res.text();
            console.error("❌ Goal add failed:", res.status, errorText);
            alert("⚠️ Failed to add goal.");
        }
    } catch (error) {
        console.error("💥 Add goal error:", error);
        alert("⚠️ Error submitting goal.");
    }
});


    document.querySelectorAll(".action-btn").forEach(btn => {
        btn.addEventListener("click", async function() {
            const target = this.getAttribute("data-target");
            const modal = document.querySelector(target);

            if (modal) {
                modal.classList.add("show");

                if (target === "#goalsModal") {
                    await loadGoals();
                }                

                if (target === "#weeklyReportModal") {
                    const addTaskBtn = document.getElementById("add-task-btn");
                    const taskEntries = document.getElementById("task-entries");

                    addTaskBtn?.removeEventListener("click", handleAddTask);
                    addTaskBtn?.addEventListener("click", handleAddTask);
                }
            }
        });
    });

    // Edit Project Info Modal logic
const editProjectForm = document.getElementById("edit-project-form");
const editProjectModal = document.getElementById("editProjectModal");

document.querySelector("[data-target='#editProjectModal']")?.addEventListener("click", () => {
    if (projectTitle) document.getElementById("edit-project-name").value = projectTitle.textContent;
    if (projectField) document.getElementById("edit-project-field").value = projectField.textContent;
    editProjectModal.classList.add("show");
});

editProjectForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const newName = document.getElementById("edit-project-name").value.trim();
    const newField = document.getElementById("edit-project-field").value.trim();

    try {
        const res = await fetch(`/api/project/projects/${projectId}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                name: newName,
                field: newField
            })
        });

        if (!res.ok) throw new Error("Failed to update project info.");

        const data = await res.json();

        projectTitle.textContent = data.name || newName;
        projectField.textContent = data.field || newField;

        editProjectModal.classList.remove("show");
        alert("✅ Project info updated successfully!");
    } catch (err) {
        alert("❌ Could not update project.");
        console.error(err);
    }
});


    function handleAddTask() {
        const goalSelect = document.getElementById("selected-goal-for-task");
        const selectedGoalId = goalSelect?.value;
        const selectedGoalText = goalSelect?.options[goalSelect.selectedIndex]?.text;
    
        if (!selectedGoalId) {
            alert("⚠️ Please select a goal first.");
            return;
        }
    
        taskCounter++;
        const newTask = document.createElement("div");
        newTask.className = "task-entry";
        newTask.innerHTML = `
            <input type="hidden" name="goal_id_${taskCounter}" value="${selectedGoalId}">
            <h5>Task ${taskCounter} (Goal: ${selectedGoalText})</h5>
    
            <label>Task Name:</label>
            <input type="text" name="task_name_${taskCounter}" class="form-control" placeholder="Task Name...">
    
            <label>Task Goal:</label>
            <input type="text" name="task_goal_${taskCounter}" class="form-control" placeholder="Write task goal...">

            <label>Expected Outputs:</label>
            <textarea name="outputs_${taskCounter}" class="form-control" rows="2" placeholder="Expected outputs..."></textarea>
    
            <label>Assign To:</label>
            <select name="assign_to_${taskCounter}" class="form-control">
                ${students.map(s => {
                    const fullName = `${s.first_name || ""} ${s.last_name || ""}`.trim();
                    return `<option value="${s.id}">${fullName}</option>`;
                }).join('')}
            </select>
    
            <label>Deadline (in days):</label>
            <input type="number" name="deadline_days_${taskCounter}" class="form-control" placeholder="Deadline...">
    
            <label>Task Status:</label>
            <select name="task_status_${taskCounter}" class="form-control">
                <option value="to do">To Do</option>
                <option value="in progress">In Progress</option>
                <option value="done">Done</option>
            </select>
    
            <hr>
        `;
        document.getElementById("task-entries").appendChild(newTask);
    }
    

    reportForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const taskEntries = document.querySelectorAll("#task-entries .task-entry");
        let tasksCreated = 0;
        let tasksFailed = 0;

        for (const taskDiv of taskEntries) {
            const taskName = taskDiv.querySelector(`[name^="task_name_"]`)?.value;
            const taskGoalText = taskDiv.querySelector(`[name^="task_goal_"]`)?.value;
            const outputs = taskDiv.querySelector(`[name^="outputs_"]`)?.value;
            const assignTo = taskDiv.querySelector(`[name^="assign_to_"]`)?.value;
            const deadlineDays = taskDiv.querySelector(`[name^="deadline_days_"]`)?.value;
            const taskStatus = taskDiv.querySelector(`[name^="task_status_"]`)?.value;

            if (!taskName || !taskGoalText || !assignTo) continue;

            const formData = new FormData();
            formData.append("goal_id", taskDiv.querySelector(`[name^="goal_id_"]`).value);
            formData.append("task_name", taskName);
            formData.append("goal_text", taskGoalText);
            formData.append("outputs", outputs);
            formData.append("assign_to", assignTo);
            formData.append("deadline_days", deadlineDays);
            formData.append("task_status", taskStatus);

            try {
                const res = await fetch(`${BASE_URL}/${projectId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: formData
                });

                if (res.ok) {
                    tasksCreated++;
                } else {
                    tasksFailed++;
                }
            } catch {
                tasksFailed++;
            }
        }

        const feedbackComment = document.getElementById("report-comment")?.value.trim();
        const feedbackFileInput = document.getElementById("feedback-file");

        if (feedbackComment || (feedbackFileInput && feedbackFileInput.files.length > 0)) {
            const feedbackData = new FormData();
            feedbackData.append("feedback_text", feedbackComment);
            if (feedbackFileInput && feedbackFileInput.files.length > 0) {
                feedbackData.append("feedback_file", feedbackFileInput.files[0]);
            }

            try {
                const res = await fetch(`${BASE_URL}/${projectId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: feedbackData
                });

                if (res.ok) {
                    alert("✅ Your weekly report have been submitted successfully!");
                    window.location.reload();
                    return;
                } else {
                    alert("⚠️ Failed to submit feedback.");
                    return;
                }
            } catch {
                alert("⚠️ Error submitting feedback.");
                return;
            }
        }

        if (tasksCreated > 0) {
            alert(`✅ ${tasksCreated} task(s) submitted successfully!`);
            window.location.reload();
        } else if (tasksFailed > 0) {
            alert("⚠️ Some tasks failed to submit.");
        } else {
            alert("⚠️ Nothing was submitted.");
        }
    });

    document.getElementById("progress-form").addEventListener("submit", async (e) => {
        e.preventDefault();
    
        const taskEntries = document.querySelectorAll("#progress-task-entries .progress-task-entry");
    
        let success = 0;
        let failed = 0;
    
        for (const taskDiv of taskEntries) {
            const taskId = taskDiv.querySelector(`[name^="task_id_"]`)?.value;
            const deliverableText = taskDiv.querySelector(`[name^="deliverable_text_"]`)?.value;
            const deliverableFile = taskDiv.querySelector(`[name^="deliverable_file_"]`)?.files[0];
            const taskStatus = taskDiv.querySelector(`[name^="task_status_"]`)?.value;
    
            if (!taskId) continue; // skip if no id
    
            const formData = new FormData();
            formData.append("task_id", taskId);
            formData.append("deliverable_text", deliverableText);
            if (deliverableFile) {
                formData.append("deliverable_file", deliverableFile);
            }
            formData.append("task_status", taskStatus);
    
            try {
                const res = await fetch(`${BASE_URL}/${projectId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                    body: formData
                });
    
                if (res.ok) {
                    success++;
                } else {
                    failed++;
                }
            } catch (error) {
                console.error("Error updating task:", error);
                failed++;
            }
        }
    
        if (success > 0) {
            alert(`✅ Progress submitted successfully for task(s)!`);
            window.location.reload();
        } else if (failed > 0) {
            alert(`⚠️ Failed to submit some progress.`);
        } else {
            alert(`⚠️ No progress was submitted.`);
        }
    });    

    await loadProject();
});
