document.addEventListener("DOMContentLoaded", () => {
    const roleSelect = document.getElementById("roleSelect");
    const loginForm = document.getElementById("loginForm");
    const otpSection = document.getElementById("otpSection");
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");

    function renderForm(role) {
        otpSection.style.display = "none";

        if (role === "user") {
            loginForm.innerHTML = `
                <div class="form-group">
                    <label>Mobile Number</label>
                    <input type="text" id="mobile" placeholder="Enter mobile" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Send OTP</button>
            `;
        } else if (role === "admin") {
            loginForm.innerHTML = `
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="adminUsername" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="adminPassword" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Login</button>
            `;
        } else if (role === "department") {
            loginForm.innerHTML = `
                <div class="alert" style="background: rgba(59, 130, 246, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 16px; font-size: 0.9rem; color: var(--primary);">
                    Login using your Department ID and password.
                </div>
                <div class="form-group">
                    <label>Department ID</label>
                    <input type="text" id="deptUsername" placeholder="e.g. water" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="deptPassword" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Login</button>
            `;
        }
    }

    renderForm(roleSelect.value);

    roleSelect.addEventListener("change", () => renderForm(roleSelect.value));

    loginForm.addEventListener("submit", e => {
        e.preventDefault();
        const role = roleSelect.value;

        if (role === "user") {
            const mobile = document.getElementById("mobile").value;

            fetch("http://127.0.0.1:8000/api/auth/send-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mobile })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        // Use toast if available, else alert
                        if (window.showToast) window.showToast("OTP sent: " + data.otp, "info");
                        else alert("OTP sent: " + data.otp);

                        otpSection.style.display = "block";
                    } else {
                        if (window.showToast) window.showToast(data.message || "Failed to send OTP", "error");
                        else alert(data.message || "Failed to send OTP");
                    }
                })
                .catch(err => {
                    console.error("Send OTP error:", err);
                    if (window.showToast) window.showToast("Server error", "error");
                    else alert("Server error");
                });
        }

        if (role === "admin") {
            const username = document.getElementById("adminUsername").value;
            const password = document.getElementById("adminPassword").value;

            fetch("http://127.0.0.1:8000/api/admin/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        localStorage.setItem("admin_token", data.token);
                        if (window.showToast) window.showToast("Admin login successful", "success");
                        // Delay redirect slightly to see toast
                        setTimeout(() => window.location.href = "admin/admin.html", 800);
                    } else {
                        if (window.showToast) window.showToast("Invalid admin credentials", "error");
                        else alert("Invalid credentials");
                    }
                })
                .catch(err => {
                    console.error("Admin login error:", err);
                    alert("Server error");
                });
        }

        if (role === "department") {
            const username = document.getElementById("deptUsername").value;
            const password = document.getElementById("deptPassword").value;

            fetch("http://127.0.0.1:8000/api/department/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        localStorage.setItem("dept_token", data.token);
                        localStorage.setItem("dept_name", data.department_name);

                        if (window.showToast) window.showToast("Department login successful", "success");
                        setTimeout(() => window.location.href = "department/department.html", 800);
                    } else {
                        if (window.showToast) window.showToast(data.detail || "Invalid credentials", "error");
                        else alert(data.detail || "Invalid credentials");
                    }
                })
                .catch(err => {
                    console.error("Department login error:", err);
                    alert("Login failed");
                });
        }
    });

    verifyOtpBtn.addEventListener("click", () => {
        const mobile = document.getElementById("mobile").value;
        const otp = parseInt(document.getElementById("otp").value);

        fetch("http://127.0.0.1:8000/api/auth/verify-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mobile, otp })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    localStorage.setItem("user_id", data.user_id);
                    if (window.showToast) window.showToast("Verified! Redirecting...", "success");
                    setTimeout(() => window.location.href = "index.html", 800);
                } else {
                    if (window.showToast) window.showToast(data.message || "OTP verification failed", "error");
                    else alert(data.message || "OTP verification failed");
                }
            })
            .catch(err => {
                console.error("OTP verify error:", err);
                if (window.showToast) window.showToast("Server error", "error");
                else alert("Server error");
            });
    });
});
