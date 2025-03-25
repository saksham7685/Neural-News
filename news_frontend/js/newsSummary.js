document.addEventListener("DOMContentLoaded", async function () {
    const newsList = document.getElementById("news-list");
    const newsSummaryData = JSON.parse(localStorage.getItem("newsSummaryData"));

    if (!newsSummaryData || Object.keys(newsSummaryData).length === 0) {
        newsList.innerHTML = "<p>No news available.</p>";
        return;
    }

    // Construct the news summary display
    let newsHTML = `
        <p><strong>App ID:</strong> ${newsSummaryData.app_id}</p>
        <p><strong>Genres Selected:</strong> ${newsSummaryData.genres_selected.join(", ")}</p>
        <p><strong>Published On:</strong> ${newsSummaryData.published_at}</p>
        <hr>
        <div class="news-summary">${newsSummaryData.summary}</div>`;

        newsList.innerHTML = newsHTML;
    } 
);


// Go back to the home page
function goBack() {
    window.location.href = "home.html";
}








/*document.addEventListener("DOMContentLoaded", function () {
    const newsList = document.getElementById("news-list");
    const newsSummaryData = JSON.parse(localStorage.getItem("newsSummaryData"));

    if (!newsSummaryData || newsSummaryData.length === 0) {
        newsList.innerHTML = "<p>No news available.</p>";
        return;
    }

    let newsHTML = "<ul>";
    newsSummaryData.forEach(article => {
        newsHTML += `
            <li class="news-item">
                <strong>${article.title}</strong><br>
                <p><strong>Source:</strong> ${article.source}</p>
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
});*/