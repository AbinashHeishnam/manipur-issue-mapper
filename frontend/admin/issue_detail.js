const token = localStorage.getItem("admin_token");
if (!token) window.location.href = "admin.html";

const urlParams = new URLSearchParams(window.location.search);
const issueId = urlParams.get('id');
if (!issueId) window.location.href = "admin.html";

// Elements
const titleEl = document.getElementById("issueTitle");
const categoryEl = document.getElementById("issueCategory");
const statusEl = document.getElementById("issueStatus");
const locationEl = document.getElementById("issueLocation");
const severityEl = document.getElementById("issueSeverity");

const deptSelect = document.getElementById("departmentSelect");
const commentInput = document.getElementById("adminComment");
const rejectBtn = document.getElementById("rejectBtn");
const approveBtn = document.getElementById("approveBtn");

let currentIssue = null;

// ----- Load Issue -----
async function loadIssue() {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/issues/${issueId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const result = await res.json();

        if (result.status !== "success") throw new Error(result.message || "Failed to load");

        const issue = result.data;
        currentIssue = issue;

        titleEl.innerText = issue.title || "No Title";
        categoryEl.innerText = issue.category || "General";
        statusEl.innerText = issue.status || "Pending";

        // Description
        const descEl = document.getElementById("issueDescription");
        if (descEl) descEl.innerText = issue.description || "No description provided.";

        // Reporter Info
        if (document.getElementById("userName")) document.getElementById("userName").innerText = issue.user_name || "Anonymous";
        if (document.getElementById("userMobile")) document.getElementById("userMobile").innerText = issue.user_mobile || "N/A";
        if (document.getElementById("userEmail")) document.getElementById("userEmail").innerText = issue.user_email || "N/A";

        // Address
        if (issue.address) {
            locationEl.innerText = issue.address;
        } else {
            // lazy fetch address
            fetchAddress(issue.latitude, issue.longitude);
        }

        // AI Severity
        const severityScore = (issue.ai_severity * 10).toFixed(1);
        severityEl.innerText = `${severityScore}/10`;
        if (issue.ai_severity > 0.7) severityEl.style.color = "var(--dange)";

        // Style Status
        updateStatusStyle(issue.status, issue.approved_by_admin);

        // Populate existing admin data
        if (issue.admin_comment) commentInput.value = issue.admin_comment;
        if (issue.assigned_department) {
            deptSelect.value = issue.assigned_department;
            const displayDept = document.getElementById("displayDept");
            if (displayDept) displayDept.innerText = issue.assigned_department;
        }

        // ----- LOCKING LOGIC -----
        // User Request: "non updatabale after resolved or making it in progress"
        // Interpretation: If Admin has approved it (In Progress/Resolved), Admin cannot change it.
        // If it is Pending or Rejected, Admin CAN change it.
        if (issue.approved_by_admin === 1) {
            // Already Approved
            approveBtn.disabled = true;
            rejectBtn.disabled = true;
            approveBtn.innerText = "Already Assigned";
            approveBtn.title = "Decision cannot be changed once assigned";

            // Also disable inputs
            deptSelect.disabled = true;
            commentInput.disabled = true;
        }

        // Disable buttons if already processed (optional, depending on workflow)
        /*
        if (issue.status === 'Rejected' || issue.approved_by_admin) {
            approveBtn.disabled = true;
            rejectBtn.disabled = true;
        }
        */

    } catch (err) {
        alert("Failed to load issue: " + err.message);
        window.location.href = "admin.html";
    }
}

async function fetchAddress(lat, lng) {
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
        const data = await res.json();
        locationEl.innerText = data.display_name || `Lat: ${lat}, Lng: ${lng}`;
    } catch (e) {
        locationEl.innerText = `Lat: ${lat}, Lng: ${lng}`;
    }
}

function updateStatusStyle(status, approved) {
    statusEl.className = "detail-value"; // reset
    if (approved === 1) {
        statusEl.style.color = "#166534";
        statusEl.innerText = "Approved & Assigned";
    } else if (status === "Rejected") {
        statusEl.style.color = "#991b1b";
    } else {
        statusEl.style.color = "#b45309"; // Pending
    }
}

// ----- Actions -----

rejectBtn.onclick = () => submitDecision(false);
approveBtn.onclick = () => submitDecision(true);

async function submitDecision(isApproved) {
    const comment = commentInput.value.trim();
    const department = deptSelect.value;

    if (isApproved && !department) {
        alert("Please assign a department before approving.");
        return;
    }

    if (!isApproved && !comment) {
        if (!confirm("Rejecting without a comment? It's better to provide a reason.")) return;
    }

    const payload = {
        approved: isApproved,
        status: isApproved ? "In Progress" : "Rejected",
        admin_comment: comment
    };

    if (isApproved) payload.department = department;

    // UX Updates
    const btn = isApproved ? approveBtn : rejectBtn;
    const oldText = btn.innerText;
    btn.innerText = "Processing...";
    btn.disabled = true;
    rejectBtn.disabled = true;
    approveBtn.disabled = true;

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/admin/issues/${issueId}/approve`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Server Error");

        if (data.status === "success") {
            alert(isApproved ? "Issue approved and assigned!" : "Issue rejected.");
            window.location.href = "admin.html";
        } else {
            throw new Error(data.message || "Unknown error");
        }

    } catch (err) {
        console.error(err);
        alert("Action failed: " + err.message);
        btn.innerText = oldText;
        rejectBtn.disabled = false;
        approveBtn.disabled = false;
    }
}

loadIssue();
