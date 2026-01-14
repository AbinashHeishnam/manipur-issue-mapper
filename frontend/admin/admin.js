const token = localStorage.getItem("admin_token");
if (!token) {
    window.location.href = "../login.html";
}

// ----- Filter Globals -----
let allIssues = [];
const dateFilter = document.getElementById("dateFilter");
const categoryFilter = document.getElementById("categoryFilter");

// ----- Fetch Issues -----
async function loadIssues() {
    console.log("Admin: Loading issues...");
    try {
        const res = await fetch('http://127.0.0.1:8000/api/admin/issues', {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.status === 401) {
            console.warn("Unauthorized, redirecting...");
            localStorage.removeItem("admin_token");
            window.location.href = "../login.html";
            return;
        }

        const data = await res.json();

        const tableBody = document.querySelector("#issueTableBody");
        if (tableBody) tableBody.innerHTML = "";

        if (data.status === 'success') {
            allIssues = data.issues || [];
            console.log(`Loaded ${allIssues.length} issues.`);
            renderTable(allIssues);
        } else {
            console.error("API returned error:", data.message);
            if (tableBody) tableBody.innerHTML =
                `<tr><td colspan="11" style="text-align:center; color: var(--dange);">Failed to load data: ${data.message || 'Unknown error'}</td></tr>`;
        }
    } catch (err) {
        console.error("Fetch Error:", err);
        const tableBody = document.querySelector("#issueTableBody");
        if (tableBody) tableBody.innerHTML =
            `<tr><td colspan="11" style="text-align:center; color: var(--dange);">Failed to load data. Backend check required.</td></tr>`;
    }
}

// ----- Quick Reject (AI) -----
async function quickReject(issueId) {
    const ok = confirm("Reject this issue as suspicious (AI flagged)?");
    if (!ok) return;

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/admin/issues/${issueId}/approve`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                approved: false,
                admin_comment: "Rejected: AI flagged as suspicious/spam"
            })
        });

        const data = await res.json();

        if (data.status === "success") {
            if (window.showToast) window.showToast("Issue rejected (AI).", "success");
            loadIssues(); // refresh
        } else {
            if (window.showToast) window.showToast("Reject failed: " + (data.message || "Unknown error"), "error");
        }
    } catch (err) {
        console.error(err);
        if (window.showToast) window.showToast("Reject failed. Backend error.", "error");
    }
}

// ----- Render Table -----
function renderTable(issuesToRender) {
    const tableBody = document.querySelector("#issueTableBody");
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (issuesToRender.length === 0) {
        tableBody.innerHTML =
            "<tr><td colspan='11' style='text-align:center; padding: 40px; color: var(--text-muted);'>No issues found</td></tr>";
        return;
    }

    issuesToRender.forEach((issue, index) => {
        try {
            // ---------------- Status Logic ----------------
            let statusText = issue.status || "Pending";
            let statusClass = "status-pending";
            const statusLower = (statusText || "").toLowerCase();

            if (statusLower === "resolved") {
                statusClass = "status-approved";
                statusText = "Resolved";
            } else if (statusLower === "in progress") {
                statusClass = "status-inprogress";
            } else if (statusLower === "rejected") {
                statusClass = "status-rejected";
                statusText = "Rejected";
            } else if (issue.approved_by_admin === 1) {
                statusClass = "status-approved";
                statusText = "Approved";
            }

            // ---------------- Address ----------------
            const address = issue.address || `Lat: ${issue.latitude}, Lng: ${issue.longitude}`;

            // ---------------- AI Verdict ----------------
            const aiVerdict = (issue.ai_veracity || "unknown").toLowerCase();
            let aiBadgeText = "Unknown";
            let aiBadgeStyle = "background:#e2e8f0; color:#334155; border:1px solid #cbd5e1;";

            if (aiVerdict === "spam") {
                aiBadgeText = "Spam";
                aiBadgeStyle = "background:#fee2e2; color:#991b1b; border:1px solid #fecaca;";
            } else if (aiVerdict === "legit") {
                aiBadgeText = "Legit";
                aiBadgeStyle = "background:#dcfce7; color:#166534; border:1px solid #bbf7d0;";
            } else if (aiVerdict === "low_quality") {
                aiBadgeText = "Low Quality";
                aiBadgeStyle = "background:#fef9c3; color:#854d0e; border:1px solid #fde68a;";
            }

            const aiBadge = `<span style="display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; font-size:0.8rem; font-weight:700; ${aiBadgeStyle}">
                                🧠 ${aiBadgeText}
                             </span>`;

            // ---------------- Suspicious Flag ----------------
            const isSuspicious = Number(issue.is_suspicious || 0) === 1;
            const suspiciousBadge = isSuspicious
                ? `<span style="display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; font-size:0.8rem; font-weight:700; background:#fee2e2; color:#991b1b; border:1px solid #fecaca;">⚠️ FLAGGED</span>`
                : `<span style="display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; font-size:0.8rem; font-weight:700; background:#dcfce7; color:#166534; border:1px solid #bbf7d0;">✅ OK</span>`;

            // Row highlight for suspicious
            const tr = document.createElement("tr");
            if (isSuspicious) tr.style.background = "rgba(239, 68, 68, 0.06)";

            // Quick Reject button rules
            const alreadyFinal = (statusLower === "rejected" || statusLower === "resolved");
            const showQuickReject = isSuspicious && !alreadyFinal;

            const quickRejectBtn = showQuickReject
                ? `<button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.85rem; margin-top:6px;"
                        onclick="quickReject(${issue.id})">
                        Reject (AI)
                   </button>`
                : "";

            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${issue.title}</td>
                <td>${issue.user_id || '-'}</td>
                <td>${issue.category}</td>
                <td style="font-size: 0.9rem; color: #666;">
                    ${window.timeAgo ? window.timeAgo(issue.timestamp) : new Date(issue.timestamp).toLocaleDateString()}
                </td>
                <td style="font-size:0.85rem; max-width: 200px; overflow:hidden; text-overflow:ellipsis;">
                    ${address}
                </td>
                <td><span class="${statusClass}">${statusText}</span></td>
                <td>${issue.assigned_department || '-'}</td>
                <td>${aiBadge}</td>
                <td>${suspiciousBadge}</td>
                <td>
                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.85rem;" 
                        onclick="window.location.href='issue_detail.html?id=${issue.id}'">
                        Manage
                    </button>
                    ${quickRejectBtn}
                </td>
            `;

            tableBody.appendChild(tr);
        } catch (rowErr) {
            console.error("Error rendering row:", rowErr, issue);
        }
    });
}

