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
    const statusLower = (issue.status || "").toLowerCase();

    // Priority 1: Final States
    if (statusLower === "resolved") return { text: "Resolved", class: "status-approved" }; // Green
    if (statusLower === "rejected") return { text: "Rejected", class: "status-rejected" }; // Red

    // Priority 2: Work in Progress
    if (statusLower === "in progress") return { text: "In Progress", class: "status-inprogress" }; // Blue

    // Priority 3: Admin Approval (Fallback if status is just 'Pending' but flag is set... though usually flag set means In Progress)
    if (issue.approved_by_admin === 1) return { text: "Approved & Assigned", class: "status-approved" };

    // Default
    return { text: "Pending", class: "status-pending" };
}

// ----- Filter Globals -----
let allIssues = [];
const dateFilter = document.getElementById("dateFilter");
const categoryFilter = document.getElementById("categoryFilter");

// ----- Fetch and render issues -----
async function loadIssues() {
    const tableBody = document.getElementById("issueTableBody");
    tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center; padding: 40px;'>Loading issues...</td></tr>";

    try {
        // Get user ID from localStorage or default to 1 (fallback)
        const userId = localStorage.getItem('user_id') || 1;
        const res = await fetch(`http://127.0.0.1:8000/api/issues/?user_id=${userId}`);
        const data = await res.json();

        if (data.status !== "success" || !data.data.length) {
            tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center; padding: 40px; color: var(--text-muted);'>No issues reported yet</td></tr>";
            return;
        }

        allIssues = data.data; // Store for filtering
        renderTable(allIssues);

    } catch (err) {
        console.error("Error fetching issues:", err);
        tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center; color: var(--danger);'>Server connection failed</td></tr>";
    }
}

async function renderTable(issues) {
    const tableBody = document.getElementById("issueTableBody");
    tableBody.innerHTML = "";

    if (issues.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center; padding: 40px; color: var(--text-muted);'>No matching issues found</td></tr>";
        return;
    }

    // We can't use await inside forEach efficiently for async getAddress, 
    // but typically you shouldn't geocode 50 items at once.
    // For now, let's just do it sequentially or parallel map.

    // Note: Reverse geocoding in a loop is slow and might get rate limited.
    // Ideally the backend provides the address. Assuming backend issue object has it or we skip it.
    // The previous code did it inside loop. I'll maintain that pattern but be careful.

    for (let i = 0; i < issues.length; i++) {
        const issue = issues[i];

        // This is slow, but preserving existing functionality
        // Optimization: Use issue.location from DB if available
        let address = issue.location || issue.address;
        if (!address) {
            address = await getAddress(issue.latitude, issue.longitude);
        }

        const statusObj = getStatusText(issue);

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${issue.user_id || "-"}</td>
            <td>${issue.category}</td>
            <td style="font-size: 0.9rem; color: #666;">${window.timeAgo ? window.timeAgo(issue.timestamp) : new Date(issue.timestamp).toLocaleDateString()}</td>
            <td>${address}</td>
            <td>
                <button class="btn" onclick="viewIssue(${issue.id})">View More</button>
            </td>
            <td class="${statusObj.class}">${statusObj.text}</td>
        `;
        tableBody.appendChild(tr);
    }
}

// ----- Filter Functions -----
function applyFilters() {
    const selectedDate = dateFilter.value;
    const selectedCat = categoryFilter.value;

    const filtered = allIssues.filter(issue => {
        if (selectedDate) {
            const issueDate = new Date(issue.timestamp).toISOString().split('T')[0];
            if (issueDate !== selectedDate) return false;
        }
        if (selectedCat && issue.category !== selectedCat) return false;
        return true;
    });

    renderTable(filtered);
}

function clearFilters() {
    dateFilter.value = "";
    categoryFilter.value = "";
    renderTable(allIssues);
}

if (dateFilter) dateFilter.addEventListener("change", applyFilters);
if (categoryFilter) categoryFilter.addEventListener("change", applyFilters);

// ----- Navigate to issue detail -----
function viewIssue(id) {
    window.location.href = `issue.html?id=${id}`;
}

// ----- Filter Dropdown Logic -----
const filterToggleBtn = document.getElementById("filterToggleBtn");
const filterDropdown = document.getElementById("filterDropdown");

if (filterToggleBtn && filterDropdown) {
    filterToggleBtn.onclick = (e) => {
        e.stopPropagation();
        filterDropdown.classList.toggle("active");
    };

    // Close on outside click
    document.addEventListener("click", (e) => {
        if (!filterDropdown.contains(e.target) && !filterToggleBtn.contains(e.target)) {
            filterDropdown.classList.remove("active");
        }
    });
}

// ----- Initialize -----
loadIssues();
