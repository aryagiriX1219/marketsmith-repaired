const loginForm = document.getElementById("loginForm");
const errorPrompt = document.getElementById("error-message");

loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const pass = document.getElementById("password").value;

    // // Simulate password check
    // if (pass !== "admin123") { 
    //     errorPrompt.style.display = "block";
    // } else {
        errorPrompt.style.display = "none";
        alert("Access Granted!");
    // }
});