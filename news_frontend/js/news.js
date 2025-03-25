document.addEventListener("DOMContentLoaded", function () {
    const newsList = document.getElementById("news-list");
    const newsData = JSON.parse(localStorage.getItem("newsData"));

    if (!newsData || newsData.length === 0) {
        newsList.innerHTML = "<p>No news available.</p>";
        return;
    }

    let newsHTML = "<ul>";
    newsData.forEach(article => {
        newsHTML += `
            <li class="news-item">
                <strong>${article.title}</strong><br>
                <p><strong>Source:</strong> ${article.source}</p>
                <p><strong>Genre:</strong> ${article.genres}</p>
                <p><strong>Published On</strong> ${article.published_at}</p>
                <p><strong>Credibility Score:</strong> ${article.credibility_score || "N/A"}</p>
                <p><strong>Bias Score:</strong> ${article.bias_score || "N/A"}</p>
                <p><strong>Overview:</strong> ${article.overview || "Content not available."}</p>
                <a href="${article.url}" target="_blank">🔗 Read Full Article</a>
            </li><hr>
        `;
    });
    newsHTML += "</ul>";

    newsList.innerHTML = newsHTML;
});

// Go back to the home page
function goBack() {
    window.location.href = "home.html";
}
