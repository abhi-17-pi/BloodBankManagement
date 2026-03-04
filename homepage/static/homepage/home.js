document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", () => {
        alert(card.innerText + " page coming soon!");
    });
});

document.getElementById("logout").onclick = () => {
    window.location.href = "../login/login.html";
};
