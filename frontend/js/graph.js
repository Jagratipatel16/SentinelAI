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

        const ringsContainer = document.getElementById("fraudRingsContainer");
        ringsContainer.innerHTML = "";

        if (fraudRings.length === 0) {

            ringsContainer.innerHTML = "<p>No fraud rings detected.</p>";

        }

        fraudRings.forEach((ring, i) => {

            renderRingDiagram(ringsContainer, ring, "Fraud Ring " + (i + 1), true);

        });

        // ---------------- Circular Transfers ----------------

        const circularContainer = document.getElementById("circularTransfersContainer");
        circularContainer.innerHTML = "";

        if (circularTransfers.length === 0) {

            circularContainer.innerHTML = "<p>No circular transfers detected.</p>";

        }

        circularTransfers.forEach((cycle, i) => {

            renderRingDiagram(circularContainer, cycle, "Cycle " + (i + 1), false);

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
// Render Full Network Diagram (simple static SVG, circular layout)
// ----------------------------------------

function renderNetworkDiagram(data) {

    const svg = document.getElementById("networkSvg");

    const SVG_NS = "http://www.w3.org/2000/svg";

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

    const positions = {};

    nodes.forEach((node, i) => {

        const angle = (2 * Math.PI * i) / nodes.length;

        positions[node.id] = {

            x: centerX + radius * Math.cos(angle),

            y: centerY + radius * Math.sin(angle)

        };

    });

    const defs = document.createElementNS(SVG_NS, "defs");

    defs.innerHTML =
        '<marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">' +
        '<polygon points="0 0, 7 3, 0 6" fill="#888"></polygon>' +
        '</marker>';

    svg.appendChild(defs);

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
// Render a small node/edge diagram for a single ring/cycle
// ----------------------------------------

function renderRingDiagram(container, ring, caption, isFraud) {

    const SVG_NS = "http://www.w3.org/2000/svg";

    const wrapper = document.createElement("div");
    wrapper.style.display = "inline-block";
    wrapper.style.margin = "10px";
    wrapper.style.textAlign = "center";
    wrapper.style.verticalAlign = "top";

    const title = document.createElement("p");
    title.style.fontWeight = "bold";
    title.style.marginBottom = "4px";
    title.textContent = caption + ":  " + ring.join(" -> ") + " -> " + ring[0];

    wrapper.appendChild(title);

    const width = 260;
    const height = 220;

    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 " + width + " " + height);
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);
    svg.style.border = "1px solid #eee";
    svg.style.borderRadius = "8px";

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 40;

    const positions = ring.map((account, i) => {

        const angle = (2 * Math.PI * i) / ring.length - Math.PI / 2;

        return {

            id: account,

            x: centerX + radius * Math.cos(angle),

            y: centerY + radius * Math.sin(angle)

        };

    });

    const markerId = "ringArrow-" + Math.random().toString(36).slice(2);

    const defs = document.createElementNS(SVG_NS, "defs");

    defs.innerHTML =
        '<marker id="' + markerId + '" markerWidth="8" markerHeight="8" refX="8" refY="3" orient="auto">' +
        '<polygon points="0 0, 8 3, 0 6" fill="' + (isFraud ? "#F44336" : "#888") + '"></polygon>' +
        '</marker>';

    svg.appendChild(defs);

    for (let i = 0; i < positions.length; i++) {

        const from = positions[i];
        const to = positions[(i + 1) % positions.length];

        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const shorten = 16;

        const x2 = to.x - (dx / dist) * shorten;
        const y2 = to.y - (dy / dist) * shorten;

        const line = document.createElementNS(SVG_NS, "line");

        line.setAttribute("x1", from.x);
        line.setAttribute("y1", from.y);
        line.setAttribute("x2", x2);
        line.setAttribute("y2", y2);
        line.setAttribute("stroke", isFraud ? "#F44336" : "#888");
        line.setAttribute("stroke-width", "2");
        line.setAttribute("marker-end", "url(#" + markerId + ")");

        svg.appendChild(line);

    }

    positions.forEach(pos => {

        const circle = document.createElementNS(SVG_NS, "circle");

        circle.setAttribute("cx", pos.x);
        circle.setAttribute("cy", pos.y);
        circle.setAttribute("r", 14);
        circle.setAttribute("fill", isFraud ? "#F44336" : "#2196F3");
        circle.setAttribute("stroke", "#fff");
        circle.setAttribute("stroke-width", "2");

        svg.appendChild(circle);

        const label = document.createElementNS(SVG_NS, "text");

        label.setAttribute("x", pos.x);
        label.setAttribute("y", pos.y - 20);
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("font-size", "10");
        label.setAttribute("fill", "#333");
        label.textContent = pos.id;

        svg.appendChild(label);

    });

    wrapper.appendChild(svg);
    container.appendChild(wrapper);

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