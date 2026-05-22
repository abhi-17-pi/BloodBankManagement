function toggleMenu(event, id) {
    event.preventDefault();
    document.querySelectorAll(".dropdown-menu").forEach(m => m.style.display = "none");
    const menu = document.getElementById(id);
    if (menu) {
        menu.style.display = menu.style.display === "block" ? "none" : "block";
    }
}

function closeForm() {
    window.location.href = "/home/";
}

function sendCallAlert(donor) {
    // Socket removed — no-op
}

function initCallListeners() {
    document.addEventListener("click", (event) => {
        const el = event.target.closest("a[href^='tel:']");
        if (!el) return;

        const donorName = el.closest("tr")?.querySelector("td:first-child")?.textContent?.trim() || "donor";
        const donorMobile = el.getAttribute("href")?.replace("tel:", "") || "";
        sendCallAlert({ name: donorName, mobile: donorMobile });
    });
}

window.addEventListener("DOMContentLoaded", () => {
    initCallListeners();
});
