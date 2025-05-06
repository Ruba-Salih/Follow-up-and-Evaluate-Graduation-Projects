window.showAlert = function (message, type = "success", duration = 0, onClose = null) {
    const alertBox = document.getElementById("custom-alert");
    const alertMessage = document.getElementById("alert-message");
    const closeBtn = document.getElementById("alert-close");

    if (!alertBox || !alertMessage || !closeBtn) {
        console.warn("⚠️ Alert container not found.");
        return;
    }
    // success  warning  error

    alertMessage.textContent = message;

    alertBox.className = "custom-alert";
    alertBox.classList.add(type);
    alertBox.classList.remove("hidden");

    const hideAlert = () => {
        alertBox.classList.add("hidden");
        if (typeof onClose === "function") {
            onClose();
        }
    };

    if (duration > 0) {
        const timeoutId = setTimeout(hideAlert, duration);
        closeBtn.onclick = () => {
            clearTimeout(timeoutId);
            hideAlert();
        };
    } else {
        closeBtn.onclick = hideAlert;
    }
};

window.confirmAction = function (message) {
    return new Promise((resolve) => {
        const confirmBox = document.getElementById("global-confirm");
        const confirmMessage = document.getElementById("confirm-message");
        const yesBtn = document.getElementById("confirm-yes");
        const noBtn = document.getElementById("confirm-no");

        confirmMessage.textContent = message;
        confirmBox.classList.remove("hidden");

        // Cleanup old listeners
        const newYesBtn = yesBtn.cloneNode(true);
        yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);

        newYesBtn.addEventListener("click", () => {
            confirmBox.classList.add("hidden");
            resolve(true);
        });

        noBtn.addEventListener("click", () => {
            confirmBox.classList.add("hidden");
            resolve(false);
        });
    });
};
