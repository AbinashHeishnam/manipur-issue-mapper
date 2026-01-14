const token = localStorage.getItem("dept_token");
if (!token) window.location.href = "../login.html";

const urlParams = new URLSearchParams(window.location.search);
const issueId = urlParams.get('id');
if (!issueId) window.location.href = "department.html";

// Elements
const titleEl = document.getElementById("issueTitle");
const idEl = document.getElementById("issueId");
const dateEl = document.getElementById("issueDate");
const descEl = document.getElementById("issueDesc");
const addressEl = document.getElementById("issueAddress");
const statsEl = document.getElementById("currentStatus");
const statusSelect = document.getElementById("statusSelect");
const noteInput = document.getElementById("completionNote");

// Map
let map, marker;

// ----- Load Issue -----
async function loadIssue() {
    try {
        // First fetch all issues (since we don't have a single GET /issues/:id for dept yet... oh wait, we can reuse admin specific or just filter client side for now since dept/issues returns array. Wait, reusing GET /issues/:id from admin route might fail auth if it requires admin token. 
        // Checking routes: `backend/routes/issues.py` has a public `GET /issues/{issue_id}`? Let's check.
        // If not, dept endpoint only lists all assigned. I'll fetch list and find.
        // Actually, `backend/utils/db_utils.py` has `get_issue_by_id`. `backend/routes/issues.py` exposes public get? 
        // Let's assume public GET is available or I use dept list.

        // Checking `backend/routes/issues.py`... I didn't verify it has GET /{id}. 
        // Admin route has. Let's try fetching from /api/department/issues and finding it.
        const res = await fetch('http://127.0.0.1:8000/api/department/issues', {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const result = await res.json();
        if (result.status !== 'success') throw new Error("Failed to load");

        const issue = result.issues.find(i => i.id == issueId);
        if (!issue) throw new Error("Issue not found or access denied");

        // Render
        titleEl.innerText = issue.title;
        idEl.innerText = issue.id;
        dateEl.innerText = new Date(issue.timestamp).toLocaleDateString();
        descEl.innerText = issue.description;

        if (issue.status) statsEl.innerText = issue.status;
        if (issue.status === 'Resolved') {
            statsEl.className = "status-approved";
            statsEl.style.color = "green";

            // LOCKING: If Resolved, prevent further updates
            document.querySelector('#updateForm button').disabled = true;
            document.querySelector('#updateForm button').innerText = "Issue Closed";
            statusSelect.disabled = true;
            noteInput.disabled = true;
        }

        // Address
        if (issue.address) addressEl.innerText = issue.address;
        else fetchAddress(issue.latitude, issue.longitude);

        // Map
        initMap(issue.latitude, issue.longitude);

    } catch (err) {
        alert(err.message);
        window.location.href = "department.html";
    }
}

// ----- Map -----
function initMap(lat, lng) {
    if (!lat || !lng) return;

    map = L.map('miniMap').setView([lat, lng], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    marker = L.marker([lat, lng]).addTo(map);
}

async function fetchAddress(lat, lng) {
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
        const data = await res.json();
        addressEl.innerText = data.display_name || "Unknown Location";
    } catch (e) { console.error(e); }
}

// ----- Submit Update -----
document.getElementById('updateForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const newStatus = statusSelect.value;
    const note = noteInput.value;

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/department/issues/${issueId}/update`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus, note: note })
        });

        const data = await res.json();
        if (data.status === 'success') {
            alert("Progress Updated Successfully!");
            window.location.href = "department.html";
        } else {
            alert("Error: " + data.detail);
        }
    } catch (err) {
        console.error(err);
        alert("Request failed");
    }
});

loadIssue();
