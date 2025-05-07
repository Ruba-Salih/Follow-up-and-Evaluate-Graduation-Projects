document.addEventListener("DOMContentLoaded", () => {
    
    const filterSelect = document.getElementById("project-filter");
    const cards = document.querySelectorAll(".proposal-card");

    filterSelect.addEventListener("change", () => {
        const value = filterSelect.value;

        cards.forEach(card => {
            const status = card.dataset.status;
        
            if (value === "all" || value === status) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
        
    });

    document.querySelectorAll(".project-action-form").forEach(form => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const projectId = form.dataset.projectId;
            const action = form.dataset.action;
            const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;

            const url = `/api/project/available/${projectId}/`;
            const fetchOptions = {
                method: action === "join" ? "POST" : "DELETE",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            };

            if (action === "leave") {
                fetchOptions.body = new FormData();
                fetchOptions.body.append("project_id", projectId);
            }

            try {
                const res = await fetch(url, fetchOptions);
                const data = await res.json();

                if (res.ok) {
                    alert(`✅ ${data.detail}`);
                    window.location.reload();
                } else {
                    alert(`⚠️ ${data.detail || "Something went wrong."}`);
                }
            } catch (err) {
                console.error("❌ Error:", err);
                alert("⚠️ Network error. Please try again.");
            }
        });
    });

    // Handle view details modal
    const modal = document.getElementById("project-details-modal");
    const closeBtn = document.getElementById("close-project-modal");

    document.querySelectorAll(".view-project-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            // Fill modal fields from data attributes
            document.getElementById("modal-project-name").textContent = btn.dataset.name;
            document.getElementById("modal-project-description").textContent = btn.dataset.description || "N/A";
            document.getElementById("modal-project-field").textContent = btn.dataset.field || "N/A";
            document.getElementById("modal-project-department").textContent = btn.dataset.department || "N/A";
            document.getElementById("modal-project-team-count").textContent = btn.dataset.teamCount || "N/A";
            document.getElementById("modal-project-students").textContent = btn.dataset.students || "None";
            document.getElementById("modal-project-duration").textContent = btn.dataset.duration || "N/A";

            modal.classList.remove("hidden");
            modal.classList.add("show");
        });
    });

    // Close modal on close button click
    closeBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.classList.remove("show");
    });

    // Close modal on outside click
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.add("hidden");
            modal.classList.remove("show");
        }
    });
});
