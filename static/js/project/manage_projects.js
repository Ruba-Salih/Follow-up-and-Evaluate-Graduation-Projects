document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("project-modal");
    const form = document.getElementById("project-form");
    const createBtn = document.getElementById("create-project-btn");
    const closeBtn = document.querySelector(".close-btn");

    const idField = document.getElementById("project-id");
    const nameInput = document.getElementById("name");
    const descriptionInput = document.getElementById("description");
    const fieldInput = document.getElementById("field");
    const deptInput = document.getElementById("department");
    const countInput = document.getElementById("team_member_count");
    const yearInput = document.getElementById("academic_year");

    const studentWrapper = document.getElementById("student-wrapper");
    const supervisorWrapper = document.getElementById("supervisor-wrapper");
    const readerWrapper = document.getElementById("reader-wrapper");
    const judgeContainer = document.getElementById("judge-checkboxes");

    const ROLE = { SUPERVISOR: "Supervisor", READER: "Reader", JUDGE: "Judgement Committee" };
    let studentsList = [], teachersList = [];
    let supervisorSelect = null;  // 🔥 Make supervisorSelect global
    let readerSelect = null;      // 🔥 Make readerSelect global

    function createCheckboxListWithSearch(wrapper, labelText, list, selectedIds = [], name = "") {
        wrapper.innerHTML = "";
        const label = document.createElement("label");
        label.textContent = labelText;
        wrapper.appendChild(label);

        const search = document.createElement("input");
        search.type = "text";
        search.placeholder = "🔍 Search...";
        wrapper.appendChild(search);

        const listContainer = document.createElement("div");
        listContainer.classList.add("judge-list", "student-list");
        wrapper.appendChild(listContainer);

        const confirmedReassignments = new Set();

        function renderList(filter = "") {
            listContainer.innerHTML = "";
            list
                .filter(user => user.username.toLowerCase().includes(filter.toLowerCase()))
                .forEach(user => {
                    const label = document.createElement("label");
                    const cb = document.createElement("input");
                    cb.type = "checkbox";
                    cb.name = name;
                    cb.value = user.id;
                    if (selectedIds.includes(user.id)) cb.checked = true;
                    const isAssigned = user.is_assigned === true;

                    if (isAssigned) {
                        label.style.opacity = "0.5";
                        label.title = "Already assigned to another project";
                    }

                    cb.addEventListener("change", async () => {
                        const teamLimit = parseInt(countInput.value || "0");
                        if (cb.checked && isAssigned && !confirmedReassignments.has(user.id)) {
                            const confirmed = await confirmAction(`${user.username} is already assigned to another project. Do you want to reassign them?`);
                            if (confirmed) {
                                confirmedReassignments.add(user.id);
                            } else {
                                cb.checked = false;
                                return;
                            }
                        }

                        const selectedStudentIds = Array.from(wrapper.querySelectorAll("input[type=checkbox]:checked"))
                            .map(c => parseInt(c.value));

                        const validSelections = selectedStudentIds.filter(id => {
                            const student = list.find(u => u.id === id);
                            return !student?.is_assigned || confirmedReassignments.has(id);
                        });

                        if (validSelections.length > teamLimit) {
                            cb.checked = false;
                            showAlert(`You can only select up to ${teamLimit} student(s).`, 'warning');
                        }
                    });

                    label.appendChild(cb);
                    label.append(" " + user.username + (isAssigned ? " (Already Assigned)" : ""));
                    listContainer.appendChild(label);
                });
        }

        renderList();
        search.addEventListener("input", () => renderList(search.value));
    }

    function createSearchableSelect(wrapper, labelText, items, selectedId = null) {
        wrapper.innerHTML = "";
        const label = document.createElement("label");
        label.textContent = labelText;
        wrapper.appendChild(label);

        const search = document.createElement("input");
        search.type = "text";
        search.placeholder = "🔍 Search...";
        wrapper.appendChild(search);

        const select = document.createElement("select");
        select.size = 6;
        select.style.width = "100%";
        wrapper.appendChild(select);

        function render(filter = "", selectedValue = null) {
            select.innerHTML = "<option value=''>-- Select --</option>";
            items
                .filter(u => u.username.toLowerCase().includes(filter.toLowerCase()))
                .forEach(u => {
                    const opt = document.createElement("option");
                    opt.value = u.id;
                    opt.textContent = u.username;
                    if (selectedValue && u.id === selectedValue) {
                        opt.selected = true;
                    }
                    select.appendChild(opt);
                });
        }

        render("", selectedId);
        search.addEventListener("input", () => render(search.value, selectedId));

        return select;
    }

    fetch("/api/project/projects/?users_only=true")
        .then(res => res.json())
        .then(data => {
            studentsList = data.students || [];
            teachersList = data.teachers || [];

            createCheckboxListWithSearch(studentWrapper, "Students:", studentsList, [], "student_ids");
            supervisorSelect = createSearchableSelect(supervisorWrapper, "Supervisor:", teachersList, null);
            readerSelect = createSearchableSelect(readerWrapper, "Reader:", teachersList, null);
            renderJudgesCheckboxes(teachersList, []);

            setupEditButtons();
            setupDeleteButtons();
        });

    function renderJudgesCheckboxes(list, selectedIds = []) {
        judgeContainer.innerHTML = "";

        const search = document.createElement("input");
        search.type = "text";
        search.placeholder = "🔍 Search judges...";
        judgeContainer.appendChild(search);

        const listContainer = document.createElement("div");
        listContainer.classList.add("judge-list");
        judgeContainer.appendChild(listContainer);

        function renderList(filter = "") {
            listContainer.innerHTML = "";
            list
                .filter(user => user.username.toLowerCase().includes(filter.toLowerCase()))
                .forEach(user => {
                    const label = document.createElement("label");
                    const cb = document.createElement("input");
                    cb.type = "checkbox";
                    cb.value = user.id;
                    if (selectedIds.includes(user.id)) cb.checked = true;

                    cb.addEventListener("change", () => {
                        const checked = listContainer.querySelectorAll("input[type=checkbox]:checked");
                        if (checked.length > 5) {
                            cb.checked = false;
                            showAlert("You can select up to 5 committee members.", 'warning');
                        }
                    });

                    label.appendChild(cb);
                    label.append(" " + user.username);
                    listContainer.appendChild(label);
                });
        }

        renderList();
        search.addEventListener("input", () => renderList(search.value));
    }

    function setupEditButtons() {
        document.querySelectorAll(".edit-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                const res = await fetch(`/api/project/projects/${id}/`);
                const project = await res.json();

                idField.value = project.id;
                nameInput.value = project.name;
                descriptionInput.value = project.description;
                fieldInput.value = project.field;
                yearInput.value = project.academic_year;
                deptInput.value = project.department?.id;
                countInput.value = project?.team_member_count || "";
                countInput.dispatchEvent(new Event("input"));

                let supervisorId = null;
                let readerId = null;
                let judgeIds = [];

                if (project.memberships) {
                    project.memberships.forEach(m => {
                        if (m.role === ROLE.SUPERVISOR) supervisorId = m.user_id;
                        else if (m.role === ROLE.READER) readerId = m.user_id;
                        else if (m.role === ROLE.JUDGE) judgeIds.push(m.user_id);
                    });
                }

                createCheckboxListWithSearch(studentWrapper, "Students:", studentsList, project.student_ids || [], "student_ids");
                supervisorSelect = createSearchableSelect(supervisorWrapper, "Supervisor:", teachersList, supervisorId);
                readerSelect = createSearchableSelect(readerWrapper, "Reader:", teachersList, readerId);
                renderJudgesCheckboxes(teachersList, judgeIds);

                modal.style.display = "flex";
                modal.classList.remove("hidden");
                document.getElementById("modal-title").textContent = "Edit Project";
            });
        });
    }

    function setupDeleteButtons() {
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                const confirmed = await confirmAction("Are you sure you want to delete this project?");
                if (!confirmed) return;

                const res = await fetch(`/api/project/projects/${id}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                });

                if (res.ok) {
                    location.reload();
                } else {
                    showAlert("Failed to delete project.", 'error');
                }
            });
        });
    }

    createBtn?.addEventListener("click", () => {
        form.reset();
        idField.value = "";

        const deptId = deptInput.dataset.deptId;
        if (deptId) deptInput.value = deptId;

        const now = new Date();
        const year = now.getMonth() >= 7 ? now.getFullYear() : now.getFullYear() - 1;
        yearInput.value = `${year}-${year + 1}`;
        countInput.value = "";

        createCheckboxListWithSearch(studentWrapper, "Students:", studentsList, [], "student_ids");
        supervisorSelect = createSearchableSelect(supervisorWrapper, "Supervisor:", teachersList, null);
        readerSelect = createSearchableSelect(readerWrapper, "Reader:", teachersList, null);
        renderJudgesCheckboxes(teachersList, []);

        modal.style.display = "flex";
        modal.classList.remove("hidden");
        document.getElementById("modal-title").textContent = "Add Project";
    });

    closeBtn?.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.style.display = "none";
    });

    form?.addEventListener("submit", async (e) => {
        e.preventDefault();

        const student_ids = Array.from(studentWrapper.querySelectorAll("input[type=checkbox]:checked")).map(cb => parseInt(cb.value));
        const memberships = [];

        const addMember = (val, role) => {
            if (val) memberships.push({ user_id: parseInt(val), role: role, group_id: null });
        };

        addMember(supervisorSelect?.value, ROLE.SUPERVISOR);
        addMember(readerSelect?.value, ROLE.READER);
        judgeContainer.querySelectorAll("input[type=checkbox]:checked").forEach(cb => {
            addMember(cb.value, ROLE.JUDGE);
        });

        const teamLimit = parseInt(countInput.value);
        if (student_ids.length > teamLimit) {
            showAlert(`You can only select up to ${teamLimit} student(s).`, "warning");
            return;
        }

        const data = {
            name: nameInput.value,
            description: descriptionInput.value,
            field: fieldInput.value,
            department_id: parseInt(deptInput.value),
            academic_year: yearInput.value,
            team_member_count: teamLimit,
            student_ids,
            memberships
        };

        const projectId = idField.value;
        const url = projectId ? `/api/project/projects/${projectId}/` : "/api/project/projects/";
        const method = projectId ? "PUT" : "POST";

        const res = await fetch(url, {
            method,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            location.reload();
        } else {
            const err = await res.json();
            showAlert("Failed to save project: " + JSON.stringify(err), 'error');
        }
    });

    const searchInput = document.getElementById("search-input");
const departmentFilter = document.getElementById("department-filter");

function applyFilters() {
    const query = searchInput?.value.toLowerCase() || "";
    const selectedDept = departmentFilter?.value.toLowerCase() || "";

    document.querySelectorAll(".project-card").forEach(card => {
        const name = card.querySelector("h4")?.innerText.toLowerCase() || "";
        const academicYear = card.querySelector("p:nth-child(4)")?.innerText.toLowerCase() || "";
        const supervisor = card.querySelector("p:nth-child(5)")?.innerText.toLowerCase() || "";
        const department = card.querySelector("p:nth-child(3)")?.innerText.toLowerCase() || "";

        const matchesSearch = (
            name.includes(query) || 
            academicYear.includes(query) || 
            supervisor.includes(query)
        );

        const matchesDepartment = selectedDept === "" || department.includes(selectedDept);

        if (matchesSearch && matchesDepartment) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

searchInput?.addEventListener("input", applyFilters);
departmentFilter?.addEventListener("change", applyFilters);

});
