document.addEventListener("DOMContentLoaded", function () {
    const BASE_URL = "/api/users/profile/api/";
    const PASSWORD_URL = "/api/users/profile/change-password/";

    const profileForm = document.getElementById("profile-form");
    const passwordForm = document.getElementById("password-form");

    const qualificationInput = document.getElementById("qualification");
    const workPlaceInput = document.getElementById("work_place");

    // Prefill user profile fields
    fetch(BASE_URL)
        .then(res => res.json())
        .then(data => {
            if (data.username) document.getElementById("username").value = data.username;
            if (data.phone_number) document.getElementById("phone_number").value = data.phone_number;
            if (data.email) document.getElementById("email").value = data.email;

            // Supervisor extras
            if ('qualification' in data) {
                qualificationInput.value = data.qualification || "";
                showField("qualification");
            } else {
                hideField("qualification");
            }
            
            if ('work_place' in data) {
                workPlaceInput.value = data.work_place || "";
                showField("work_place");
            } else {
                hideField("work_place");
            }
            
        })
        .catch(err => {
            console.error("❌ Failed to load profile:", err);
            showAlert("⚠️ Failed to load profile.", "error");
        });

    // Hide a field by id (label + input)
    function hideField(fieldId) {
        const input = document.getElementById(fieldId);
        if (input) {
            input.style.display = "none";
            const label = document.querySelector(`label[for="${fieldId}"]`);
            if (label) label.style.display = "none";
        }
    }

    function showField(fieldId) {
        const input = document.getElementById(fieldId);
        const label = document.querySelector(`label[for="${fieldId}"]`);
        if (input) input.style.display = "block";
        if (label) label.style.display = "block";
    }
    

    // Update profile
    profileForm?.addEventListener("submit", async function (e) {
        e.preventDefault();

        const payload = {
            username: document.getElementById("username").value,
            phone_number: document.getElementById("phone_number").value,
            email: document.getElementById("email").value
        };

        if (qualificationInput && qualificationInput.style.display !== "none")
            payload.qualification = qualificationInput.value;

        if (workPlaceInput && workPlaceInput.style.display !== "none")
            payload.work_place = workPlaceInput.value;

        try {
            const res = await fetch(BASE_URL, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (res.ok) {
                showAlert("✅ Profile updated successfully!", "success");
            } else {
                const errorMsg = Object.values(data)[0];
                showAlert("⚠️ " + errorMsg, "error");
            }
        } catch (err) {
            console.error("❌ Error updating profile:", err);
            showAlert("⚠️ Something went wrong", "error");
        }
    });

    // Change password
    passwordForm?.addEventListener("submit", async function (e) {
        e.preventDefault();

        const payload = {
            old_password: document.getElementById("old_password").value,
            new_password: document.getElementById("new_password").value
        };

        try {
            const res = await fetch(PASSWORD_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (res.ok) {
                showAlert("✅ Password changed successfully", "success");
                passwordForm.reset();
            } else {
                const errorMsg = data.error || Object.values(data)[0];
                showAlert("⚠️ " + errorMsg, "error");
            }
        } catch (err) {
            console.error("❌ Password change error:", err);
            showAlert("⚠️ Unable to update password", "error");
        }
    });

    // Alert system
    function showAlert(message, type = "info") {
        let alertBox = document.getElementById("alert-box");

        if (!alertBox) {
            alertBox = document.createElement("div");
            alertBox.id = "alert-box";
            alertBox.style.padding = "10px";
            alertBox.style.marginTop = "10px";
            alertBox.style.borderRadius = "5px";
            alertBox.style.fontWeight = "bold";
            alertBox.style.textAlign = "center";
            document.querySelector(".container")?.prepend(alertBox);
        }

        alertBox.style.display = "block";
        alertBox.style.backgroundColor = type === "success" ? "#d4edda" : "#f8d7da";
        alertBox.style.color = type === "success" ? "#155724" : "#721c24";
        alertBox.textContent = message;

        setTimeout(() => {
            alertBox.style.display = "none";
        }, 4000);
    }
});
