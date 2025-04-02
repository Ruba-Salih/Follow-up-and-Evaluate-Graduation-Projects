console.log("loading..");

document.addEventListener("DOMContentLoaded", function () {
    const BASE_URL = "/university";

    const modal = document.getElementById("college-modal");
    const openBtn = document.getElementById("create-college-btn");
    const closeBtn = modal.querySelector(".close-btn");
    const form = document.getElementById("college-form");
    const collegeNameInput = document.getElementById("college-name");
    const collegeIdInput = document.getElementById("college-id");
    const deptFieldsContainer = document.getElementById("department-fields");
    const addDeptBtn = document.getElementById("add-department-btn");
    const downloadBtn = document.getElementById("download-colleges");
    const autoReload = true;

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    }

    function openModal() {
        modal.classList.remove("hidden");
        modal.style.display = "flex";
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.style.display = "none";
        form.reset();
        collegeIdInput.value = "";
        const allDeptGroups = deptFieldsContainer.querySelectorAll(".department-group");
        allDeptGroups.forEach((group, index) => {
            if (index > 0) group.remove();
            else group.querySelector("input").value = "";
        });
    }

    openBtn.addEventListener("click", () => {
        document.getElementById("college-modal-title").textContent = "Add New College";
        openModal();
    });

    closeBtn.addEventListener("click", closeModal);

    addDeptBtn.addEventListener("click", () => {
        const div = document.createElement("div");
        div.className = "department-group";
        div.innerHTML = '<input type="text" name="departments" class="department-input" placeholder="Department Name">';
        deptFieldsContainer.appendChild(div);
    });

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const name = collegeNameInput.value.trim();
        const id = collegeIdInput.value;

        const departments = Array.from(document.querySelectorAll(".department-input"))
            .map(input => input.value.trim())
            .filter(name => name);

        const payload = { name, departments };
        const method = id ? "PUT" : "POST";
        const url = id ? `${BASE_URL}/manage-colleges/${id}/` : `${BASE_URL}/manage-colleges/`;

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok) {
                showAlert("✅ College saved successfully!", "success", 0, () => {
                    if (autoReload) location.reload();
                });
            } else {
                showAlert("⚠️ " + (data.error || "Failed to save college."), "error");
            }
        } catch (err) {
            console.error("❌ Error:", err);
            showAlert("⚠️ Unexpected error occurred. Please try again.", "warning");
        }
    });

    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const confirmed = await confirmAction("Are you sure you want to delete this college?");
            if (!confirmed) return;

            try {
                const response = await fetch(`${BASE_URL}/manage-colleges/delete/${id}/`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    }
                });

                if (response.ok) {
                    showAlert("✅ College deleted successfully.", "success", 0, () => {
                        if (autoReload) location.reload();
                    });
                } else {
                    const data = await response.json();
                    showAlert("⚠️ " + (data.error || "Failed to delete college."), "error");
                }
            } catch (error) {
                console.error("❌ Delete Error:", error);
                showAlert("⚠️ Could not delete college. Please try again.", "error");
            }
        });
    });

    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            const departments = JSON.parse(btn.dataset.departments);

            document.getElementById("college-modal-title").textContent = "Edit College";
            collegeIdInput.value = id;
            collegeNameInput.value = name;

            const firstInput = deptFieldsContainer.querySelector(".department-input");
            firstInput.value = "";
            deptFieldsContainer.querySelectorAll(".department-group").forEach((el, idx) => {
                if (idx > 0) el.remove();
            });

            departments.forEach((dept, i) => {
                if (i === 0) firstInput.value = dept.name;
                else {
                    const div = document.createElement("div");
                    div.className = "department-group";
                    div.innerHTML = `<input type="text" name="departments" class="department-input" value="${dept.name}" placeholder="Department Name">`;
                    deptFieldsContainer.appendChild(div);
                }
            });

            openModal();
        });
    });

    // ✅ Download CSV
    if (downloadBtn) {
        downloadBtn.addEventListener("click", () => {
            const rows = Array.from(document.querySelectorAll("table tbody tr"));
            const csv = [
                ["College Name", "Departments"].join(","),
                ...rows.map(row => {
                    const name = row.querySelector("td:nth-child(1)").textContent.trim();
                    const depts = Array.from(row.querySelectorAll("td:nth-child(2) li"))
                        .map(li => li.textContent.trim()).join(" | ");
                    return `"${name}","${depts}"`;
                })
            ].join("\n");

            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "colleges_list.csv";
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    // ✅ Live Search for College Name
const searchInput = document.getElementById("college-search");
if (searchInput) {
    const tableRows = document.querySelectorAll("table tbody tr");

    searchInput.addEventListener("input", () => {
        const searchText = searchInput.value.toLowerCase();
        tableRows.forEach(row => {
            const name = row.querySelector("td:nth-child(1)").textContent.toLowerCase();
            row.style.display = name.includes(searchText) ? "" : "none";
        });
    });
}

});
