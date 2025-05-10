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

    function populateSelect(selectEl, items, isMulti = true, selectedIds = []) {
        if (!selectEl) return;
        selectEl.innerHTML = "";
        if (!isMulti) {
            const placeholder = document.createElement("option");
            placeholder.value = "";
            placeholder.textContent = "-- Select Recipient --";
            selectEl.appendChild(placeholder);
        }
        items.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id;
            const fullName = [item.first_name, item.last_name].filter(Boolean).join(" ");
            option.textContent = fullName || item.username || item.name || "";

            if (selectedIds.includes(item.id)) {
                option.selected = true;
            }
            selectEl.appendChild(option);
        });
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
                checkbox.name = "team_members";
                checkbox.value = student.id;
        
                const label = document.createElement("label");
        
                const isSelected = selectedIds.includes(student.id);
                const fullName = [student.first_name, student.last_name].filter(Boolean).join(" ") || student.username;
        
                if (student.already_assigned && !isSelected) {
                    checkbox.disabled = true;
                    label.style.opacity = "0.6";
                    label.title = "Already assigned to another project.";
                    label.appendChild(checkbox);
                    label.append(` ${fullName} (Assigned)`);
                } else {
                    checkbox.checked = isSelected;
                    label.appendChild(checkbox);
                    label.append(` ${fullName}`);
                }
        
                wrapper.appendChild(label);
                checkboxContainer.appendChild(wrapper);
            });
        }
        
    
        displayList(list);
    
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.toLowerCase();
            const filtered = list.filter(s => {
                const fullName = [s.first_name, s.last_name].filter(Boolean).join(" ").toLowerCase();
                return fullName.includes(query) || s.username.toLowerCase().includes(query);
            });
            
            displayList(filtered);
        });
    }    

    async function loadData() {
        const res = await fetch("/api/project/proposals/");
        const data = await res.json();

        studentsList = data.students || [];
        coordinatorsList = data.coordinators || [];
        teachersList = data.teachers || [];

        coordinatorsList.forEach(coordinator => {
            if (coordinator.department) {
                departmentToCoordinator[coordinator.department] = coordinator.id;
            }
        });

        renderCheckboxes(studentsList);
        isTeacher = coordinatorsList.length > 0 && Boolean(departmentSelect);

        if (isTeacher && proposedToSelect) {
            const proposedToLabel = proposedToSelect.closest("label");
            if (proposedToLabel) {
                proposedToLabel.remove();
            }
            proposedToSelect.remove();
        }
    }

    await loadData();

    createBtn?.addEventListener("click", () => {
        editMode = false;
        currentProposalId = null;
        form.reset();

        feedbackSection.classList.add("hidden");
        feedbackContent.textContent = "";

        renderCheckboxes(studentsList);

        if (!isTeacher && proposedToSelect) {
            populateSelect(proposedToSelect, teachersList, false);
        }

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

        if (isTeacher) {
            if (!departmentSelect?.value) {
                showAlert("Please select a department before submitting your proposal.", 'warning');
                return; // 🚨 stop the submit
            }
        }
        
        const formData = new FormData();
        formData.append("title", titleInput.value);
        formData.append("description", descriptionInput.value);
        formData.append("field", fieldInput.value);
        formData.append("team_member_count", teamCount.value || 1);
        formData.append("duration", document.getElementById("duration").value || 0);
        if (additionalComment?.value) formData.append("additional_comment", additionalComment.value);
        if (departmentSelect?.value) formData.append("department", departmentSelect.value);

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

        const url = editMode ? `/api/project/proposals/${currentProposalId}/` : `/api/project/proposals/`;

        const response = await fetch(url, {
            method: editMode ? "PUT" : "POST",
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
        
            const message =
                error.detail ||
                error.message ||
                Object.values(error)[0] || // first field if it's a serializer error
                "Something went wrong.";
        
            showAlert(message, 'error');
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
            document.getElementById("duration").value = data.duration || 0;

            const feedback = data.feedback_text?.trim();
            const role = data.feedback_sender_role || "Teacher";
            if (feedback) {
                feedbackSection.classList.remove("hidden");
                const label = feedbackSection.querySelector("label");
                if (label) {
                    label.innerHTML = `<strong>${role} Feedback:</strong>`;
                }
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
            // 🧩 Show team members as full names in the modal
            const teamMembersSpan = document.getElementById("modal-team-members");
            if (teamMembersSpan) {
                const fullNames = data.team_members?.map(member => {
                    return [member.first_name, member.last_name].filter(Boolean).join(" ") || member.username;
                }).join(", ") || "None";
                
                teamMembersSpan.textContent = fullNames;
            }


            if (!isTeacher && proposedToSelect) {
                populateSelect(proposedToSelect, teachersList, false, [data.proposed_to]);
            }

            modal.classList.add("show");
            modal.classList.remove("hidden");
            modal.style.display = "flex";
        });

        card.querySelector(".delete-btn")?.addEventListener("click", async () => {
            const confirmed = await confirmAction("Delete this proposal?");
            if (confirmed) {
                const res = await fetch(`/api/project/proposals/${id}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                });
                if (res.ok) {
                    location.reload();
                } else {
                    showAlert("Delete failed.", 'error');
                }
            }

        });
    });

    function filterProposals() {
        const query = searchInput.value.toLowerCase();
        const selectedStatus = statusFilter.value.toLowerCase();
        const cards = proposalList.querySelectorAll(".proposal-card");
    
        cards.forEach(card => {
            const title = card.querySelector("h4")?.textContent.toLowerCase() || "";
            const field = card.querySelector("p:nth-of-type(1)")?.textContent.toLowerCase() || "";
            const date = card.querySelector("p:nth-of-type(2)")?.textContent.toLowerCase() || "";
    
            const statusBadges = card.querySelectorAll(".status");
            let teacherStatus = "", coordinatorStatus = "";
    
            if (statusBadges.length > 0) {
                teacherStatus = statusBadges[0]?.classList[1] || "";
            }
            if (statusBadges.length > 1) {
                coordinatorStatus = statusBadges[1]?.classList[1] || "";
            }
    
            const matchesSearch = title.includes(query) || field.includes(query) || date.includes(query);
            const matchesStatus = selectedStatus === "" || teacherStatus.includes(selectedStatus) || coordinatorStatus.includes(selectedStatus);
    
            if (matchesSearch && matchesStatus) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    }
    
    // ✅ You must ADD these 4 lines after defining the function:
    const searchInput = document.getElementById("search-input");
    const statusFilter = document.getElementById("status-filter");
    const proposalList = document.getElementById("proposal-list");
    
    searchInput.addEventListener("input", filterProposals);
    statusFilter.addEventListener("change", filterProposals);
    

});
