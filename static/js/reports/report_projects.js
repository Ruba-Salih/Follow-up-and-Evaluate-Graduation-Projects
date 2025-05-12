document.addEventListener("DOMContentLoaded", () => {
    const tbody = document.getElementById("projects-table-body");
    const search = document.getElementById("project-search");
    const departmentFilter = document.getElementById("filter-department");
    const supervisorFilter = document.getElementById("filter-supervisor");
    const downloadBtn = document.getElementById("download-btn");

    let projectsData = [];

    fetch("/api/report/report-view/?type=projects")
        .then(res => res.json())
        .then(data => {
            projectsData = data;
            renderTable(data);
            populateFilters(data);
        });

    function renderTable(data) {
        tbody.innerHTML = "";
        data.forEach((project, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${project.name}</td>
                <td>${project.field?.name || "—"}</td>
                <td>${project.department?.name || "—"}</td>
                <td>${project.supervisor?.full_name || "—"}</td>
                <td>${project.team_members?.map(m => m.full_name || m.username).join(", ") || "—"}</td>
            `;
            tbody.appendChild(row);
        });
    }

    function populateFilters(data) {
        const departments = new Set();
        const supervisors = new Set();

        data.forEach(p => {
            if (p.department?.name) departments.add(p.department.name);
            if (p.supervisor?.full_name) supervisors.add(p.supervisor.full_name);
        });

        [...departments].sort().forEach(d => {
            const option = document.createElement("option");
            option.value = d;
            option.textContent = d;
            departmentFilter.appendChild(option);
        });

        [...supervisors].sort().forEach(s => {
            const option = document.createElement("option");
            option.value = s;
            option.textContent = s;
            supervisorFilter.appendChild(option);
        });
    }

    function filterTable() {
        const query = search.value.toLowerCase();
        const dept = departmentFilter.value;
        const sup = supervisorFilter.value;

        const rows = tbody.querySelectorAll("tr");
        rows.forEach(row => {
            const nameCell = row.children[1];
            const deptCell = row.children[3];
            const supCell = row.children[4];
            const matches =
                nameCell.textContent.toLowerCase().includes(query) &&
                (!dept || deptCell.textContent === dept) &&
                (!sup || supCell.textContent === sup);
            row.style.display = matches ? "" : "none";
        });
    }

    search.addEventListener("input", filterTable);
    departmentFilter.addEventListener("change", filterTable);
    supervisorFilter.addEventListener("change", filterTable);

    // Column toggle
    document.querySelectorAll(".col-toggle").forEach(cb => {
        cb.addEventListener("change", () => {
            const index = parseInt(cb.dataset.col);
            document.querySelectorAll("table tr").forEach(row => {
                const cell = row.children[index];
                if (cell) cell.style.display = cb.checked ? "none" : "";
            });
        });
    });

    // CSV download
    downloadBtn.addEventListener("click", () => {
        const rows = [["#", "Project Name", "Field", "Department", "Supervisor", "Team Members"]];
        let index = 1;
        document.querySelectorAll("#projects-table-body tr").forEach(row => {
            if (row.style.display !== "none") {
                const cells = Array.from(row.children).map(td => `"${td.textContent.trim()}"`);
                cells[0] = index++;  // Reassign numbering
                rows.push(cells);
            }
        });

        const csvContent = rows.map(e => e.join(",")).join("\n");
        const blob = new Blob([csvContent], { type: "text/csv" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "projects_report.csv";
        link.click();
    });
});
