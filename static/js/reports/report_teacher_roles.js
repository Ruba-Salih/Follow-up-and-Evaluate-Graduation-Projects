document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("teacher-table-body");
    const roleFilter = document.getElementById("role-filter");
    const downloadBtn = document.getElementById("download-btn");

    let allData = [];

    // Load data from API
    fetch("/api/report/report-view/?type=teacher_roles")
        .then(res => res.json())
        .then(data => {
            allData = data;
            renderTable(data);
        });

    // Render table rows
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

    // Filter by role
    roleFilter?.addEventListener("change", () => {
        const selected = roleFilter.value;
        if (!selected) {
            renderTable(allData);
            return;
        }

        const filtered = allData.filter(item => item.role === selected);
        renderTable(filtered);
    });

    // Download as CSV
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
