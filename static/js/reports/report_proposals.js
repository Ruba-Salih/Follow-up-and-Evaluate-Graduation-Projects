document.addEventListener("DOMContentLoaded", () => {
    const filter = document.getElementById("proposal-filter");
    if (!filter) return;

    filter.addEventListener("input", () => {
        const value = filter.value.toLowerCase();
        document.querySelectorAll("tbody tr").forEach(row => {
            const title = row.children[0].textContent.toLowerCase();
            row.style.display = title.includes(value) ? "" : "none";
        });
    });
});