// ----- Filter Logic -----
function applyFilters() {
    const selectedDate = dateFilter.value;
    const selectedCat = categoryFilter.value;

    const filtered = allIssues.filter(issue => {
        // Date Filter
        if (selectedDate) {
            const issueDate = new Date(issue.timestamp).toISOString().split('T')[0];
            if (issueDate !== selectedDate) return false;
        }
        // Category Filter
        if (selectedCat && issue.category !== selectedCat) return false;

        return true;
    });

    renderTable(filtered);
}

function clearFilters() {
    if (dateFilter) dateFilter.value = "";
    if (categoryFilter) categoryFilter.value = "";
    renderTable(allIssues);
}

// Event Listeners
if (dateFilter) dateFilter.addEventListener("change", applyFilters);
if (categoryFilter) categoryFilter.addEventListener("change", applyFilters);

// Filter Dropdown Toggle
const filterToggleBtn = document.getElementById("filterToggleBtn");
const filterDropdown = document.getElementById("filterDropdown");

if (filterToggleBtn && filterDropdown) {
    filterToggleBtn.onclick = (e) => {
        e.stopPropagation();
        filterDropdown.classList.toggle("active");
    };

    document.addEventListener("click", (e) => {
        if (!filterDropdown.contains(e.target) && !filterToggleBtn.contains(e.target)) {
            filterDropdown.classList.remove("active");
        }
    });
}

// ----- Logout -----
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("admin_token");
        window.location.href = "../login.html";
    });
}

// ----- Start -----
loadIssues();
