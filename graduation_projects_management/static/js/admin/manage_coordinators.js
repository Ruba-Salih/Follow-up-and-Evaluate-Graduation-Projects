document.addEventListener("DOMContentLoaded", function () {
    const BASE_URL = "/api/users/manage-coordinators";

    const openBtn = document.getElementById("create-coord-btn");
    const modal = document.getElementById("coord-modal");
    const closeBtn = modal.querySelector(".close-btn");
    const form = document.getElementById("coord-form");

    const usernameInput = document.getElementById("coord-username");
    const emailInput = document.getElementById("coord-email");
    const passwordInput = document.getElementById("coord-pass");
    const coordIdInput = document.getElementById("coord-code");
    const deptSelect = document.getElementById("coord-dept");
    const idHiddenInput = document.getElementById("coord-id-hidden");

    const searchInput = document.getElementById("search-input");
    const downloadBtn = document.getElementById("download-btn");
    const tableRows = document.querySelectorAll("table tbody tr");

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    } 

    function openModal() {
        form.reset();
        idHiddenInput.value = "";
        modal.classList.remove("hidden");
        modal.style.display = "flex";
        document.getElementById("modal-title").textContent = "Add Coordinator";
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.style.display = "none";
    }

    openBtn.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const id = idHiddenInput.value;
        const url = id ? `${BASE_URL}/${id}/` : `${BASE_URL}/`;
        const method = id ? "PUT" : "POST";

        const payload = {
            username: usernameInput.value,
            email: emailInput.value,
            coord_id: coordIdInput.value,
            department_id: deptSelect.value,
        };
        if (passwordInput.value.trim()) {
            payload.password = passwordInput.value;
        }

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify(payload)
            });

            let data = {};
            try {
                data = await response.json(); // try parsing error response
            } catch (jsonErr) {
                console.warn("Could not parse JSON from server");
            }

            if (response.ok) {
                showAlert("✅ Coordinator saved successfully!", "success", 1500, () => location.reload());
            } else {
                let message = "⚠️ Failed to save coordinator.";
                if (data && typeof data === "object" && Object.keys(data).length > 0) {
                    const errors = Object.entries(data).map(([field, value]) => {
                        if (Array.isArray(value)) {
                            return `${field}: ${value.join(", ")}`;
                        } else {
                            return `${field}: ${value}`;
                        }
                    });
                    message = errors.join("\n");
                }
                showAlert(message, "error", 6000);
            }
        } catch (err) {
            console.error("❌ Error saving coordinator:", err);
            showAlert("⚠️ Unexpected error occurred.", "error");
        }
    });

    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => {
            idHiddenInput.value = btn.dataset.id;
            usernameInput.value = btn.dataset.username;
            emailInput.value = btn.dataset.email;
            coordIdInput.value = btn.dataset.coord_id;
            deptSelect.value = btn.dataset.department;
            passwordInput.value = "";

            document.getElementById("modal-title").textContent = "Edit Coordinator";
            modal.classList.remove("hidden");
            modal.style.display = "flex";
        });
    });

    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const confirmed = confirmAction("Are you sure you want to delete this coordinator?");
            if (!confirmed) return;

            try {
                const response = await fetch(`${BASE_URL}/${id}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": getCSRFToken()
                    }
                });

                if (response.ok) {
                    showAlert("✅ Coordinator deleted successfully.", "success", 1500, () => location.reload());
                } else {
                    const data = await response.json();
                    showAlert("⚠️ " + (data.error || "Failed to delete coordinator."), "error");
                }
            } catch (error) {
                console.error("❌ Delete Error:", error);
                showAlert("⚠️ Could not delete coordinator. Please try again.", "error");
            }
        });
    });

    searchInput.addEventListener("input", () => {
        const searchText = searchInput.value.trim().toLowerCase();
        const tableRows = document.querySelectorAll("table tbody tr");
    
        tableRows.forEach(row => {
            const rowText = row.innerText.replace(/\s+/g, " ").toLowerCase();
            row.style.display = rowText.includes(searchText) ? "" : "none";
        });
    });
    
    
    

    downloadBtn.addEventListener("click", () => {
        const headers = ["Username", "Email", "Coordinator ID", "Department", "College"];
        const visibleRows = Array.from(tableRows).filter(row => row.style.display !== "none");

        const csv = [
            headers.join(","),
            ...visibleRows.map(row => {
                const cols = row.querySelectorAll("td");
                return Array.from(cols).slice(0, 5).map(td => `"${td.textContent.trim()}"`).join(",");
            })
        ].join("\n");

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "coordinators_list.csv";
        a.click();
        URL.revokeObjectURL(url);
    });
});
