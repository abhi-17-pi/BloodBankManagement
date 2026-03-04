try {
    const form = document.getElementById("loginForm");
    if (form) {
        form.addEventListener("submit", function (e) {
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            const error = document.getElementById("error");

            if (username === "" || password === "") {
                e.preventDefault();
                if (error) error.textContent = "Please fill in all fields";
            }
            // otherwise allow form to submit to server for authentication
        });
    }
} catch (err) {
    // silent fail if elements not present
}
