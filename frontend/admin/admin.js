const token = localStorage.getItem("admin_token");
if (!token) {
    window.location.href = "../login.html";
}

async function fetchIssues() {
    const tbody = document.getElementById('issueTableBody');

    try {
        const res = await fetch('http://127.0.0.1:8000/api/admin/issues', {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.status === 401) {
            localStorage.removeItem("admin_token");
            window.location.href = "../login.html";
            return;
        }

        const result = await res.json();

        if (result.status !== "success") throw new Error("API returned error");

        tbody.innerHTML = '';
        const issues = result.issues || [];

        if (issues.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No issues found</td></tr>`;
            return;
        }

        issues.forEach((issue, idx) => {
            let statusClass = "status-pending"; // Default
            const statusLower = (issue.status || "").toLowerCase();

            if (issue.approved_by_admin === 1) statusClass = "status-approved";
            else if (statusLower === "rejected") statusClass = "status-rejected";
            else if (statusLower === "in progress") statusClass = "status-inprogress";

            // Address: Use what's in DB or static text "View Map" to avoid 429 errors
            const address = issue.address || `Lat: ${issue.latitude}, Lng: ${issue.longitude}`;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td>${issue.title}</td>
                <td>${issue.user_id || '-'}</td>
                <td>${issue.category}</td>
                <td style="font-size:0.85rem; max-width: 200px; overflow:hidden; text-overflow:ellipsis;">${address}</td>
                <td><span class="${statusClass}">${issue.status || "Pending"}</span></td>
                <td>${issue.assigned_department || '-'}</td>
                <td>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.85rem;" 
                        onclick="window.location.href='issue_detail.html?id=${issue.id}'">
                        Manage
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--dange);">Failed to load data. Is backend running?</td></tr>`;
    }
}

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("admin_token");
    window.location.href = "../login.html";
});

fetchIssues();
