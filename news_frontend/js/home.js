const BASE_URL = "http://127.0.0.1:8000/api/user";
const TOKEN = localStorage.getItem("access_token");

// Fetch user profile data
fetch(`${BASE_URL}/getProfile/`, {
    method: "GET",
    headers: { "Authorization": `Bearer ${TOKEN}` }
})
.then(response => response.json())
.then(data => {
    document.getElementById("username").textContent = data.name || "User";
    document.getElementById("email").textContent = data.email || "N/A";
    document.getElementById("mobile").textContent = data.mobile || "N/A";
    document.getElementById("country").textContent = data.country || "N/A";
    document.getElementById("gender").textContent = data.gender || "N/A";
    document.getElementById("dob").textContent = data.dob || "N/A";
    document.getElementById("genres").textContent = data.genres_selected.join(", ") || "N/A";
    document.getElementById("status").textContent = data.status || "Unknown";
    document.getElementById("verification").textContent = data.is_verified ? "Verified" : "Not Verified";
})
.catch(error => {
    console.error("Error fetching profile:", error);
    document.getElementById("username").textContent = "Error loading profile!";
});

// Fetch latest news overview
function getNewsOverview() {
    fetch(`${BASE_URL}/get-news/`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${TOKEN}` }
    })
    .then(response => response.json())
    .then(data => {
        if (!data || data.length === 0) {
            alert("No news available.");
            return;
        }
        
        // Store full news data in localStorage
        localStorage.setItem("newsData", JSON.stringify(data));

        // Redirect to news page
        window.location.href = "news.html";
    })
    .catch(error => {
        console.error("Error fetching news:", error);
        alert("Failed to fetch news.");
    });
}

// Function to trigger scraper
function triggerScraper() {
    fetch(`${BASE_URL}/trigger-scraper/`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${TOKEN}` }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("news-container").innerHTML = 
            `<p style="color: green;">${data.message || "Scraper started successfully!"}</p>`;
    })
    .catch(error => {
        console.error("Error triggering scraper:", error);
        document.getElementById("news-container").innerHTML = 
            `<p style="color: red;">Failed to start scraper. Please try again.</p>`;
    });
}

function openNewsPage(type) {
    window.location.href = `news.html?type=${type}`;
}



function getSummary() {
    fetch(`${BASE_URL}/get-Summary/`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${TOKEN}` }
    })
    .then(response => response.json())
    .then(data => {
        if (!data || data.length === 0) {
            alert("No news available.");
            return;
        }
        
        // Store full news data in localStorage
        localStorage.setItem("newsSummaryData", JSON.stringify(data));

        // Redirect to news page
        window.location.href = "newsSummary.html";
    })
    .catch(error => {
        console.error("Error fetching news:", error);
        alert("Failed to fetch news.");
    });
}