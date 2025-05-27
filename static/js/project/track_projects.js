document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const projectList = document.getElementById("project-list");
    const modal = document.getElementById("coord-modal");
    const closeBtn = modal.querySelector(".close-btn");
    const feedbackInput = document.getElementById("coord-feedback-input");
    const submitFeedbackBtn = document.getElementById("submit-feedback-btn");
    const feedbackMessage = document.getElementById("feedback-message");

    let currentReportId = null;

    const allReports = Array.from(document.querySelectorAll(".report-card")).map(card => ({
        id: card.getAttribute("data-report-id"),
        element: card,
        project_name: card.getAttribute("data-project-name").toLowerCase(),
        supervisor: card.getAttribute("data-supervisor").toLowerCase(),
        report_date: card.getAttribute("data-report-date").toLowerCase()
    }));

    // 🔍 Search filter
    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase();
        allReports.forEach(r => {
            const match = r.project_name.includes(query) ||
                          r.supervisor.includes(query) ||
                          r.report_date.includes(query);
            r.element.style.display = match ? "" : "none";
        });
    });

    // 📄 Open modal and fill content
    projectList.addEventListener("click", (e) => {
        const viewBtn = e.target.closest(".btn-view");
        if (!viewBtn) return;

        const card = viewBtn.closest(".report-card");
        if (!card) return;

        currentReportId = card.getAttribute("data-report-id");

        document.getElementById("modal-project-name").textContent = card.getAttribute("data-project-name") || "—";
        document.getElementById("modal-supervisor").textContent = card.getAttribute("data-supervisor") || "—";
        document.getElementById("modal-report-date").textContent = card.getAttribute("data-report-date") || "—";
        document.getElementById("modal-progress").textContent = card.getAttribute("data-progress") || "—";
        document.getElementById("modal-work-done").textContent = card.getAttribute("data-work-done") || "—";
        document.getElementById("modal-work-remaining").textContent = card.getAttribute("data-work-remaining") || "—";
        document.getElementById("modal-challenges").textContent = card.getAttribute("data-challenges") || "—";

        // ✅ Read plain string from button
        const studentsStr = viewBtn.getAttribute("data-students-html");
        document.getElementById("modal-students").textContent = studentsStr || "—";

        feedbackInput.value = "";
        feedbackMessage.textContent = "";
        modal.classList.add("show");
        loadFeedbackThread(currentReportId);

    });

    async function loadFeedbackThread(reportId) {
    const threadDiv = document.getElementById("feedback-thread");
    threadDiv.innerHTML = " ";

    try {
        const res = await fetch(`/api/project/feedback/?report_id=${reportId}`);
        if (!res.ok) throw new Error("Failed to load feedback");
        const data = await res.json();

        if (!data.length) {
            threadDiv.innerHTML = "<p class='text-muted'>No feedback yet.</p>";
            return;
        }

        threadDiv.innerHTML = "";
        data.forEach(fb => {
            const card = document.createElement("div");
            card.classList.add("feedback-card");
            card.innerHTML = `
                <strong>👤 ${fb.sender_name || "Unknown"}</strong><br>
                <p>${fb.message}</p>
                <small class="text-muted">${new Date(fb.created_at).toLocaleString()}</small>
                <hr>
            `;
            threadDiv.appendChild(card);
        });
    } catch (err) {
        threadDiv.innerHTML = "<p class='text-danger'>❌ Could not load feedback.</p>";
        console.error("Error loading feedback:", err);
    }
}


    // ❌ Close modal
    closeBtn.addEventListener("click", () => {
        modal.classList.remove("show");
        feedbackInput.value = "";
        feedbackMessage.textContent = "";
        loadFeedbackThread(currentReportId); 
    });

    // 📤 Submit feedback
    submitFeedbackBtn.addEventListener("click", async () => {
        const message = feedbackInput.value.trim();
        if (!message || !currentReportId) return;

        try {
            const res = await fetch("/api/project/feedback/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('input[name="csrfmiddlewaretoken"]').value
                },
                body: JSON.stringify({
                    report: currentReportId, 
                    feedback_text: message
                })
            });

            if (res.ok) {
                feedbackMessage.textContent = "✅ Feedback submitted.";
                feedbackInput.value = "";
                loadFeedbackThread(currentReportId);
            } else {
                const err = await res.json();
                feedbackMessage.textContent = "❌ " + (err.detail || "Failed to submit.");
            }
        } catch (err) {
            feedbackMessage.textContent = "❌ Network error.";
        }
    });
});
