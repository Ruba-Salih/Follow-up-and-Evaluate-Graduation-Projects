document.addEventListener("DOMContentLoaded", () => {
    const feedbackForm = document.getElementById("feedback-form");
    const feedbackMessage = document.getElementById("feedback-message");
    const feedbackProjectId = feedbackForm?.dataset.projectId;

    feedbackForm?.addEventListener("submit", async (e) => {
        e.preventDefault();

        const comment = document.getElementById("feedback-comment").value.trim();
        if (!comment) {
            alert("Feedback cannot be empty.");
            return;
        }

        const res = await fetch("/api/feedback/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({
                comment: comment,
                project: feedbackProjectId
            })
        });

        if (res.ok) {
            feedbackMessage.textContent = "✅ Feedback sent successfully!";
            feedbackMessage.style.color = "green";
            document.getElementById("feedback-comment").value = "";
        } else {
            feedbackMessage.textContent = "❌ Failed to send feedback.";
            feedbackMessage.style.color = "red";
        }
    });
});
