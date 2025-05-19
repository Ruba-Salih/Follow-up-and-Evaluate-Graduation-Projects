document.addEventListener("DOMContentLoaded", function () { 
    const createUserBtn = document.getElementById("create-user-btn");
    const createUserModal = document.getElementById("create-user-modal");
    const closeModal = document.querySelector(".close-btn");
    const userRoleSelect = document.getElementById("user-role");
    const studentForm = document.getElementById("student-form");
    const userForm = document.getElementById("user-form");
    const coordForm = document.getElementById("coordinator-form");

    let editingUserId = null;
    const autoReload = true;

    function resetForms() {
        studentForm.reset();
        userForm.reset();
        coordForm.reset();
        editingUserId = null;
    }

    function closeModalHandler() {
        createUserModal.style.display = "none";
        createUserModal.classList.add("hidden");
    }

    createUserBtn.addEventListener("click", function () {
        createUserModal.style.display = "flex";
        createUserModal.classList.remove("hidden");
        resetForms();
        userRoleSelect.value = "student";
        userRoleSelect.dispatchEvent(new Event("change"));
    });

    closeModal.addEventListener("click", closeModalHandler);
    createUserModal.addEventListener("click", function (event) {
        if (event.target === createUserModal) closeModalHandler();
    });

    userRoleSelect.addEventListener("change", function () {
        const role = this.value;
        studentForm.classList.toggle("hidden", role !== "student");
        userForm.classList.toggle("hidden", role !== "user");
        coordForm.classList.toggle("hidden", role !== "coordinator");
    });

    function getDepartmentValue(selectId) {
        const select = document.getElementById(selectId);
        return select.disabled ? select.querySelector("option")?.value : select.value;
    }

    studentForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const userData = {
            username: document.getElementById("student-name").value,
            email: document.getElementById("student-email").value,
            phone_number: document.getElementById("student-phone").value,
            password: document.getElementById("student-password").value,
            role: "student",
            student_id: document.getElementById("student-id").value,
            sitting_number: document.getElementById("sitting-number").value,
            department_id: getDepartmentValue("student-department"),
            first_name: document.getElementById("student-first-name").value,
            last_name: document.getElementById("student-last-name").value,

        };
        await submitUser(userData);
    });

    userForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const userData = {
            username: document.getElementById("user-name").value,
            email: document.getElementById("user-email").value,
            phone_number: document.getElementById("user-phone").value,
            password: document.getElementById("user-password").value,
            role: "user",
            department_id: getDepartmentValue("user-department"),
            first_name: document.getElementById("user-first-name").value,
            last_name: document.getElementById("user-last-name").value,

        };
        await submitUser(userData);
    });

    coordForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const userData = {
            username: document.getElementById("coord-name").value,
            email: document.getElementById("coord-email").value,
            phone_number: document.getElementById("coord-phone").value,
            password: document.getElementById("coord-password").value,
            //coord_id: document.getElementById("coord-id").value,
            role: "coordinator",
            department_id: getDepartmentValue("coord-department"),
            first_name: document.getElementById("coord-first-name").value,
            last_name: document.getElementById("coord-last-name").value,

        };
        await submitUser(userData);
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }

    async function submitUser(userData) {
        const method = editingUserId ? "PUT" : "POST";
        const url = editingUserId
            ? `/api/users/manage-accounts/${editingUserId}/`
            : "/api/users/manage-accounts/";

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();
            if (response.ok) {
                showAlert("✅ User saved successfully!", "success", 0, () => {
                    if (autoReload) location.reload();
                });
            } else {
                showAlert("⚠️ " + (data.error || "Failed to save user."), "warning");
            }
        } catch (error) {
            console.error("❌ Error:", error);
            showAlert("⚠️ An error occurred. Please try again.", "warning");
        }
    }

    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            editingUserId = this.dataset.id;

            const username = this.dataset.username;
            const firstName = this.dataset.first_name || "";
            const lastName = this.dataset.last_name || "";
            const email = this.dataset.email;
            const phone = this.dataset.phone;
            const departmentId = this.dataset.department;
            const role = this.dataset.role;
            const studentId = this.dataset.student_id || "";
            const sittingNumber = this.dataset.sitting_number || "";
            const coordId = this.dataset.coord_id || "";

            createUserModal.style.display = "flex";
            createUserModal.classList.remove("hidden");
            userRoleSelect.value = role;
            userRoleSelect.dispatchEvent(new Event("change"));

            if (role === "student") {
                document.getElementById("student-name").value = username;
                document.getElementById("student-first-name").value = firstName;
                document.getElementById("student-last-name").value = lastName;
                document.getElementById("student-email").value = email;
                document.getElementById("student-phone").value = phone;
                document.getElementById("student-department").value = departmentId;
                document.getElementById("student-id").value = studentId;
                document.getElementById("sitting-number").value = sittingNumber;
            } else if (role === "user") {
                document.getElementById("user-name").value = username;
                document.getElementById("user-first-name").value = firstName;
                document.getElementById("user-last-name").value = lastName;
                document.getElementById("user-email").value = email;
                document.getElementById("user-phone").value = phone;
                document.getElementById("user-department").value = departmentId;
            } else if (role === "coordinator") {
                document.getElementById("coord-name").value = username;
                document.getElementById("coord-first-name").value = firstName;
                document.getElementById("coord-last-name").value = lastName;
                document.getElementById("coord-email").value = email;
                document.getElementById("coord-phone").value = phone;
                document.getElementById("coord-id").value = coordId;
                document.getElementById("coord-department").value = departmentId;
            }
        });
    });

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", async function () {
            const userId = this.dataset.id;
            const confirmed = await confirmAction("Are you sure you want to delete this user?");
            if (!confirmed) return;

            try {
                const response = await fetch(`/api/users/manage-accounts/${userId}/`, {
                    method: "DELETE",
                    headers: { "X-CSRFToken": getCSRFToken() }
                });

                if (response.ok) {
                    showAlert("✅ User deleted successfully.", "success", 0, () => {
                        if (autoReload) location.reload();
                    });
                } else {
                    const data = await response.json();
                    showAlert("⚠️ " + (data.error || "Failed to delete user."), "error");
                }
            } catch (error) {
                console.error("❌ Delete Error:", error);
                showAlert("⚠️ Could not delete user. Please try again.", "error");
            }
        });
    });

    const searchInput = document.getElementById("search-input");
    const roleFilter = document.getElementById("role-filter");
    const tableRows = document.querySelectorAll("table tbody tr");

    function filterUsers() {
    const searchText = searchInput.value.toLowerCase();
    const selectedRole = roleFilter.value;

    let rowNumber = 1;

    tableRows.forEach(row => {
        const username = row.querySelector("td:nth-child(2)")?.textContent.toLowerCase();
        const roleAttr = row.querySelector(".edit-btn")?.getAttribute("data-role");
        const matchesSearch = !searchText || username.includes(searchText);
        const matchesRole = !selectedRole || roleAttr === selectedRole;

        if (matchesSearch && matchesRole) {
            row.style.display = "";
            const numberCell = row.querySelector(".user-index");
            if (numberCell) numberCell.textContent = rowNumber++;
        } else {
            row.style.display = "none";
        }
    });
}

    searchInput.addEventListener("input", filterUsers);
    roleFilter.addEventListener("change", filterUsers);

    document.getElementById("download-btn").addEventListener("click", () => {
        const headers = ["Username", "Email", "Phone", "Department"];
        const visibleRows = Array.from(tableRows).filter(row => row.style.display !== "-");

        const csv = [
            headers.join(","),
            ...visibleRows.map((row, index) => {
                const cols = row.querySelectorAll("td");
                return [
            `"${index + 1}"`, //
            `"${cols[1].textContent.trim()}"`, // Username
            `"${cols[2].textContent.trim()}"`, // Full Name
            `"${cols[3].textContent.trim()}"`, // Email
            `"${cols[4].textContent.trim()}"`, // Phone
            `"${cols[5].textContent.trim()}"`  // Department
        ].join(",");
            })
        ].join("\n");

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "users_list.csv";
        a.click();
        URL.revokeObjectURL(url);
    });
    filterUsers(); // Initialize row numbers on first load

});
