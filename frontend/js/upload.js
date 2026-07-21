const API_URL = "http://127.0.0.1:8000";

// -------------------------------
// Check Login
// -------------------------------

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}


// -------------------------------
// Upload CSV
// -------------------------------

async function uploadCSV() {

    const file = document.getElementById("csvFile").files[0];

    if (!file) {

        alert("Please select a CSV file.");

        return;

    }

    document.getElementById("loading").style.display = "block";

    document.getElementById("resultCard").style.display = "none";

    const formData = new FormData();

    formData.append("file", file);

    try {

    const response = await fetch(
        API_URL + "/upload/",
        {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            },
            body: formData
        }
    );

    console.log("Status:", response.status);

    const data = await response.json();

    console.log("Response:", data);

    if (!response.ok) {
        alert(data.detail || "Upload Failed");
        return;
    }

    document.getElementById("loading").style.display = "none";
    document.getElementById("resultCard").style.display = "block";

    document.getElementById("totalRecords").innerHTML =
        data.total_records;

    document.getElementById("fraudRecords").innerHTML =
        data.fraud_transactions;

    document.getElementById("safeRecords").innerHTML =
        data.safe_transactions;

}
catch(error){

    console.log(error);

    alert(error);

}

}


// -------------------------------
// Logout
// -------------------------------

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}