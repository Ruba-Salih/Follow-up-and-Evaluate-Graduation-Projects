document.addEventListener("DOMContentLoaded", () => {
    const tbody = document.getElementById("coordinator-table-body");
    const searchInput = document.getElementById("coord-search");
    const deptFilter = document.getElementById("dept-filter");
    const downloadBtn = document.getElementById("download-btn");

    let originalData = [];

    fetch("/api/report/report-view/?type=projects_by_coordinator")
        .then(res => res.json())
        .then(data => {
            originalData = data;
            populateDepartmentFilter(data);
            renderTable(data);
        });

    function renderTable(data) {
        tbody.innerHTML = "";
        data.forEach((entry, index) => {
            const projectNames = entry.projects.map(p => p.name).join("<br>-");
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${entry.coordinator}</td>
                <td>-${projectNames || "—"}</td>
                <td>${entry.department || "—"}</td>
            `;
            tbody.appendChild(row);
        });
    }

    function populateDepartmentFilter(data) {
        const departments = new Set(data.map(d => d.department).filter(Boolean));
        departments.forEach(dept => {
            const option = document.createElement("option");
            option.value = dept;
            option.textContent = dept;
            deptFilter.appendChild(option);
        });
    }

    function applyFilters() {
        const name = searchInput.value.toLowerCase();
        const dept = deptFilter.value;

        document.querySelectorAll("#coordinator-table-body tr").forEach(row => {
            const coordText = row.children[1]?.textContent.toLowerCase() || "";
            const deptText = row.children[3]?.textContent || "";
            const match = coordText.includes(name) && (!dept || dept === deptText);
            row.style.display = match ? "" : "none";
        });
    }

    searchInput?.addEventListener("input", applyFilters);
    deptFilter?.addEventListener("change", applyFilters);

    downloadBtn?.addEventListener("click", () => {
        let csv = "Coordinator,Projects,Department\n";
        document.querySelectorAll("#coordinator-table-body tr").forEach(row => {
            if (row.style.display !== "none") {
                const cells = Array.from(row.children).map(td => `"${td.textContent.trim().replace(/\n/g, ' ')}"`);
                csv += cells.join(",") + "\n";
            }
        });

        const blob = new Blob([csv], { type: "text/csv" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "projects_by_coordinator.csv";
        link.click();
    });
});
