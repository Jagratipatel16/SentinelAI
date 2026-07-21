const API_URL = "http://127.0.0.1:8000";

// ----------------------------
// Check Login
// ----------------------------

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}


// ----------------------------
// Explain Transaction
// ----------------------------

async function getExplanation() {

    const body = {

        step: Number(document.getElementById("step").value),

        type: Number(document.getElementById("type").value),

        amount: Number(document.getElementById("amount").value),

        oldbalanceOrg: Number(document.getElementById("oldbalanceOrg").value),

        newbalanceOrig: Number(document.getElementById("newbalanceOrig").value),

        oldbalanceDest: Number(document.getElementById("oldbalanceDest").value),

        newbalanceDest: Number(document.getElementById("newbalanceDest").value),

        isFlaggedFraud: Number(document.getElementById("isFlaggedFraud").value)

    };

    try {

        const response = await fetch(

            API_URL + "/explanation/",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "Authorization": "Bearer " + token

                },

                body: JSON.stringify(body)

            }

        );

        const data = await response.json();

        console.log(data);

        // Show Cards

        document.getElementById("resultCard").style.display = "block";

        document.getElementById("reasonCard").style.display = "block";

        document.getElementById("recommendationCard").style.display = "block";


        // ----------------------------
        // Prediction
        // ----------------------------

        const prediction = document.getElementById("prediction");

        prediction.innerHTML = data.prediction;

        prediction.classList.remove("safe", "fraud", "medium");

        if (data.prediction === "Fraud") {

            prediction.classList.add("fraud");

        }

        else {

            prediction.classList.add("safe");

        }


        // ----------------------------
        // Risk Score
        // ----------------------------

        document.getElementById("riskScore").innerHTML =
            data.risk_score + "%";

        const bar = document.getElementById("progressBar");

        bar.style.width = data.risk_score + "%";

        bar.innerHTML = data.risk_score + "%";

        if (data.risk_score >= 70) {

            bar.style.background = "red";

        }

        else if (data.risk_score >= 40) {

            bar.style.background = "orange";

        }

        else {

            bar.style.background = "green";

        }


        // ----------------------------
        // Reasons
        // ----------------------------

        const reasonList = document.getElementById("reasonList");

        reasonList.innerHTML = "";

        data.reasons.forEach(reason => {

            const li = document.createElement("li");

            li.innerHTML = "✔ " + reason;

            reasonList.appendChild(li);

        });


        // ----------------------------
        // Recommendation
        // ----------------------------

        document.getElementById("recommendation").innerHTML =
            data.recommendation;

    }

    catch (error) {

        console.log(error);

        alert("Unable to get explanation.");

    }

}


// ----------------------------
// Logout
// ----------------------------

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}