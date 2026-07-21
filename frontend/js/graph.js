const API_URL = "http://127.0.0.1:8000";

// -------------------------------
// Check Login
// -------------------------------

const token = localStorage.getItem("access_token");

if (!token) {

    window.location.href = "login.html";

}

let network;
let graphData;
// -------------------------------
// Load Graph
// -------------------------------

async function loadGraph() {

    try {

        const response = await fetch(

            API_URL + "/graph/network",

            {

                method: "GET",

                headers: {

                    "Authorization": "Bearer " + token

                }

            }

        );

        const data = await response.json();

        console.log(data);

        const container = document.getElementById("network");

          graphData = {

            nodes: new vis.DataSet(data.nodes),

            edges: new vis.DataSet(data.edges)

        };

const options = {

    layout: {

        improvedLayout: true

    },

    nodes: {

        shape: "dot",

        size: 22,

        borderWidth: 2,

        font: {

            size: 16,

            color: "#000"

        }

    },

    edges: {

        arrows: {

            to: {

                enabled: true

            }

        },

        smooth: {

            enabled: true,

            type: "dynamic"

        },

        font: {

            size: 14,

            align: "top"

        },

        color: {

            color: "#666"

        }

    },

    physics: {

        enabled: true,

        barnesHut: {

            gravitationalConstant: -8000,

            centralGravity: 0.3,

            springLength: 180,

            springConstant: 0.04,

            damping: 0.09

        }

    },

    interaction: {

        hover: true,

        navigationButtons: true,

        keyboard: true

    }

};
network = new vis.Network(

    container,

    graphData,

    options

);

network.fit();
    }

    catch (error) {

        console.log(error);

        alert("Unable to load graph.");

    }

}


// -------------------------------
// Logout
// -------------------------------

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";

}

const summaryResponse = await fetch(

    API_URL + "/graph/summary",

    {

        headers: {

            "Authorization":"Bearer "+token

        }

    }

);

const summary = await summaryResponse.json();

document.getElementById("accounts").innerHTML =
summary.total_accounts;

document.getElementById("transactions").innerHTML =
summary.total_transactions;

document.getElementById("connections").innerHTML =
summary.connections;



function searchNode(){

    const account=document

    .getElementById("searchAccount")

    .value;

    const id=graphData.nodes.get(account);

    if(id){

        network.focus(

            account,

            {

                scale:1.6,

                animation:true

            }

        );

    }

    else{

        alert("Account Not Found");

    }

}
// -------------------------------
// Load Automatically
// -------------------------------

loadGraph();