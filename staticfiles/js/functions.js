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
    const clientIdField = document.getElementById("client_id");

    // Met à jour la valeur du champ caché avec l'ID sélectionné
    clientIdField.value = dropdown.value;

    // Met à jour les détails affichés dynamiquement
    document.getElementById("detail_birth").innerText = dropdown.selectedOptions[0].getAttribute("data-birth");
    document.getElementById("detail_employed").innerText = dropdown.selectedOptions[0].getAttribute("data-employed");
    document.getElementById("detail_credit").innerText = dropdown.selectedOptions[0].getAttribute("data-credit");
    document.getElementById("detail_income").innerText = dropdown.selectedOptions[0].getAttribute("data-income");

    // Gestion du sexe (booléen vers texte lisible)
    const gender = dropdown.selectedOptions[0].getAttribute("data-gender");
    document.getElementById("detail_gender").innerText = (gender === "true" || gender === "True") ? "Homme" : "Femme";
}

// Initialiser les détails au chargement de la page si nécessaire
document.addEventListener("DOMContentLoaded", () => {
    showCustomerDetails();
});

// }function showCustomerDetails() {
//     const dropdown = document.getElementById("customer_dropdown");
//     const selectedOption = dropdown.options[dropdown.selectedIndex];

//     // Mettre à jour les champs avec les données correspondantes
//     document.getElementById("detail_birth").textContent = selectedOption.getAttribute("data-birth");
//     document.getElementById("detail_employed").textContent = selectedOption.getAttribute("data-employed");
//     document.getElementById("detail_credit").textContent = selectedOption.getAttribute("data-credit");
//     document.getElementById("detail_income").textContent = selectedOption.getAttribute("data-income");
// }
