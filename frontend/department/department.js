const token = localStorage.getItem("dept_token");
const deptName = localStorage.getItem("dept_name");

if (!token) {
    window.location.href = "../login.html";
}

if (deptName) {
    document.getElementById("deptName").innerText = deptName;
    // Update subtitle for context
    const subtitle = document.querySelector(".branding-text p");
    if (subtitle) subtitle.innerText = `Official ${deptName} Dashboard`;
}

async function fetchMyIssues() {
    const tbody = document.getElementById('issueTableBody');

    try {
        const res = await fetch('http://127.0.0.1:8000/api/department/issues', {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.status === 401) {
            alert("Session expired");
            window.location.href = "../login.html";
            return;
        }

        const result = await res.json();

        if (result.status !== "success") throw new Error(result.message || "Failed to load");

        const issues = result.issues || [];
        tbody.innerHTML = '';

        if (issues.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No issues assigned to you yet.</td></tr>`;
            return;
        }

        issues.forEach((issue, idx) => {
            const tr = document.createElement('tr');

            // AI Severity color
            let severityColor = "white";
            if (issue.ai_severity >= 0.8) severityColor = "var(--dange)";
            else if (issue.ai_severity >= 0.5) severityColor = "var(--accent)";

            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td>${issue.title}</td>
                <td>${issue.address || 'Loading...'}</td>
                <td><span class="status-inprogress">Assigned</span></td>
                <td style="color:${severityColor}; font-weight:bold;">${(issue.ai_severity * 10).toFixed(1)}/10</td>
                <td>
                    <button class="btn btn-primary" onclick="alert('Work update feature coming soon!')">
                        Update Progress
                    </button>
                </td>
            `;
            tbody.appendChild(tr);

            if (!issue.address && issue.latitude) {
                fetchAddress(issue.latitude, issue.longitude, tr);
            }
        });

    } catch (err) {
        console.error(err);
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--dange);">Error loading data</td></tr>`;
    }
}

async function fetchAddress(lat, lng, tr) {
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
        const data = await res.json();
        if (tr.children[2]) tr.children[2].innerText = data.display_name || "Unknown";
    } catch (e) { console.error(e); }
}

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("dept_token");
    localStorage.removeItem("dept_name");
    window.location.href = "../login.html";
});

fetchMyIssues();
