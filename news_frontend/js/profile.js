document.addEventListener("DOMContentLoaded", function () {
    const BASE_URL = "http://127.0.0.1:8000/api/user/";
    const TOKEN = localStorage.getItem("access_token");
    
    let user = null;
    let formData = {};
    let editing = false;
    
    const AVAILABLE_GENRES = [
        "Technology", "Science", "Politics", "Sports", "Entertainment",
        "Business", "Health", "Education", "Travel", "Lifestyle",
        "Gaming", "Finance", "Music", "Movies", "Food",
        "Artificial Intelligence", "Climate & Environment", "History & Culture",
        "Social Issues", "Crime & Law", "Automobiles", "Space",
        "Startups & Entrepreneurship", "Economy", "Psychology & Mental Health",
        "Real Estate", "Defense & Military", "Cryptocurrency & Blockchain",
        "Science Fiction & Futurism", "Philosophy & Ethics","Astrology"
    ];
    
    async function fetchProfile() {
        try {
            const response = await fetch(`${BASE_URL}getProfile/`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${TOKEN}` }
            });

            if (!response.ok) throw new Error("Failed to fetch profile");

            user = await response.json();
            formData = { ...user };
            updateProfileUI();
        } catch (error) {
            console.error(error);
        }
    }
    
    function updateProfileUI() {
        document.getElementById("name").value = formData.name || "";
        document.getElementById("email").value = formData.email;
        document.getElementById("mobile").value = formData.mobile || "";
        document.getElementById("country").value = formData.country || "";
        document.getElementById("gender").value = formData.gender || "";
        document.getElementById("dob").value = formData.dob || "";
        document.getElementById("genres-container1").innerHTML = generateGenresCheckboxes();
        document.getElementById("status").textContent = user.status;
        document.getElementById("verification").textContent = user.is_verified;
    }
    
    function generateGenresCheckboxes() {
        return AVAILABLE_GENRES.map(genre => {
            const checked = user.genres_selected?.includes(genre) ? "checked" : "";
            return `<label class="genre-checkbox">
                        <input type="checkbox" class="genre-checkbox" name="genres_selected" value="${genre}" ${checked}> 
                        ${genre}
                    </label>`;
        }).join("<br>");
    }

    function handleChange(e) {
        if (e.target.name === "genres_selected") {
            if (e.target.checked) {
                formData.genres_selected = [...(formData.genres_selected || []), e.target.value];
            } else {
                formData.genres_selected = formData.genres_selected.filter(g => g !== e.target.value);
            }
        } else {
            formData[e.target.name] = e.target.value;
        }
    }
    
    async function handleUpdate() {
        try {
            const response = await fetch(`${BASE_URL}updateProfile/`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${TOKEN}`
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error("Update failed");

            alert("Profile updated successfully!");
            fetchProfile();
            toggleEdit();
        } catch (error) {
            console.error(error);
            alert("Failed to update profile.");
        }
    }
    
    function toggleEdit() {
        editing = !editing;
        document.querySelectorAll("input, select").forEach(el => el.disabled = !editing);
        document.getElementById("edit-btn").textContent = editing ? "Cancel" : "Edit Profile";
        document.getElementById("save-btn").style.display = editing ? "inline-block" : "none";
    }
    
    document.getElementById("edit-btn").addEventListener("click", toggleEdit);
    document.getElementById("save-btn").addEventListener("click", handleUpdate);
    document.querySelectorAll("input, select").forEach(el => el.addEventListener("input", handleChange));
    document.addEventListener("change", handleChange);
    
    fetchProfile();
});
