document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("coord-modal");
    const closeBtn = document.querySelector(".close-btn");
    const feedbackTextarea = document.getElementById("feedback-text");

    const searchInput = document.getElementById("search-input");
    const statusFilter = document.getElementById("status-filter");
    const proposalList = document.getElementById("coordinator-proposal-list");

    function filterProposals() {
        const query = searchInput?.value.toLowerCase() || "";
        const selectedStatus = statusFilter?.value.toLowerCase() || "";
        const cards = proposalList.querySelectorAll(".proposal-card");

        cards.forEach(card => {
            const title = card.querySelector("h4")?.textContent.toLowerCase() || "";
            const field = card.querySelector("p:nth-of-type(1)")?.textContent.toLowerCase() || "";
            const submittedBy = card.querySelector("p:nth-of-type(2)")?.textContent.toLowerCase() || "";
            const date = card.querySelector("p:nth-of-type(3)")?.textContent.toLowerCase() || "";

            const statuses = card.querySelectorAll(".status");
            let teacherStatus = "", coordinatorStatus = "";

            if (statuses.length > 0) teacherStatus = statuses[0].classList[1] || "";
            if (statuses.length > 1) coordinatorStatus = statuses[1].classList[1] || "";

            const matchesSearch = (
                title.includes(query) ||
                field.includes(query) ||
                submittedBy.includes(query) ||
                date.includes(query)
            );

            const matchesStatus = selectedStatus === "" ||
                teacherStatus.includes(selectedStatus) ||
                coordinatorStatus.includes(selectedStatus);

            card.style.display = matchesSearch && matchesStatus ? "block" : "none";
        });
    }

    searchInput?.addEventListener("input", filterProposals);
    statusFilter?.addEventListener("change", filterProposals);

    document.querySelectorAll(".view-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const proposalId = btn.dataset.id;
            try {
                const response = await fetch(`/api/project/proposals/${proposalId}/`);
                const data = await response.json();

                if (!response.ok) {
                    showAlert((data.detail || "Error fetching proposal details."), 'error');
                    return;
                }

                document.getElementById("modal-title-text").textContent = data.title || '';
                document.getElementById("modal-field").textContent = data.field || '';
                document.getElementById("modal-description").textContent = data.description || '';
                document.getElementById("modal-team-count").textContent = data.team_member_count || 0;

                const team = data.student_memberships || [];
                const alreadyInTeam = team.some(m => m.username === data.submitted_by.username);
                if (
                    data.submitted_by &&
                    !alreadyInTeam &&
                    (data.submitted_by.first_name || data.submitted_by.last_name || data.submitted_by.username)
                ) {
                    team.unshift({
                        first_name: data.submitted_by.first_name || "",
                        last_name: data.submitted_by.last_name || "",
                        username: data.submitted_by.username || "",
                        role: "Submitter"
                    });
                }

                const teamMembersSpan = document.getElementById("modal-team-members");
                if (teamMembersSpan) {
                    teamMembersSpan.textContent = team.map(m => {
                        const fullName = [m.first_name, m.last_name].filter(Boolean).join(" ") || m.username;
                        return `${fullName}${m.role ? ` (${m.role})` : ""}`;
                    }).join(", ") || "None";
                }

                const membersSpan = document.getElementById("modal-members");
                if (data.members && membersSpan) {
                    const list = data.members.map(m => `${m.name} (${m.role})`);
                    membersSpan.textContent = list.join(", ") || "None";
                }

                const roleSpan = document.getElementById("modal-teacher-role");
                if (roleSpan) {
                    roleSpan.textContent = data.teacher_role || "None";
                }

                document.getElementById("modal-file").innerHTML = data.attached_file
                    ? `<a href="${data.attached_file}" target="_blank">Download File</a>`
                    : 'None';

                document.getElementById("modal-comment").textContent = data.additional_comment || 'None';

                // 💬 Load and render feedback thread
                const feedbackThread = document.getElementById("feedback-thread");
                feedbackThread.innerHTML = "<p>Loading feedback...</p>";

                try {
                    const feedbackRes = await fetch(`/api/project/feedback/?proposal=${proposalId}`);
                    const feedbackData = await feedbackRes.json();

                    if (Array.isArray(feedbackData) && feedbackData.length > 0) {
                        feedbackThread.innerHTML = feedbackData.map(fb => {
                            const sender = fb.sender_name || "Unknown";
                            const created = new Date(fb.created_at).toLocaleString();
                            const message = fb.message || "";

                            return `
                                <div class="feedback-item" style="margin-bottom: 10px;">
                                    <p><strong>${sender}</strong> <em>${created}</em></p>
                                    <p>${message}</p>
                                    <hr>
                                </div>
                            `;
                        }).join("");
                    } else {
                        feedbackThread.innerHTML = "<p>No feedback yet.</p>";
                    }
                } catch (err) {
                    console.error("❌ Error loading feedback:", err);
                    feedbackThread.innerHTML = "<p>⚠️ Failed to load feedback.</p>";
                }

                modal.dataset.proposalId = proposalId;
                if (feedbackTextarea) feedbackTextarea.value = "";

                modal.classList.remove("hidden");
                modal.style.display = "flex";
            } catch (error) {
                console.error("error:", error);
            }
        });
    });

    closeBtn?.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.style.display = "none";
    });

    document.getElementById("accept-btn").addEventListener("click", () => updateStatus("accepted"));
    document.getElementById("edit-btn").addEventListener("click", () => updateStatus("pending"));
    document.getElementById("reject-btn").addEventListener("click", () => updateStatus("rejected"));

    async function updateStatus(status) {
        const proposalId = modal.dataset.proposalId;
        if (!proposalId) {
            showAlert("No proposal selected.", 'warning');
            return;
        }

        const feedback = feedbackTextarea ? feedbackTextarea.value.trim() : "";

        const formData = new FormData();
        formData.append("coordinator_status", status);
        if (feedbackTextarea) formData.append("teacher_status", status);

        try {
            const response = await fetch(`/api/project/proposals/${proposalId}/`, {
                method: "PUT",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                showAlert(("Update failed: " + (errorData.detail || JSON.stringify(errorData))), 'error');
                return;
            }

            if (feedback) {
                await fetch("/api/project/feedback/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({
                        proposal: proposalId,
                        feedback_text: feedback
                    })
                });
            }

            location.reload();
        } catch (error) {
            console.error("Status update error:", error);
        }
    }

    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split("=");
            if (key === name) return decodeURIComponent(value);
        }
        return "";
    }
});
