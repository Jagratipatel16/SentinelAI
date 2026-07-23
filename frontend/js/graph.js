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

        const [summary, highlyConnected, muleAccounts, fraudRings, circularTransfers, network] =
            await Promise.all([

                fetchJson("/graph/summary"),
                fetchJson("/graph/highly-connected"),
                fetchJson("/graph/mule-accounts"),
                fetchJson("/graph/fraud-rings"),
                fetchJson("/graph/circular-transfers"),
                fetchJson("/graph/network")

            ]);

        // ---------------- Summary ----------------

        document.getElementById("totalAccounts").innerHTML =
            summary.total_accounts;

        document.getElementById("totalTransactions").innerHTML =
            summary.total_transactions;

        document.getElementById("totalConnections").innerHTML =
            summary.connections;

        // ---------------- Network Diagram ----------------

        renderNetworkDiagram(network);

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

// ----------------------------------------
// Render Network Diagram (simple static SVG, circular layout)
// ----------------------------------------

function renderNetworkDiagram(data) {

    const svg = document.getElementById("networkSvg");

    const SVG_NS = "http://www.w3.org/2000/svg";

    // Clear any previous diagram (in case of refresh)

    svg.innerHTML = "";

    const nodes = data.nodes || [];
    const edges = data.edges || [];

    if (nodes.length === 0) {

        const text = document.createElementNS(SVG_NS, "text");
        text.setAttribute("x", 20);
        text.setAttribute("y", 30);
        text.textContent = "No transaction data to display.";
        svg.appendChild(text);
        return;

    }

    const width = 800;
    const height = Math.max(500, nodes.length * 18);

    svg.setAttribute("viewBox", "0 0 " + width + " " + height);
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", height);

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 70;

    // ---------------- Position each node evenly around a circle ----------------

    const positions = {};

    nodes.forEach((node, i) => {

        const angle = (2 * Math.PI * i) / nodes.length;

        positions[node.id] = {

            x: centerX + radius * Math.cos(angle),

            y: centerY + radius * Math.sin(angle)

        };

    });

    // ---------------- Arrowhead marker (defined once, reused by all edges) ----------------

    const defs = document.createElementNS(SVG_NS, "defs");

    defs.innerHTML =
        '<marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">' +
        '<polygon points="0 0, 7 3, 0 6" fill="#888"></polygon>' +
        '</marker>';

    svg.appendChild(defs);

    // ---------------- Draw Edges ----------------

    edges.forEach(edge => {

        const from = positions[edge.from];
        const to = positions[edge.to];

        if (!from || !to || edge.from === edge.to) {

            return;

        }

        const line = document.createElementNS(SVG_NS, "line");

        line.setAttribute("x1", from.x);
        line.setAttribute("y1", from.y);
        line.setAttribute("x2", to.x);
        line.setAttribute("y2", to.y);
        line.setAttribute("stroke", "#aaa");
        line.setAttribute("stroke-width", "1.5");
        line.setAttribute("marker-end", "url(#arrowhead)");

        const title = document.createElementNS(SVG_NS, "title");
        title.textContent = edge.from + " -> " + edge.to + " (Rs " + edge.label + ")";
        line.appendChild(title);

        svg.appendChild(line);

    });

    // ---------------- Draw Nodes ----------------

    nodes.forEach(node => {

        const pos = positions[node.id];

        const circle = document.createElementNS(SVG_NS, "circle");

        circle.setAttribute("cx", pos.x);
        circle.setAttribute("cy", pos.y);
        circle.setAttribute("r", (node.size || 20) / 2.5);
        circle.setAttribute("fill", node.color || "#2196F3");
        circle.setAttribute("stroke", "#fff");
        circle.setAttribute("stroke-width", "1");

        const title = document.createElementNS(SVG_NS, "title");
        title.textContent = node.label;
        circle.appendChild(title);

        svg.appendChild(circle);

        const label = document.createElementNS(SVG_NS, "text");

        label.setAttribute("x", pos.x);
        label.setAttribute("y", pos.y - ((node.size || 20) / 2.5) - 4);
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("font-size", "9");
        label.setAttribute("fill", "#333");
        label.textContent = node.label;

        svg.appendChild(label);

    });

}


// ----------------------------------------
// AI Network Explanation
// ----------------------------------------

async function explainGraph() {

    document.getElementById("explainLoading").style.display = "block";
    document.getElementById("graphExplanationCard").style.display = "none";

    try {

        const data = await fetchJson("/graph/explain");

        document.getElementById("graphExplanationText").innerHTML =
            data.explanation;

        document.getElementById("graphExplanationCard").style.display = "block";

    }

    catch (error) {

        console.error(error);
        alert(error.message || "Unable to generate graph explanation.");

    }

    finally {

        document.getElementById("explainLoading").style.display = "none";

    }

}


// Logout

function logout() {

    localStorage.removeItem("access_token");
    window.location.href = "login.html";

}

// Load Automatically

loadGraphData();