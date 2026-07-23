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

        if (!response.ok) {

            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || "Explanation request failed.");

        }

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

        alert(error.message || "Unable to get explanation.");

    }

}


// ----------------------------
// Tabs
// ----------------------------

function showTab(tab) {

    const singleTab = document.getElementById("singleTab");
    const csvTab = document.getElementById("csvTab");

    const tabBtnSingle = document.getElementById("tabBtnSingle");
    const tabBtnCsv = document.getElementById("tabBtnCsv");

    if (tab === "csv") {

        singleTab.style.display = "none";
        csvTab.style.display = "block";

        tabBtnCsv.classList.add("active");
        tabBtnSingle.classList.remove("active");

    }

    else {

        singleTab.style.display = "block";
        csvTab.style.display = "none";

        tabBtnSingle.classList.add("active");
        tabBtnCsv.classList.remove("active");

    }

}


// ----------------------------
// Explain CSV (Batch)
// ----------------------------

async function explainCsv() {

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

    document.getElementById("csvLoading").style.display = "block";
    document.getElementById("csvSummaryCard").style.display = "none";
    document.getElementById("csvResultsCard").style.display = "none";

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch(

            API_URL + "/explanation/batch-csv",

            {
                method: "POST",
                headers: {
                    "Authorization": "Bearer " + token
                },
                body: formData
            }

        );

        if (!response.ok) {

            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || "CSV explanation failed.");

        }

        const result = await response.json();

        document.getElementById("csvLoading").style.display = "none";

        // ---------------- Summary ----------------

        document.getElementById("csvSummaryCard").style.display = "block";

        document.getElementById("csvTotalRecords").innerHTML =
            result.total_records;

        document.getElementById("csvFraudCount").innerHTML =
            result.fraud_count;

        // ---------------- Results Table ----------------

        const body = document.getElementById("csvResultsBody");

        body.innerHTML = "";

        if (result.explanations.length === 0) {

            body.innerHTML =
                "<tr><td colspan='8'>No fraud transactions were found in this file.</td></tr>";

        }

        result.explanations.forEach(item => {

            const row = document.createElement("tr");

            const reasonsHtml = item.reasons
                .map(r => "&#10003; " + r)
                .join("<br>");

            row.innerHTML =
                "<td>" + item.row + "</td>" +
                "<td>" + item.sender + "</td>" +
                "<td>" + item.receiver + "</td>" +
                "<td>" + item.type + "</td>" +
                "<td>" + item.amount + "</td>" +
                "<td>" + item.risk_score + "%</td>" +
                "<td>" + reasonsHtml + "</td>" +
                "<td>" + item.recommendation + "</td>";

            body.appendChild(row);

        });

        document.getElementById("csvResultsCard").style.display = "block";

    }

    catch (error) {

        console.error(error);
        document.getElementById("csvLoading").style.display = "none";
        alert(error.message || "Unable to explain CSV.");

    }

}


// ----------------------------
// Logout
// ----------------------------

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}