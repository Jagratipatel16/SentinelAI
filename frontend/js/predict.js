const API_URL = "http://127.0.0.1:8000";

// Check Login

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}


// Predict Transaction

async function predictTransaction() {

    // Show Loading

    document.getElementById("loading").style.display = "block";

    document.getElementById("resultCard").style.display = "none";

    // Collect Data

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

        //---------------- Prediction API ----------------//

        const response = await fetch(

            API_URL + "/predict/",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "Authorization": "Bearer " + token

                },

                body: JSON.stringify(data)

            }

        );

        const result = await response.json();

        //---------------- AI Explanation API ----------------//

        const explanationResponse = await fetch(

            API_URL + "/explanation/",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "Authorization": "Bearer " + token

                },

                body: JSON.stringify(data)

            }

        );

        const explanation = await explanationResponse.json();

        //---------------- Hide Loading ----------------//

        document.getElementById("loading").style.display = "none";

        document.getElementById("resultCard").style.display = "block";

        //---------------- Prediction ----------------//

        document.getElementById("prediction").innerHTML =
            result.prediction;

        document.getElementById("probability").innerHTML =
            result.probability;

        document.getElementById("risk").innerHTML =
            result.risk_score + " %";

        //---------------- Card Color ----------------//

        const card = document.getElementById("resultCard");

        card.classList.remove("safe");

        card.classList.remove("fraud");

        if (result.prediction === "Fraud") {

            card.classList.add("fraud");

            document.getElementById("prediction").style.color = "red";

        }

        else {

            card.classList.add("safe");

            document.getElementById("prediction").style.color = "green";

        }

        //---------------- AI Reasons ----------------//

        const list = document.getElementById("reasons");

        list.innerHTML = "";

        explanation.reasons.forEach(reason => {

            const li = document.createElement("li");

            li.textContent = reason;

            list.appendChild(li);

        });

        //---------------- Recommendation ----------------//

        document.getElementById("recommendation").innerHTML =
            explanation.recommendation;

    }

    catch (error) {

        console.error(error);

        document.getElementById("loading").style.display = "none";

        alert("Prediction Failed.");

    }

}


// Logout

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}