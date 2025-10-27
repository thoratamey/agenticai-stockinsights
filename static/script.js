// Simple JS to show loader during form submission
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const loader = document.getElementById("loader");

    if (form && loader) {
        form.addEventListener("submit", function() {
            loader.style.display = "block";
        });
    }
});
