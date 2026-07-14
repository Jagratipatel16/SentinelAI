const API_URL = "http://127.0.0.1:8000";

// Check Login

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}

// Load Dashboard

async function loadDashboard() {

    try {

        const response = await fetch(

            API_URL + "/dashboard"

        );

        const data = await response.json();

        console.log(data);

        document.getElementById("total").innerHTML =
            data.total_transactions;

        document.getElementById("fraud").innerHTML =
            data.fraud_transactions;

        document.getElementById("safe").innerHTML =
            data.safe_transactions;

        document.getElementById("high").innerHTML =
            data.suspicious_transactions;

        document.getElementById("medium").innerHTML =
            data.pending_transactions;

        document.getElementById("low").innerHTML =
            Number(data.fraud_amount).toLocaleString();

        document.getElementById("amount").innerHTML =
            Number(data.total_amount).toLocaleString();

    }

    catch (error) {

        console.error(error);

        alert("Unable to load dashboard.");

    }

}

// Logout

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}

// Load Dashboard Automatically

loadDashboard();