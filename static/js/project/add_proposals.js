document.addEventListener("DOMContentLoaded", async () => {
    const modal = document.getElementById("proposal-modal");
    const form = document.getElementById("proposal-form");
    const createBtn = document.getElementById("create-proposal-btn");
    const closeBtn = document.querySelector(".close-btn");

    const titleInput = document.getElementById("title");
    const descriptionInput = document.getElementById("description");
    const fileInput = document.getElementById("attached_file");
    const teamCount = document.getElementById("team_member_count");
    const fieldInput = document.getElementById("field");
    const teamMemberWrapper = document.getElementById("team-member-checkboxes");
    const proposedToSelect = document.getElementById("proposed_to");
    const departmentSelect = document.getElementById("department");
    const additionalComment = document.getElementById("additional_comment");

    const feedbackSection = document.getElementById("feedback-section");
    const feedbackContent = document.getElementById("feedback-content");

    let studentsList = [];
    let coordinatorsList = [];
    let teachersList = [];
    let editMode = false;
    let currentProposalId = null;
    let isTeacher = false;

    let departmentToCoordinator = {};

    async function loadData() {
        const res = await fetch("/api/project/proposals/");
        const data = await res.json();

        studentsList = data.students || [];
        coordinatorsList = data.coordinators || [];
        teachersList = data.teachers || [];

        // Map department ID to coordinator
        coordinatorsList.forEach(c => {
            if (c.department) {
                departmentToCoordinator[c.department] = c.id;
            }
        });

        renderCheckboxes(studentsList);
        isTeacher = coordinatorsList.length > 0 && departmentSelect;

        // Hide proposedToSelect for teachers
        if (isTeacher && proposedToSelect) {
            proposedToSelect.closest("label")?.remove();
            proposedToSelect.remove();
        }
    }

    function renderCheckboxes(list, selectedIds = []) {
        if (!teamMemberWrapper) return;
        teamMemberWrapper.innerHTML = "";

        const searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.placeholder = "🔍 Search students...";
        teamMemberWrapper.appendChild(searchInput);

        const checkboxContainer = document.createElement("div");
        checkboxContainer.classList.add("team-checkbox-list");
        teamMemberWrapper.appendChild(checkboxContainer);

        function displayList(filtered) {
            checkboxContainer.innerHTML = "";
            filtered.forEach(student => {
                const wrapper = document.createElement("div");
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.value = student.id;
                checkbox.name = "team_members";
                if (selectedIds.includes(student.id)) checkbox.checked = true;

                const label = document.createElement("label");
                label.appendChild(checkbox);
                label.append(" " + student.username);
                wrapper.appendChild(label);
                checkboxContainer.appendChild(wrapper);
            });
        }

        displayList(list);

        searchInput.addEventListener("input", () => {
            const query = searchInput.value.toLowerCase();
            const filtered = list.filter(s => s.username.toLowerCase().includes(query));
            displayList(filtered);
        });
    }

    await loadData();

    createBtn?.addEventListener("click", () => {
        editMode = false;
        currentProposalId = null;
        form.reset();

        feedbackSection.classList.add("hidden");
        feedbackContent.textContent = "";

        renderCheckboxes(studentsList);

        modal.classList.add("show");
        modal.classList.remove("hidden");
        modal.style.display = "flex";
    });

    closeBtn?.addEventListener("click", () => {
        modal.classList.remove("show");
        modal.classList.add("hidden");
        modal.style.display = "none";
    });

    form?.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append("title", titleInput.value);
        formData.append("description", descriptionInput.value);
        formData.append("field", fieldInput.value);
        formData.append("team_member_count", teamCount.value || 1);
        if (additionalComment?.value) formData.append("additional_comment", additionalComment.value);
        if (departmentSelect?.value) formData.append("department", departmentSelect.value);

        // Automatically assign coordinator if teacher
        if (isTeacher) {
            const deptId = departmentSelect?.value;
            const coordId = departmentToCoordinator[deptId];
            if (coordId) {
                formData.append("proposed_to", coordId);
            }
        } else {
            if (proposedToSelect?.value) {
                formData.append("proposed_to", proposedToSelect.value);
            }
        }

        if (fileInput?.files.length > 0) {
            formData.append("attached_file", fileInput.files[0]);
        }

        const checkedBoxes = teamMemberWrapper.querySelectorAll("input[type='checkbox']:checked");
        checkedBoxes.forEach(cb => formData.append("team_members_ids", cb.value));

        const url = editMode
            ? `/api/project/proposals/${currentProposalId}/`
            : `/api/project/proposals/`;
        const method = editMode ? "PUT" : "POST";

        const response = await fetch(url, {
            method,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: formData
        });

        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            console.error("Error submitting proposal:", error);
            alert("Something went wrong. Check console for details.");
        }
    });

    document.querySelectorAll(".proposal-card").forEach(card => {
        const id = card.dataset.id;
        card.querySelector(".view-btn")?.addEventListener("click", async () => {
            const res = await fetch(`/api/project/proposals/${id}/`);
            const data = await res.json();

            editMode = true;
            currentProposalId = data.id;

            titleInput.value = data.title;
            descriptionInput.value = data.description;
            fieldInput.value = data.field;
            teamCount.value = data.team_member_count || "";
            additionalComment.value = data.additional_comment || "";

            const feedback = data.teacher_feedback?.trim();
            if (feedback) {
                feedbackSection.classList.remove("hidden");
                feedbackContent.textContent = feedback;
            } else {
                feedbackSection.classList.add("hidden");
                feedbackContent.textContent = "";
            }

            if (departmentSelect && data.department) {
                departmentSelect.value = data.department;
            }

            const selectedTeamMemberIds = data.team_members?.map(s => s.id) || [];
            renderCheckboxes(studentsList, selectedTeamMemberIds);

            if (!isTeacher && proposedToSelect) {
                populateSelect(proposedToSelect, teachersList, false, [data.proposed_to]);
            }

            modal.classList.add("show");
            modal.classList.remove("hidden");
            modal.style.display = "flex";
        });

        card.querySelector(".delete-btn")?.addEventListener("click", async () => {
            if (confirm("Delete this proposal?")) {
                const res = await fetch(`/api/project/proposals/${id}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                });
                if (res.ok) location.reload();
                else alert("Delete failed.");
            }
        });
    });
});
