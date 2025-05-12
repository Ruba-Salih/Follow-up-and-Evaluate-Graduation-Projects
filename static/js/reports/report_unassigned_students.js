document.addEventListener("DOMContentLoaded", () => {
    const tbody = document.getElementById("students-table-body");
    const searchInput = document.getElementById("student-search");

    fetch("/api/report/report-view/?type=non_assigned_students")
        .then(res => res.json())
        .then(data => {
            data.forEach(student => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${student.student_id || "—"}</td>
                    <td>${student.first_name} ${student.last_name}</td>
                    <td>${student.department || "—"}</td>
                `;
                tbody.appendChild(row);
            });
        });

    searchInput?.addEventListener("input", () => {
        const val = searchInput.value.toLowerCase();
        document.querySelectorAll("tbody tr").forEach(row => {
            const studentId = row.children[0]?.textContent.toLowerCase() || "";
            const studentName = row.children[1]?.textContent.toLowerCase() || "";
            row.style.display = studentId.includes(val) || studentName.includes(val) ? "" : "none";
        });
    });
});
