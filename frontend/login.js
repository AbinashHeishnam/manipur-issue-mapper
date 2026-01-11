document.addEventListener("DOMContentLoaded", () => {
    const roleSelect = document.getElementById("roleSelect");
    const loginForm = document.getElementById("loginForm");
    const otpSection = document.getElementById("otpSection");
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");

    function renderForm(role) {
        otpSection.style.display = "none";

        if (role === "user") {
            loginForm.innerHTML = `
                <label>Mobile Number</label>
                <input type="text" id="mobile" placeholder="Enter mobile" required>
                <button type="submit">Send OTP</button>
            `;
        } else if (role === "admin") {
            loginForm.innerHTML = `
                <label>Username</label>
                <input type="text" id="adminUsername" required>
                <label>Password</label>
                <input type="password" id="adminPassword" required>
                <button type="submit">Login</button>
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

            fetch("http://127.0.0.1:8000/api/auth/send-otp", { // NO trailing slash
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mobile })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    alert("OTP sent (DEV): " + data.otp);
                    otpSection.style.display = "block";
                } else {
                    alert(data.message || "Failed to send OTP");
                }
            })
            .catch(err => {
                console.error("Send OTP error:", err);
                alert("Server error");
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
                    window.location.href = "admin/admin.html";
                } else {
                    alert("Invalid admin credentials");
                }
            })
            .catch(err => {
                console.error("Admin login error:", err);
                alert("Server error");
            });
        }
    });

    verifyOtpBtn.addEventListener("click", () => {
        const mobile = document.getElementById("mobile").value;
        const otp = parseInt(document.getElementById("otp").value);

        fetch("http://127.0.0.1:8000/api/auth/verify-otp", { // NO trailing slash
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mobile, otp })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                localStorage.setItem("user_id", data.user_id);
                window.location.href = "index.html";
            } else {
                alert(data.message || "OTP verification failed");
            }
        })
        .catch(err => {
            console.error("OTP verify error:", err);
            alert("Server error");
        });
    });
});
