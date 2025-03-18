document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/api/users/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem("access", data.access);
                localStorage.setItem("refresh", data.refresh);
                window.location.href =  data.user.home_url;
            } else {
                document.getElementById("error-message").innerText = data.error || "Invalid credentials.";
            }
        } catch (error) {
            console.error("Login Error:", error);
            document.getElementById("error-message").innerText = "Login failed. Please try again.";
        }
    });
});
