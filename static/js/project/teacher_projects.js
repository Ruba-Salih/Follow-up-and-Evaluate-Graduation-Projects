document.addEventListener("DOMContentLoaded", () => {


    const searchInput = document.getElementById("search-input");
    const roleFilter = document.getElementById("role-filter");
    const projectCards = document.querySelectorAll(".project-card");

    function applyFilters() {
        const query = searchInput.value.toLowerCase();
        const role = roleFilter.value.toLowerCase();

        projectCards.forEach(card => {
            const name = card.dataset.name;
            const myRole = card.dataset.role;

            const matchesName = name.includes(query);
            const matchesRole = role === "" || myRole.includes(role);

            card.style.display = (matchesName && matchesRole) ? "" : "none";

        });
    }

    searchInput.addEventListener("input", applyFilters);
    roleFilter.addEventListener("change", applyFilters);

    // Handle "View" button click - redirect to tracking page
    document.querySelectorAll(".view-project-btn").forEach(button => {
        button.addEventListener("click", () => {
            const projectId = button.dataset.projectId;
            if (projectId) {
                window.location.href = `/track/project/${projectId}/`;
            }
        });
    });

    // Handle "Leave" form submission
    document.querySelectorAll(".project-leave-form").forEach(form => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!confirm("Are you sure you want to leave this project?")) return;

            const projectId = form.dataset.projectId;
            const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;

            try {
                const response = await fetch(`/api/project/available/${projectId}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": csrfToken
                    }
                });

                const data = await response.json();
                if (response.ok) {
                    alert("✅ You have been removed from the project.");
                    location.reload();
                } else {
                    alert(`⚠️ ${data.detail || "Failed to remove you from the project."}`);
                }

            } catch (error) {
                console.error("❌ Error:", error);
                alert("⚠️ Network error. Please try again.");
            }
        });
    });
});
