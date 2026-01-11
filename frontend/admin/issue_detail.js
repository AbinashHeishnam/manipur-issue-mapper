const token = localStorage.getItem("admin_token");
if (!token) window.location.href = "admin.html";

const urlParams = new URLSearchParams(window.location.search);
const issueId = urlParams.get('id');
if (!issueId) window.location.href = "admin.html";

const titleEl = document.getElementById("title");
const descEl = document.getElementById("description");
const approveEl = document.getElementById("approveSelect");
const deptEl = document.getElementById("departmentInput");
const commentEl = document.getElementById("commentInput");

const saveBtn = document.getElementById("saveBtn");
const backBtn = document.getElementById("backBtn");

// ----- Load Issue -----
async function loadIssue() {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/issues/${issueId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const result = await res.json();
        if (result.status !== "success") throw new Error(result.message);

        const issue = result.data;
        titleEl.innerText = issue.title;
        descEl.innerText = issue.description;

        deptEl.value = issue.assigned_department || "";
        commentEl.value = issue.admin_comment || "";

        // Set select based on DB status
        approveEl.value = issue.status;

        // Disable fields if finalized
        if (issue.status === "Resolved" || issue.status === "Rejected") {
            approveEl.disabled = true;
            deptEl.disabled = true;
            commentEl.disabled = true;
            saveBtn.disabled = true;
        }

    } catch (err) {
        alert("Failed to load issue: " + err.message);
        window.location.href = "admin.html";
    }
}

// ----- Save / Update -----
saveBtn.onclick = async () => {
    const selectedStatus = approveEl.value;  // ENUM-safe
    const department = deptEl.value;
    const admin_comment = commentEl.value;

    let approved = false;
    if (selectedStatus === "In Progress") approved = true;
    if (selectedStatus === "Rejected") approved = false;

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/admin/issues/${issueId}/approve`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ approved, department, admin_comment })
        });
        const data = await res.json();

        if (res.status === 400 || res.status === 401) throw new Error(data.detail || "Update failed");

        alert(data.message || "Updated successfully!");
        window.location.href = "admin.html";
    } catch (err) {
        alert("Error updating issue: " + err.message);
    }
};

backBtn.onclick = () => window.location.href = "admin.html";

loadIssue();
