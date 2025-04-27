document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("view-modal");
    const closeBtn = document.querySelector(".close-btn");
    const feedbackTextarea = document.getElementById("feedback-text");
    const searchInput = document.getElementById("search-input");
    const statusFilter = document.getElementById("status-filter");
    const proposalList = document.getElementById("student-proposal-list");

    // 🔍 Filter Function
    function filterProposals() {
        const query = searchInput.value.toLowerCase();
        const selectedStatus = statusFilter.value;
        const cards = proposalList.querySelectorAll(".proposal-card");

        cards.forEach(card => {
            const title = card.querySelector("h4")?.textContent.toLowerCase() || "";
            const field = card.querySelector("p:nth-of-type(1)")?.textContent.toLowerCase() || "";
            const student = card.querySelector("p:nth-of-type(2)")?.textContent.toLowerCase() || "";
            const date = card.querySelector("p:nth-of-type(3)")?.textContent.toLowerCase() || "";
            const teacherStatus = card.querySelector(".status:nth-of-type(1)")?.textContent.toLowerCase() || "";
            const coordinatorStatus = card.querySelector(".status:nth-of-type(2)")?.textContent.toLowerCase() || "";

            const matchesSearch = (
                title.includes(query) ||
                field.includes(query) ||
                student.includes(query) ||
                date.includes(query)
            );

            const matchesStatus = selectedStatus === "" || 
                teacherStatus.includes(selectedStatus) || 
                coordinatorStatus.includes(selectedStatus);

            if (matchesSearch && matchesStatus) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    }

    searchInput.addEventListener("input", filterProposals);
    statusFilter.addEventListener("change", filterProposals);

    // 📄 Open Modal View
    document.querySelectorAll(".view-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const proposalId = btn.dataset.id;
            try {
                const response = await fetch(`/api/project/proposals/${proposalId}/`);
                const data = await response.json();
                if (!response.ok) {
                    alert(data.detail || "Error fetching proposal details.");
                    return;
                }

                document.getElementById("modal-title-text").textContent = data.title || '';
                document.getElementById("modal-field").textContent = data.field || '';
                document.getElementById("modal-description").textContent = data.description || '';
                document.getElementById("modal-duration").textContent = data.duration || '0';
                document.getElementById("modal-team-count").textContent = data.team_member_count || 0;

                if (data.student_memberships) {
                    const names = data.student_memberships.map(sm => sm.username).join(", ");
                    document.getElementById("modal-team-members").textContent = names || 'None';
                } else {
                    document.getElementById("modal-team-members").textContent = 'None';
                }

                document.getElementById("modal-file").innerHTML = data.attached_file ? `<a href="${data.attached_file}" target="_blank">Download</a>` : 'None';
                document.getElementById("modal-comment").textContent = data.additional_comment || 'None';

                modal.dataset.proposalId = proposalId;
                feedbackTextarea.value = "";
                modal.classList.remove("hidden");
            } catch (error) {
                console.error("Fetch error:", error);
            }
        });
    });

    closeBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
    });

    document.getElementById("accept-btn").addEventListener("click", () => updateProposalStatus("accepted"));
    document.getElementById("edit-btn").addEventListener("click", () => updateProposalStatus("pending"));
    document.getElementById("reject-btn").addEventListener("click", () => updateProposalStatus("rejected"));

    async function updateProposalStatus(status) {
        const proposalId = modal.dataset.proposalId;
        const feedback = feedbackTextarea.value.trim();

        const formData = new FormData();
        formData.append("teacher_status", status);

        if (feedback) {
            await fetch(`/api/project/feedback/`, {
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
                alert("Update failed: " + (errorData.detail || JSON.stringify(errorData)));
                return;
            }

            location.reload();
        } catch (error) {
            console.error("Update error:", error);
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
