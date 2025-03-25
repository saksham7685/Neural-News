const BASE_URL = "http://127.0.0.1:8000/api/user";
function loginUser() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch(`${BASE_URL}/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (data.error.includes("Email is not registered")) {
                alert("This email is not registered. Please sign up first.");
                window.location.href = "signup.html"; // Redirect to signup page
            } else {
                alert("Invalid credentials. Please try again.");
            }
        } else {
            // Store tokens in local storage
            localStorage.setItem("access_token", data.access);
            localStorage.setItem("refresh_token", data.refresh);
            localStorage.setItem("user_id", data.user_id);

            alert("Login successful!");
            window.location.href = "home.html"; // Redirect to the main page after login
        }
    })
    .catch(error => console.error("Error:", error));
}
