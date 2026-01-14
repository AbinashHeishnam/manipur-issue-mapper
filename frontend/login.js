document.addEventListener("DOMContentLoaded", () => {
    const roleSelect = document.getElementById("roleSelect");
    const loginForm = document.getElementById("loginForm");
    const otpSection = document.getElementById("otpSection");
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");
    const setPasswordSection = document.getElementById("setPasswordSection");
    const setPasswordBtn = document.getElementById("setPasswordBtn");
    const userActionButtons = document.getElementById("userActionButtons");
    const userSignupBtn = document.getElementById("userSignupBtn");
    const userLoginBtn = document.getElementById("userLoginBtn");

    let currentUserMobile = null;
    let currentUserId = null;

    function toast(msg) { alert(msg); }

    function renderUserForm(action) {
        otpSection.style.display = "none";
        setPasswordSection.style.display = "none";
        loginForm.innerHTML = "";

        if (action === "signup") {
            loginForm.innerHTML = `
                <div class="form-group"><label>Name</label><input type="text" id="name"></div>
                <div class="form-group"><label>Email</label><input type="email" id="email"></div>
                <div class="form-group"><label>Mobile</label><input type="text" id="mobile" required></div>
                <button type="submit" class="btn" style="width:100%">Send OTP</button>
            `;
        } else if (action === "login") {
            loginForm.innerHTML = `
                <div class="form-group"><label>Email or Mobile</label><input type="text" id="loginUser" required></div>
                <div class="form-group"><label>Password</label><input type="password" id="loginPassword" required></div>
                <button type="submit" class="btn" style="width:100%">Login</button>
            `;
        }
    }

    function renderForm(role) {
        otpSection.style.display = "none";
        setPasswordSection.style.display = "none";
        loginForm.innerHTML = "";

        if (role === "user") {
            userActionButtons.style.display = "flex";
        } else {
            userActionButtons.style.display = "none";
            if (role === "admin") {
                loginForm.innerHTML = `
                    <div class="form-group"><label>Username</label><input type="text" id="adminUsername" required></div>
                    <div class="form-group"><label>Password</label><input type="password" id="adminPassword" required></div>
                    <button type="submit" class="btn" style="width:100%">Login</button>
                `;
            } else if (role === "department") {
                loginForm.innerHTML = `
                    <div class="form-group"><label>Department ID</label><input type="text" id="deptUsername" required></div>
                    <div class="form-group"><label>Password</label><input type="password" id="deptPassword" required></div>
                    <button type="submit" class="btn" style="width:100%">Login</button>
                `;
            }
        }
    }

    renderForm(roleSelect.value);
    roleSelect.addEventListener("change", () => renderForm(roleSelect.value));

    userSignupBtn.addEventListener("click", () => renderUserForm("signup"));
    userLoginBtn.addEventListener("click", () => renderUserForm("login"));

    loginForm.addEventListener("submit", e => {
        e.preventDefault();
        const role = roleSelect.value;
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true; submitBtn.innerText = "Processing...";

        // ----- USER SIGNUP OTP -----
        if (role === "user" && loginForm.querySelector("#mobile")) {
            const name = document.getElementById("name").value || null;
            const email = document.getElementById("email").value || null;
            const mobile = document.getElementById("mobile").value;

            fetch("http://127.0.0.1:8000/api/auth/send-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mobile, name, email })
            }).then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        currentUserMobile = mobile;
                        currentUserId = data.user_id;
                        toast("OTP sent: " + data.otp);
                        otpSection.style.display = "block";
                    } else { toast(data.detail || "Failed"); }
                })
                .catch(err => { console.error(err); toast("Server error"); })
                .finally(() => { submitBtn.disabled = false; submitBtn.innerText = "Send OTP"; });
            return;
        }

        // ----- USER LOGIN -----
        if (role === "user" && loginForm.querySelector("#loginUser")) {
            const loginUser = document.getElementById("loginUser").value;
            const loginPassword = document.getElementById("loginPassword").value;

            fetch("http://127.0.0.1:8000/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mobile_or_email: loginUser, password: loginPassword })
            }).then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        localStorage.setItem("user_id", data.user_id);
                        localStorage.setItem("user_token", "user-" + data.user_id);
                        toast("Login successful!");
                        setTimeout(() => window.location.href = "index.html", 500);
                    } else { toast(data.detail || "Invalid credentials"); submitBtn.disabled = false; submitBtn.innerText = "Login"; }
                }).catch(err => { console.error(err); toast("Server error"); submitBtn.disabled = false; submitBtn.innerText = "Login"; });
            return;
        }

        // ----- ADMIN LOGIN -----
        if (role === "admin") {
            const username = document.getElementById("adminUsername").value;
            const password = document.getElementById("adminPassword").value;
            fetch("http://127.0.0.1:8000/api/admin/login", {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            }).then(res => res.json())
                .then(data => {
                    if (data.status === "success") { localStorage.setItem("admin_token", data.token); toast("Welcome Admin"); setTimeout(() => window.location.href = "admin/admin.html", 500); }
                    else { toast("Invalid credentials"); submitBtn.disabled = false; submitBtn.innerText = "Login"; }
                }).catch(err => { console.error(err); toast("Server error"); submitBtn.disabled = false; submitBtn.innerText = "Login"; });
        }

        // ----- DEPARTMENT LOGIN -----
        if (role === "department") {
            const username = document.getElementById("deptUsername").value;
            const password = document.getElementById("deptPassword").value;
            fetch("http://127.0.0.1:8000/api/department/login", {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            }).then(res => res.json())
                .then(data => {
                    if (data.status === "success") { localStorage.setItem("dept_token", data.token); toast(`Login: ${data.department_name}`); setTimeout(() => window.location.href = "department/department.html", 500); }
                    else { toast(data.detail || "Invalid credentials"); submitBtn.disabled = false; submitBtn.innerText = "Login"; }
                }).catch(err => { console.error(err); toast("Server error"); submitBtn.disabled = false; submitBtn.innerText = "Login"; });
        }
    });

    // ----- VERIFY OTP -----
    verifyOtpBtn.addEventListener("click", () => {
        const otp = parseInt(document.getElementById("otp").value);
        if (!otp) { toast("Enter OTP"); return; }
        verifyOtpBtn.disabled = true; verifyOtpBtn.innerText = "Verifying...";
        fetch("http://127.0.0.1:8000/api/auth/verify-otp", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mobile: currentUserMobile, otp })
        }).then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    toast("OTP verified! Set your password now");
                    setPasswordSection.style.display = "block";
                } else { toast(data.detail || "OTP failed"); }
            }).catch(err => { console.error(err); toast("Server error"); })
            .finally(() => { verifyOtpBtn.disabled = false; verifyOtpBtn.innerText = "Verify OTP"; });
    });

    // ----- SET PASSWORD -----
    setPasswordBtn.addEventListener("click", () => {
        const password = document.getElementById("password").value;
        if (!password) { toast("Enter password"); return; }
        setPasswordBtn.disabled = true; setPasswordBtn.innerText = "Setting...";
        fetch("http://127.0.0.1:8000/api/auth/set-password", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: currentUserId, password })
        }).then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    localStorage.setItem("user_id", currentUserId);
                    localStorage.setItem("user_token", "user-" + currentUserId);
                    toast("Password set! Redirecting...");
                    setTimeout(() => window.location.href = "index.html", 500);
                } else { toast(data.detail || "Failed"); setPasswordBtn.disabled = false; setPasswordBtn.innerText = "Set Password"; }
            }).catch(err => { console.error(err); toast("Server error"); setPasswordBtn.disabled = false; setPasswordBtn.innerText = "Set Password"; });
    });

});
