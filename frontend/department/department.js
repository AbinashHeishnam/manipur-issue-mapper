const token = localStorage.getItem("dept_token");
const deptName = localStorage.getItem("dept_name");

if (!token) {
    window.location.href = "../login.html";
}

if (deptName) {
    const deptNameEl = document.getElementById("deptName");
    if (deptNameEl) {
        deptNameEl.innerText = deptName; // Should say "Sanitation Department"
        deptNameEl.style.color = "var(--primary)";
    }

    // Update subtitle for context
    const subtitle = document.querySelector(".branding-text p");
    if (subtitle) {
        subtitle.innerText = "Official Department Dashboard";
        subtitle.style.fontWeight = "500";
    }
}

// ----- Globals -----
let allIssues = [];
const dateFilter = document.getElementById("dateFilter");

// ----- Fetch Issues -----
async function loadIssues() {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/department/issues', {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.status === 401) {
            alert("Session expired");
            localStorage.removeItem("dept_token");
            window.location.href = "../login.html";
            return;
        }

        const result = await res.json();

        const tableBody = document.getElementById("issueTableBody");
        if (tableBody) tableBody.innerHTML = "";

        if (result.status === 'success') {
            allIssues = result.issues || [];
            renderTable(allIssues);
        } else {
            console.error("Failed to load issues");
        }
    } catch (err) {
        console.error(err);
    }
}

// ----- Render Table -----
function renderTable(issues) {
    const tableBody = document.getElementById("issueTableBody");
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (issues.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center; padding: 40px; color: var(--text-muted);'>No issues assigned to you yet.</td></tr>";
        return;
    }

    issues.forEach((issue, idx) => {
        let severityColor = "green";
        if (issue.ai_severity > 0.4) severityColor = "orange";
        if (issue.ai_severity > 0.7) severityColor = "red";

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${idx + 1}</td>
            <td>${issue.title}</td>
            <td style="font-size: 0.9rem; color: #666;">${window.timeAgo ? window.timeAgo(issue.timestamp) : new Date(issue.timestamp).toLocaleDateString()}</td>
            <td>${issue.address || 'Loading...'}</td>
            <td><span class="${issue.status === 'Resolved' ? 'status-approved' : 'status-inprogress'}">${issue.status}</span></td>
            <td style="color:${severityColor}; font-weight:bold;">${(issue.ai_severity * 10).toFixed(1)}/10</td>
            <td>
                <button class="btn btn-primary" onclick="window.location.href='update.html?id=${issue.id}'">
                    Update Progress
                </button>
            </td>
        `;
        tableBody.appendChild(tr);

        // Lazy load address if missing
        if (!issue.address && issue.latitude) {
            fetchAddress(issue.latitude, issue.longitude, tr);
        }
    });
}

// ----- Address Fetcher -----
async function fetchAddress(lat, lng, tr) {
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
        const data = await res.json();
        if (tr.children[2]) tr.children[2].innerText = data.display_name || "Unknown";
    } catch (e) { console.error(e); }
}

// ----- Filter Logic -----
function applyFilters() {
    const selectedDate = dateFilter ? dateFilter.value : null;

    if (!selectedDate) {
        renderTable(allIssues);
        return;
    }

    const filtered = allIssues.filter(issue => {
        const issueDate = new Date(issue.timestamp).toISOString().split('T')[0];
        return issueDate === selectedDate;
    });

    renderTable(filtered);
}

function clearFilters() {
    if (dateFilter) dateFilter.value = "";
    renderTable(allIssues);
}

if (dateFilter) dateFilter.addEventListener("change", applyFilters);

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
        localStorage.removeItem("dept_token");
        localStorage.removeItem("dept_name");
        window.location.href = "../login.html";
    });
}

loadIssues();
