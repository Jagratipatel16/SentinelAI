
const API_URL = "http://127.0.0.1:8000";

// Check Login

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}

// Upload CSV

async function uploadCsv() {

    const fileInput = document.getElementById("csvFile");

    if (!fileInput.files.length) {

        alert("Please choose a CSV file first.");
        return;

    }

    const file = fileInput.files[0];

    if (!file.name.endsWith(".csv")) {

        alert("Only .csv files are allowed.");
        return;

    }

    // Show Loading

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

        if (!response.ok) {

            const errorData = await response.json();
            throw new Error(errorData.detail || "Upload failed.");

        }

        const result = await response.json();

        // Hide Loading

        document.getElementById("loading").style.display = "none";
        document.getElementById("resultCard").style.display = "block";

        // Fill Summary

        document.getElementById("totalRecords").innerHTML =
            result.total_records;

        document.getElementById("fraudCount").innerHTML =
            result.fraud_transactions;

        document.getElementById("safeCount").innerHTML =
            result.safe_transactions;

        // Download Link

        document.getElementById("downloadLink").href =
            API_URL + "/upload/download/" + result.download_file;

    }

    catch (error) {

        console.error(error);
        document.getElementById("loading").style.display = "none";
        alert(error.message || "Unable to upload CSV.");

    }

}

// Logout

function logout() {

    localStorage.removeItem("access_token");
    window.location.href = "login.html";

}
