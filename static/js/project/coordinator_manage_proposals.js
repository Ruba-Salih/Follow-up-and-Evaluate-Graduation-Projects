document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("coord-modal");
    const closeBtn = document.querySelector(".close-btn");
    const feedbackTextarea = document.getElementById("feedback-text");

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
                document.getElementById("modal-team-count").textContent = data.team_member_count || 0;
                document.getElementById("modal-team-members").textContent = (data.team_members || []).map(m => m.username).join(", ") || "None";
                document.getElementById("modal-file").innerHTML = data.attached_file
                    ? `<a href="${data.attached_file}" target="_blank">Download File</a>`
                    : 'None';
                document.getElementById("modal-comment").textContent = data.additional_comment || 'None';

                modal.dataset.proposalId = proposalId;
                if (feedbackTextarea) feedbackTextarea.value = "";

                modal.classList.remove("hidden");
                modal.style.display = "flex";
            } catch (error) {
                console.error("Fetch error:", error);
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
            alert("No proposal selected.");
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
                alert("Update failed: " + (errorData.detail || JSON.stringify(errorData)));
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
