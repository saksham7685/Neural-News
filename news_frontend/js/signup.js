const BASE_URL = "http://127.0.0.1:8000/api/user"; // Replace with actual backend URL

const AVAILABLE_GENRES = [
    "Technology", "Science", "Politics", "Sports", "Entertainment",
    "Business", "Health", "Education", "Travel", "Lifestyle",
    "Gaming", "Finance", "Music", "Movies", "Food",
    "Artificial Intelligence", "Climate & Environment", "History & Culture",
    "Social Issues", "Crime & Law", "Automobiles", "Space",
    "Startups & Entrepreneurship", "Economy", "Psychology & Mental Health",
    "Real Estate", "Defense & Military", "Cryptocurrency & Blockchain",
    "Science Fiction & Futurism", "Philosophy & Ethics","Astrology",
];

const STATIC_COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia & Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
    "Cambodia", "Cameroon", "Canada", "Cape Verde", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
    "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guyana",
    "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan",
    "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
    "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
    "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
    "Oman",
    "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
    "Qatar",
    "Romania", "Russia", "Rwanda",
    "Saint Kitts & Nevis", "Saint Lucia", "Saint Vincent & the Grenadines", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
    "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
    "Yemen",
    "Zambia", "Zimbabwe"
]

// Populate genres dynamically with checkboxes
document.addEventListener("DOMContentLoaded", function() {
    const genresContainer = document.getElementById("genres-container");
    const countrySelect = document.getElementById("country");
    AVAILABLE_GENRES.forEach(genre => {
        const label = document.createElement("label");
        label.classList.add("genre-checkbox");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = genre;
        checkbox.name = "genres";

        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(genre));
        genresContainer.appendChild(label);
    });
    
    STATIC_COUNTRIES.forEach(country => {
        const option = document.createElement("option");
        option.value = country;
        option.textContent = country;
        countrySelect.appendChild(option);
    });
});

function registerUser() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const mobile = document.getElementById("phone").value;
    const dob = document.getElementById("dob").value;
    const gender = document.getElementById("gender").value;
    const country = document.getElementById("country").value;
    const password = document.getElementById("password").value;

    // Get selected genres
    const selectedGenres = [];
    document.querySelectorAll("#genres-container input:checked").forEach(input => {
        selectedGenres.push(input.value);
    });

    if (selectedGenres.length === 0 || selectedGenres.length > 10) {
        alert("Please select between 1 and 10 genres.");
        return;
    }

    fetch(`${BASE_URL}/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name, email, mobile, dob, gender, country,
            genres_selected: selectedGenres, password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message && data.message.includes("OTP sent")) {
            document.getElementById("otp-section").style.display = "block";
            alert("OTP has been sent to your mobile number.");
        } else {
            alert("Registration failed: " + (data.error || "Unknown error"));
        }
    })
    .catch(error => console.error("Error:", error));
}

function verifyOTP() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const mobile = document.getElementById("phone").value;
    const dob = document.getElementById("dob").value;
    const gender = document.getElementById("gender").value;
    const country = document.getElementById("country").value;
    const password = document.getElementById("password").value;
    const otp = document.getElementById("otp").value;

    const genres = Array.from(document.querySelectorAll('input[name="genres"]:checked'))
                        .map(checkbox => checkbox.value);

    if (genres.length === 0 || genres.length > 10) {
        alert("Please select between 1 and 10 genres.");
        return;
    }
    fetch(`${BASE_URL}/register/`, {  // Using the same API
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name, email, mobile, dob, gender, country, 
            genres_selected: genres, password, otp
        })  // Send OTP for verification
    })
    .then(response => response.json())
    .then(data => {
        if (data.jwt) {
            alert("Account created successfully!");
            window.location.href = "login.html";
        } else {
            alert("Invalid OTP. Please try again.");
        }
    })
    .catch(error => console.error("Error:", error));
}
