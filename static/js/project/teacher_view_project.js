document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("customModalOverlay");
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = modal.querySelector(".close-modal");
    const feedbackForm = document.getElementById("feedback-form");
  
    // Open modal (add class 'show')
    openBtn?.addEventListener("click", () => {
      modal.classList.add("show");
      document.getElementById("feedback_text")?.focus();
    });
  
    // Close modal (remove class 'show')
    closeBtn?.addEventListener("click", () => {
      modal.classList.remove("show");
    });
  
    // Close modal when clicking overlay (remove class 'show')
    modal?.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("show");
      }
    });
  
    // Close modal with Escape key (remove class 'show')
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("show")) {
        modal.classList.remove("show");
      }
    });
  
    // Handle feedback form submission
    feedbackForm?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(feedbackForm);
      const csrfToken = formData.get("csrfmiddlewaretoken");
  
      try {
        const res = await fetch(`/api/project/feedback/`, {
          method: "POST",
          headers: { "X-CSRFToken": csrfToken },
          body: formData,
        });
  
        const data = await res.json();
        if (res.ok) {
          showAlert("✅ Feedback submitted successfully!", 'success');
          feedbackForm.reset();
          modal.classList.remove("show");
        } else {
          alert("❌ Error: " + (data.detail || "Something went wrong."));
        }
      } catch (err) {
        console.error("Submit error:", err);
        alert("❌ Network error.");
      }
    });
});
