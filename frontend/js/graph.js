
const API_URL = "http://127.0.0.1:8000";

// Check Login

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}

// Fetch helper with auth header

async function fetchJson(path) {

    const response = await fetch(

        API_URL + path,

        {
            headers: {
                "Authorization": "Bearer " + token
            }
        }

    );

    if (!response.ok) {

        throw new Error("Request failed: " + path);

    }

    return response.json();

}

// Load All Graph Data

async function loadGraphData() {

    document.getElementById("loading").style.display = "block";

    try {

        const [summary, highlyConnected, muleAccounts, fraudRings, circularTransfers] =
            await Promise.all([

                fetchJson("/graph/summary"),
                fetchJson("/graph/highly-connected"),
                fetchJson("/graph/mule-accounts"),
                fetchJson("/graph/fraud-rings"),
                fetchJson("/graph/circular-transfers")

            ]);

        // ---------------- Summary ----------------

        document.getElementById("totalAccounts").innerHTML =
            summary.total_accounts;

        document.getElementById("totalTransactions").innerHTML =
            summary.total_transactions;

        document.getElementById("totalConnections").innerHTML =
            summary.connections;

        // ---------------- Highly Connected Accounts ----------------

        const highlyConnectedTable = document.getElementById("highlyConnectedTable");
        highlyConnectedTable.innerHTML = "";

        if (highlyConnected.length === 0) {

            highlyConnectedTable.innerHTML =
                "<tr><td colspan='2'>No data available.</td></tr>";

        }

        highlyConnected.forEach(item => {

            const row = document.createElement("tr");

            row.innerHTML =
                "<td>" + item.account + "</td>" +
                "<td>" + item.connections + "</td>";

            highlyConnectedTable.appendChild(row);

        });

        // ---------------- Mule Accounts ----------------

        const muleTable = document.getElementById("muleAccountsTable");
        muleTable.innerHTML = "";

        if (muleAccounts.length === 0) {

            muleTable.innerHTML =
                "<tr><td colspan='2'>No suspected mule accounts found.</td></tr>";

        }

        muleAccounts.forEach(item => {

            const row = document.createElement("tr");

            row.innerHTML =
                "<td>" + item.account + "</td>" +
                "<td>" + item.received_from + "</td>";

            muleTable.appendChild(row);

        });

        // ---------------- Fraud Rings ----------------

        const ringsList = document.getElementById("fraudRingsList");
        ringsList.innerHTML = "";

        if (fraudRings.length === 0) {

            ringsList.innerHTML = "<li>No fraud rings detected.</li>";

        }

        fraudRings.forEach(ring => {

            const li = document.createElement("li");
            li.textContent = ring.join(" -> ") + " -> " + ring[0];
            ringsList.appendChild(li);

        });

        // ---------------- Circular Transfers ----------------

        const circularList = document.getElementById("circularTransfersList");
        circularList.innerHTML = "";

        if (circularTransfers.length === 0) {

            circularList.innerHTML = "<li>No circular transfers detected.</li>";

        }

        circularTransfers.forEach(cycle => {

            const li = document.createElement("li");
            li.textContent = cycle.join(" -> ") + " -> " + cycle[0];
            circularList.appendChild(li);

        });

    }

    catch (error) {

        console.error(error);
        alert("Unable to load graph data.");

    }

    finally {

        document.getElementById("loading").style.display = "none";

    }

}

// Logout

function logout() {

    localStorage.removeItem("access_token");
    window.location.href = "login.html";

}

// Load Automatically

loadGraphData();
