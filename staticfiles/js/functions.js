function openFullscreen(iframeId) {
    var elem = document.getElementById(iframeId);
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
        elem.msRequestFullscreen();
    }
}

function showCustomerDetails() {
    const dropdown = document.getElementById("customer_dropdown");
    const selectedOption = dropdown.options[dropdown.selectedIndex];

    const birthDays = parseInt(selectedOption.getAttribute("data-birth"), 10); // Convertir en nombre
    const birthYears = birthDays / 365; // Convertir en années

    
    document.getElementById("detail_birth").textContent = `${birthYears} ans`
    document.getElementById("detail_employed").textContent = selectedOption.getAttribute("data-employed");
    document.getElementById("detail_credit").textContent = selectedOption.getAttribute("data-credit");
    document.getElementById("detail_income").textContent = selectedOption.getAttribute("data-income");
}


