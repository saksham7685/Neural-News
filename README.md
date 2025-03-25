# Neural News - AI-Powered Personalized News Platform

Neural News is a cutting-edge news platform that leverages advanced AI and NLP technologies to deliver personalized, reliable, and unbiased news to users. It integrates features like AI-driven credibility scoring, bias detection, and conversational news summaries using state-of-the-art LLMs.

## Features

-   **Personalized News Feed:** Tailored news based on user interests.
-   **AI-Powered Credibility Scoring:** Assesses news reliability using NLP. (`all-mpnet-base-v2`)
-   **Bias Detection:** Identifies potential biases in news reporting. (`all-mpnet-base-v2`)
-   **Real-Time News Scraping:** Fetches fresh news from trusted sources using Scrapy and Selenium.
-   **Conversational News Summaries:** Provides context-aware summaries and answers using `zephyr-7b-alpha.Q4_K_M.gguf`. (RAG functionality)
-   **Efficient Semantic Search:** Stores news embeddings in Pinecone for fast and accurate retrieval. (`all-MiniLM-L6-v2`)
-   **Secure Authentication:** Uses OTP (Redis) and JWT for secure user logins.
-   **Fully Customizable Genre Selection:** Allows users to select and update their preferred news genres.
-   **User-Friendly Interface:** Built with vanilla JavaScript, HTML, and CSS for a smooth experience.

## Technologies Used

-   **Backend:** Django (Python)
-   **Database:** MySQL
-   **Authentication:** JWT, Redis (OTP caching)
-   **Web Scraping:** Scrapy, Selenium
-   **NLP:**
    -   `all-MiniLM-L6-v2` (Embedding Storage)
    -   `all-mpnet-base-v2` (Bias Detection, Credibility Scoring)
    -   `zephyr-7b-alpha.Q4_K_M.gguf` (RAG, Summarization)
-   **Embedding Storage:** Pinecone
-   **Frontend:** HTML, CSS, JavaScript

## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone [repository_url]
    cd neural-news
    ```

2.  **Set up Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Database:**

    -   Set up your MySQL database and update the `settings.py` file in your Django project with your database credentials.

5.  **Set up Redis:**

    -   Install and run Redis.
    -   Configure the Redis connection settings in your Django project.

6.  **Set up Pinecone:**

    -   Create a Pinecone account and obtain your API key.
    -   Set up your Pinecone index and configure the connection in your Django project.

7.  **Run Migrations:**

    ```bash
    python manage.py migrate
    ```

8.  **Run Development Server:**

    ```bash
    python manage.py runserver
    ```

9.  **Frontend Setup:**
    * Open `index.html` in your browser.
    * Ensure that the frontend is configured to point to your Django backend's API endpoints.

10. **LLM Setup (Zephyr 7B Alpha):**
    * Download the `zephyr-7b-alpha.Q4_K_M.gguf` model and place it in the correct directory.
    * Configure the path to the model in your Django project.

## Usage

1.  **Register/Login:**
    -   Users can register and log in using OTP verification.
2.  **Personalize Feed:**
    -   Users can select their preferred news genres.
3.  **Search News:**
    -   Users can search for news articles using keywords or natural language queries.
4.  **View Summaries:**
    -   The application provides AI-generated summaries of news articles.
5.  **View Credibility and Bias Scores:**
    -   The application displays credibility and bias scores for news articles.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

[Your License]
