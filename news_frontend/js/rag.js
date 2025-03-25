async function sendQuery() {
    const query = document.getElementById("userQuery").value;
    const responseContainer = document.getElementById("responseContainer");
    const token = localStorage.getItem("access_token"); // Retrieve JWT token

    if (!query.trim()) {
        responseContainer.innerHTML = "<p style='color:red;'>Please enter a query.</p>";
        return;
    }

    responseContainer.innerHTML = "<p>Thinking ...</p>";

    try {
        const response = await fetch("http://127.0.0.1:8000/api/user/query/", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`, // Send JWT token
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        console.log("API Response:", data); // Log the response

        if (response.ok) {
            let answerHtml = "";

            if (typeof data.answer === "string") {
                answerHtml = `<p><strong></strong> ${data.answer}</p>`;
            } else if (typeof data.answer === "object" && data.answer.result) {
                answerHtml = `<p><strong>Answer:<br></strong> ${data.answer.result}</p>`;
            } else {
                responseContainer.innerHTML = `<p style='color:red;'>Unexpected response format. Check console.</p>`;
                console.error("Unexpected response:", data);
                return;
            }

            let sourcesHtml = "";
            if (data.retrieved_sources && Array.isArray(data.retrieved_sources)) {
                sourcesHtml = "<h3>Retrieved Sources:</h3><ul>";
                data.retrieved_sources.forEach(source => {
                    sourcesHtml += `<li><strong>Title:</strong> ${source.title}, <strong>Source:</strong> ${source.source}, <strong>Published At:</strong> ${source.published_at}</li>`;
                });
                sourcesHtml += "</ul>";
            }

            responseContainer.innerHTML = answerHtml + sourcesHtml; // Combine answer and sources
        } else {
            responseContainer.innerHTML = `<p style='color:red;'>Error: ${data.error || "Something went wrong"}</p>`;
        }
    } catch (error) {
        responseContainer.innerHTML = "<p style='color:red;'>Error fetching response.</p>";
        console.error("Error:", error);
    }
}