document.addEventListener("DOMContentLoaded", function () {
    const createUserBtn = document.getElementById("create-user-btn");
    const createUserModal = document.getElementById("create-user-modal");
    const closeModal = document.querySelector(".close-btn");
    const modalContent = document.querySelector(".modal-content");

    // User Type Selection Logic
    const userRoleSelect = document.getElementById("user-role");
    const studentForm = document.getElementById("student-form");
    const userForm = document.getElementById("user-form");

    // ✅ Ensure elements exist
    if (!createUserBtn || !createUserModal || !closeModal || !modalContent || !userRoleSelect) {
        console.error("❌ Error: Required elements not found.");
        return;
    }

    console.log("✅ JavaScript Loaded");

    // ✅ Open Create User Modal with Student Form as Default
    createUserBtn.addEventListener("click", function () {
        console.log("✅ Create User Button Clicked");
        
        // Make sure modal is visible
        createUserModal.style.display = "flex";  
        createUserModal.classList.remove("hidden"); 

        // ✅ Ensure Student Form is default
        studentForm.classList.remove("hidden");
        userForm.classList.add("hidden");
        userRoleSelect.value = "student"; // Default to Student
    });

    // ✅ Close Modal when clicking "X" button
    closeModal.addEventListener("click", function () {
        console.log("✅ Close Button Clicked");
        createUserModal.style.display = "none";  // ✅ Hide modal
        createUserModal.classList.add("hidden");
    });

    // ✅ Close Modal when clicking outside modal content
    createUserModal.addEventListener("click", function (event) {
        if (event.target === createUserModal) {
            console.log("✅ Clicked outside modal, closing.");
            createUserModal.style.display = "none";
            createUserModal.classList.add("hidden");
        }
    });

    // ✅ Handle Role Selection to Show Correct Form
    userRoleSelect.addEventListener("change", function () {
        console.log("✅ Role Changed: " + this.value);

        if (this.value === "student") {
            studentForm.classList.remove("hidden");
            userForm.classList.add("hidden");
        } else if (this.value === "user") {
            studentForm.classList.add("hidden");
            userForm.classList.remove("hidden");
        }
    });

    // ✅ Handle Student Form Submission
    studentForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        console.log("✅ Student Form Submitted");

        const userData = {
            username: document.getElementById("student-name").value,
            email: document.getElementById("student-email").value,
            phone_number: document.getElementById("student-phone").value,
            password: document.getElementById("student-password").value,
            role: "student",
            student_id: document.getElementById("student-id").value,
            sitting_number: document.getElementById("sitting-number").value,
            department_id: document.getElementById("student-department").value,
        };

        await submitUser(userData);
    });

    // ✅ Handle Normal User Form Submission
    userForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        console.log("✅ Normal User Form Submitted");

        const userData = {
            username: document.getElementById("user-name").value,
            email: document.getElementById("user-email").value,
            phone_number: document.getElementById("user-phone").value,
            password: document.getElementById("user-password").value,
            role: "user",
            department_id: document.getElementById("user-department").value,
        };

        await submitUser(userData);
    });

    // ✅ Function to Submit User Data
    async function submitUser(userData) {
        console.log("✅ Submitting User Data:", userData);
        try {
            const response = await fetch("/api/users/manage-accounts/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(userData),
            });

            const data = await response.json();
            if (response.ok) {
                alert("✅ User created successfully!");
                location.reload();
            } else {
                alert("⚠️ " + (data.error || "Failed to create user."));
            }
        } catch (error) {
            console.error("❌ Error:", error);
            alert("⚠️ An error occurred. Please try again.");
        }
    }
});
