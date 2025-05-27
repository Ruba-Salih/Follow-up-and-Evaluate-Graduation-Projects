document.addEventListener("DOMContentLoaded", async () => {
    const reportForm = document.getElementById("report-form");
    const teamStatusSection = document.getElementById("team-status-section");
    const reportDateInput = document.getElementById("report_date");
    const projectId = reportForm.dataset.projectId;
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const today = new Date().toISOString().split("T")[0];

    const reportModal = document.getElementById("reportModal");
    const openBtn = document.getElementById("openReportModal");
    const closeBtn = document.querySelector("#reportModal .close-modal");

    const detailModal = document.getElementById("reportDetailModal");
    const detailBody = document.getElementById("report-detail-body");
    const closeDetailBtn = document.querySelector("#reportDetailModal .close-modal");

    const feedbackList = document.getElementById("feedback-list");
    const feedbackForm = document.getElementById("feedback-form");
    const feedbackTextarea = document.getElementById("feedback-textarea");
    const feedbackMessage = document.getElementById("feedback-message");

    let currentReportId = null;
    reportDateInput.value = today;

    const studentIdToNameMap = {};
    await loadStudents();

    openBtn.addEventListener("click", () => {
        reportModal.classList.add("show");
        loadStudents();
    });

    closeBtn.addEventListener("click", () => {
        reportModal.classList.remove("show");
        reportForm.reset();
        teamStatusSection.innerHTML = "";
    });

    closeDetailBtn.addEventListener("click", () => {
        detailModal.classList.remove("show");
        detailBody.innerHTML = "";
        feedbackList.innerHTML = "";
        feedbackMessage.textContent = "";
        feedbackTextarea.value = "";
    });

    async function loadStudents() {
        try {
            const res = await fetch(`/api/report/students/${projectId}/`);
            if (!res.ok) throw new Error("Project not found.");
            const data = await res.json();

            teamStatusSection.innerHTML = "";
            (data.members || []).forEach(member => {
                if (member.role === "Student") {
                    const fullName = `${member.first_name || ""} ${member.last_name || ""}`.trim();
                    studentIdToNameMap[member.id] = fullName;

                    const div = document.createElement("div");
                    div.classList.add("form-group", "mb-3");
                    div.innerHTML = `
                        <label>${member.username}: ${fullName}</label>
                        <select id="status_${member.id}" class="form-control mb-1">
                            <option value="active" selected>Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                        <textarea id="note_${member.id}" class="form-control" placeholder="Add notes (optional)"></textarea>
                    `;
                    teamStatusSection.appendChild(div);
                }
            });
        } catch (err) {
            alert("❌ Failed to load student data.");
        }
    }

    reportForm.addEventListener("submit", async (e) => {
        if (!reportModal.classList.contains("show")) {
            // Prevent accidental submission from other contexts
            return;
        }
    
        e.preventDefault();
    
        const memberStatuses = [];
        document.querySelectorAll("#team-status-section .form-group").forEach(group => {
            const select = group.querySelector("select");
            const textarea = group.querySelector("textarea");
            const studentId = select.id.split("_").pop();

            memberStatuses.push({
                student_id: studentId,
                status: select.value || "active",
                notes: textarea.value || ""
            });
        });

        const payload = {
            project: projectId,
            report_date: today,
            progress: document.getElementById("progress").value,
            work_done: document.getElementById("work_done").value,
            work_remaining: document.getElementById("work_remaining").value,
            challenges: document.getElementById("challenges").value,
            member_statuses: memberStatuses
        };

        try {
            const res = await fetch("/api/report/project-reports/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                showAlert("✅ Report submitted successfully!", 'success');
                reportModal.classList.remove("show");
                location.reload();
            } else {
                const error = await res.json();
                alert("❌ Error submitting report:\n" + JSON.stringify(error, null, 2));
            }
        } catch (err) {
            alert("❌ Failed to submit the report.");
        }
    });

    document.querySelectorAll(".btn-delete").forEach(button => {
        button.addEventListener("click", async () => {
            const reportId = button.dataset.reportId;
            const confirmDelete = confirmAction("Are you sure you want to delete this report?");
            if (!confirmDelete) return;

            try {
                const res = await fetch(`/api/report/project-reports/${reportId}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": csrfToken
                    }
                });

                if (res.status === 204) {
                    showAlert("✅ Report deleted successfully.", 'success');
                    location.reload();
                } else {
                    const error = await res.json();
                    alert("❌ Failed to delete report:\n" + JSON.stringify(error, null, 2));
                }
            } catch (err) {
                alert("❌ Error occurred while deleting the report.");
            }
        });
    });

    async function loadFeedbackThread(currentReportId) {
    console.log("🔍 Loading feedback for report:", currentReportId);
    try {
        const res = await fetch(`/api/project/feedback/?report_id=${currentReportId}`);
        if (!res.ok) throw new Error("Failed to load feedback.");
        const feedbackData = await res.json();

        feedbackList.innerHTML = "";

        if (feedbackData.length === 0) {
            feedbackList.innerHTML = "<p class='text-muted'>No feedback yet.</p>";
            return;
        }

        feedbackData.forEach(fb => {
            const reply = fb.reply ? `
                <div class="mt-2 p-2 bg-light border-start border-success ps-3">
                    <strong>↪️ Reply:</strong> ${fb.reply.message}
                    <br><small class="text-muted">${new Date(fb.reply.created_at).toLocaleString()}</small>
                </div>
            ` : "";

            const card = `
                <div class="mb-3 p-3 border rounded">
                    <strong>👤 ${fb.sender_name}</strong><br>
                    <span>${fb.message}</span><br>
                    <small class="text-muted">${new Date(fb.created_at).toLocaleString()}</small>
                    ${reply}
                </div>
            `;
            feedbackList.insertAdjacentHTML("beforeend", card);
        });
    } catch (err) {
        console.error("❌ Error loading feedback:", err);
        feedbackList.innerHTML = "<p class='text-danger'>Error loading feedback thread.</p>";
    }
}


    if (feedbackForm) {
        feedbackForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    e.stopPropagation(); 
    feedbackMessage.textContent = "";

    const message = feedbackTextarea.value.trim();
    if (!message) return;

    if (!currentReportId) {
        console.error("❌ No report selected for feedback.");
        feedbackMessage.textContent = "❌ No report selected. Please open a report first.";
        return;
    }

    console.log("📤 Submitting feedback for report:", currentReportId, "Message:", message);

    const res = await fetch("/api/project/feedback/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            report: currentReportId,
            
            feedback_text: message
        })
    });

    if (res.ok) {
        feedbackTextarea.value = "";
        feedbackMessage.textContent = "✅ Feedback sent.";
        await loadFeedbackThread(currentReportId);
    } else {
        const error = await res.json();
        feedbackMessage.textContent = "❌ " + (error.detail || "Failed to send.");
        console.error("❌ Error sending feedback:", error);
    }
});

    }

    document.querySelectorAll(".btn-view").forEach(button => {
        button.addEventListener("click", async () => {
            const reportId = button.dataset.reportId;
            try {
                const res = await fetch(`/api/report/project-reports/${reportId}/`);
                const data = await res.json();

                detailBody.innerHTML = `
                    <p><strong> Progress:</strong> ${data.progress}</p>
                    <p><strong> Work Done:</strong> ${data.work_done}</p>
                    <p><strong> Work Remaining:</strong> ${data.work_remaining}</p>
                    <p><strong> Challenges:</strong> ${data.challenges}</p>
                    <p><strong> Date:</strong> ${data.report_date}</p>
                    <hr>
                    <h5>👥 Team Member Statuses:</h5>
                    ${data.member_statuses.map(status => `
                        <div style="margin-bottom: 10px;">
                            <strong>👤 Student Name:</strong> ${studentIdToNameMap[status.student_id] || "Unknown"}<br>
                            <strong>Status:</strong> ${status.status}<br>
                            <strong>Notes:</strong> ${status.notes || "—"}
                        </div>
                    `).join("")}
                `;

                // Show modal & load thread
                detailModal.classList.add("show");
                currentReportId = reportId;
                loadFeedbackThread(currentReportId);
            } catch (err) {
                alert("❌ Failed to load report details.");
            }
        });
    });
});
