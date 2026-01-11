// ----- Helper: Get address from lat/lng -----
async function getAddress(lat, lng) {
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
        const data = await res.json();
        return data.display_name || "Unknown location";
    } catch (err) {
        console.error("Reverse geocoding error:", err);
        return "Unknown location";
    }
}

// ----- Map status to display text and color -----
function getStatusText(issue) {
    if (issue.approved_by_admin === 1) return { text: "Approved", class: "status-approved" };
    if (issue.approved_by_admin === 0 && issue.status.toLowerCase() === "pending") return { text: "Pending", class: "status-pending" };
    if (issue.approved_by_admin === 0 && issue.status.toLowerCase() === "rejected") return { text: "Rejected", class: "status-rejected" };
    if (issue.status.toLowerCase() === "in progress") return { text: "In Progress", class: "status-inprogress" };
    return { text: issue.status, class: "" };
}

// ----- Fetch and render issues -----
async function loadIssues() {
    const tableBody = document.getElementById("issueTableBody");
    tableBody.innerHTML = "<tr><td colspan='6'>Loading...</td></tr>";

    try {
        // Get user ID from localStorage or default to 1 (fallback)
        const userId = localStorage.getItem('user_id') || 1;
        const res = await fetch(`http://127.0.0.1:8000/api/issues/?user_id=${userId}`);
        const data = await res.json();

        if (data.status !== "success" || !data.data.length) {
            tableBody.innerHTML = "<tr><td colspan='6'>No issues reported</td></tr>";
            return;
        }

        tableBody.innerHTML = "";

        for (let i = 0; i < data.data.length; i++) {
            const issue = data.data[i];

            const address = await getAddress(issue.latitude, issue.longitude);

            const statusObj = getStatusText(issue);

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${i + 1}</td>
                <td>${issue.user_id || "-"}</td>
                <td>${issue.category}</td>
                <td>${address}</td>
                <td>
                    <button class="btn" onclick="viewIssue(${issue.id})">View More</button>
                </td>
                <td class="${statusObj.class}">${statusObj.text}</td>
            `;
            tableBody.appendChild(tr);
        }
    } catch (err) {
        console.error("Error fetching issues:", err);
        tableBody.innerHTML = "<tr><td colspan='6'>Server unavailable</td></tr>";
    }
}

// ----- Navigate to issue detail -----
function viewIssue(id) {
    window.location.href = `issue.html?id=${id}`;
}

// ----- Add CSS for status -----
const style = document.createElement("style");
style.innerHTML = `
    .status-approved { color: green; font-weight: bold; }
    .status-pending { color: orange; font-weight: bold; }
    .status-rejected { color: red; font-weight: bold; }
    .status-inprogress { color: blue; font-weight: bold; }
`;
document.head.appendChild(style);

// ----- Initialize -----
loadIssues();
