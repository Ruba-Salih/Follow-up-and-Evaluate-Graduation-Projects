document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("coord-modal");
    const closeBtn = document.querySelector(".close-btn");

    document.querySelectorAll(".view-btn").forEach(button => {
        button.addEventListener("click", async () => {
            const proposalId = button.dataset.id;
            const response = await fetch(`/api/project/proposals/${proposalId}/`);
            const data = await response.json();

            document.getElementById("modal-title-text").textContent = data.title;
            document.getElementById("modal-field").textContent = data.field;
            document.getElementById("modal-description").textContent = data.description;
            document.getElementById("modal-team-count").textContent = data.team_member_count;
            document.getElementById("modal-team-members").textContent = (data.team_members || []).map(tm => tm.username).join(", ") || "None";
            document.getElementById("modal-comment").textContent = data.additional_comment || "None";

            if (data.attached_file) {
                const fileLink = `<a href="${data.attached_file}" target="_blank">Download File</a>`;
                document.getElementById("modal-file").innerHTML = fileLink;
            } else {
                document.getElementById("modal-file").textContent = "None";
            }

            modal.classList.remove("hidden");
            modal.style.display = "flex";
        });
    });

    closeBtn?.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.style.display = "none";
    });

    document.getElementById("accept-btn").addEventListener("click", () => handleStatusUpdate("accepted"));
    document.getElementById("edit-btn").addEventListener("click", () => handleStatusUpdate("pending"));
    document.getElementById("reject-btn").addEventListener("click", () => handleStatusUpdate("rejected"));

    async function handleStatusUpdate(status) {
        const proposalId = document.querySelector(".view-btn[data-id]").dataset.id;
        const isSuper = document.getElementById("feedback-text") !== null;
        const url = `/api/project/proposals/${proposalId}/`;
        const body = isSuper ? {
            coordinator_status: status,
            teacher_status: status
        } : {
            coordinator_status: status
        };

        const response = await fetch(url, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify(body)
        });

        if (response.ok) {
            if (isSuper) {
                const feedback = document.getElementById("feedback-text").value;
                if (feedback.trim()) {
                    await fetch("/api/project/feedback/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                        },
                        body: JSON.stringify({
                            proposal: proposalId,
                            feedback_text: feedback
                        })
                    });
                }
            }
            location.reload();
        } else {
            alert("Failed to update status.");
        }
    }
});
