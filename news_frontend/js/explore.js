document.addEventListener("DOMContentLoaded", () => {
    const features = [
        {
          "title": "Personalized News Feed",
          "description": "Stay updated with news tailored to your interests."
        },
        {
          "title": "AI-Powered Credibility Scoring",
          "description": "Get reliable news with AI-backed credibility assessments."
        },
        {
          "title": "Bias Detection",
          "description": "Identify news bias to make informed decisions."
        },
        {
          "title": "Efficient Web Scraping",
          "description": "Fresh news articles sourced using Scrapy and Selenium."
        },
        {
          "title": "Secure Authentication",
          "description": "Safe and easy login with OTP verification using Redis and JWT authentication."
        },
        {
          "title": "Customizable Experience",
          "description": "Choose and modify your preferred news categories anytime."
        },
        {
          "title": "User-Friendly Interface",
          "description": "Smooth and intuitive UI using vanilla JavaScript, HTML and CSS"
        },
        {
          "title": "Advanced RAG Inference",
          "description": "Utilizes Zephyr 7B Alpha for accurate and context-aware news retrieval and generation."
        },
        {
          "title": "Efficient Embeddings",
          "description": "Leverages sentence-transformers/all-MiniLM-L6-v2 for optimized news embedding storage in Pinecone."
        }
      ]

    const container = document.getElementById("features");

    features.forEach(feature => {
        const featureBox = document.createElement("div");
        featureBox.classList.add("feature-box");
        
        featureBox.innerHTML = `
            <h2>${feature.title}</h2>
            <p>${feature.description}</p>
        `;

        container.appendChild(featureBox);
    });
});
