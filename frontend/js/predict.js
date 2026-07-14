const API_URL = "http://127.0.0.1:8000";

// Check Login

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}


// Predict Transaction

async function predictTransaction() {

    const data = {

        step: parseInt(document.getElementById("step").value),

        type: parseInt(document.getElementById("type").value),

        amount: parseFloat(document.getElementById("amount").value),

        oldbalanceOrg: parseFloat(document.getElementById("oldbalanceOrg").value),

        newbalanceOrig: parseFloat(document.getElementById("newbalanceOrig").value),

        oldbalanceDest: parseFloat(document.getElementById("oldbalanceDest").value),

        newbalanceDest: parseFloat(document.getElementById("newbalanceDest").value),

        isFlaggedFraud: parseInt(document.getElementById("isFlaggedFraud").value)

    };

    try {

        const response = await fetch(

            API_URL + "/predict/",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(data)

            }

        );

        const result = await response.json();

        console.log(result);

        document.getElementById("prediction").innerHTML =
            result.prediction;

        document.getElementById("probability").innerHTML =
            result.probability;

        document.getElementById("risk").innerHTML =
            result.risk_score + "%";


        if (result.prediction === "Fraud") {

            document.getElementById("prediction").style.color = "red";

        }

        else {

            document.getElementById("prediction").style.color = "green";

        }

    }

    catch (error) {

        console.log(error);

        alert("Prediction Failed.");

    }

}


// Logout

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}