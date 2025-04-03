document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");

    // 🔐 Utility to get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/api/users/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken  // ✅ Important for session-auth POST
                },
                body: JSON.stringify({ username, password }),
                credentials: "include"  // ✅ Ensure session cookie is sent/received
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem("access", data.access);
                localStorage.setItem("refresh", data.refresh);
                window.location.href = data.user.home_url;
            } else {
                document.getElementById("error-message").innerText = data.error || "Invalid credentials.";
            }
        } catch (error) {
            console.error("Login Error:", error);
            document.getElementById("error-message").innerText = "Login failed. Please try again.";
        }
    });
});
