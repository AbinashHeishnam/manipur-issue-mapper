const token = localStorage.getItem("admin_token");
if (!token) {
    window.location.href = "../login.html";
}

async function fetchIssues() {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/admin/issues', {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const result = await res.json();
        if (result.status !== "success") throw new Error("Unauthorized");

        const tbody = document.querySelector('#issues-table tbody');
        tbody.innerHTML = '';

        const issues = result.issues || [];
        issues.forEach((issue, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td>${issue.title}</td>
                <td>${issue.category}</td>
                <td>${issue.address || '-'}</td>
                <td>${issue.status}</td>
                <td>${issue.approved_by_admin ? '✅' : '❌'}</td>
                <td>${issue.assigned_department || '-'}</td>
                <td>
                    <button onclick="window.location.href='issue_detail.html?id=${issue.id}'">
                        View / Update
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Failed to load admin data: " + err.message);
    }
}

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("admin_token");
    window.location.href = "../login.html";
});

fetchIssues();
