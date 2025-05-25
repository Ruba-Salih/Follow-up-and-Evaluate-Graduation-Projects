document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("teacher-table-body");
    const roleFilter = document.getElementById("role-filter");
    const teacherSearch = document.getElementById("teacher-search");
    const downloadBtn = document.getElementById("download-btn");

    let allData = [];

    fetch("/api/report/report-view/?type=teacher_roles")
        .then(res => res.json())
        .then(data => {
            allData = data;
            renderTable(data);
        });

    function renderTable(data) {
        tableBody.innerHTML = "";
        data.forEach(item => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${item.teacher}</td>
                <td>${item.project}</td>
                <td>${item.role}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    roleFilter?.addEventListener("change", applyFilters);
    teacherSearch?.addEventListener("input", applyFilters);

    function applyFilters() {
        const roleVal = roleFilter.value.toLowerCase();
        const searchVal = teacherSearch.value.toLowerCase();

        const filtered = allData.filter(item => {
            const matchesRole = !roleVal || item.role.toLowerCase() === roleVal;
            const matchesSearch = !searchVal || item.teacher.toLowerCase().includes(searchVal);
            return matchesRole && matchesSearch;
        });

        renderTable(filtered);
    }

    downloadBtn?.addEventListener("click", () => {
        let csv = "Teacher,Project,Role\n";
        document.querySelectorAll("#teacher-table-body tr").forEach(row => {
            const cells = Array.from(row.children).map(td => `"${td.textContent.trim()}"`);
            csv += cells.join(",") + "\n";
        });

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "teacher_roles.csv";
        a.click();
        URL.revokeObjectURL(url);
    });
});
