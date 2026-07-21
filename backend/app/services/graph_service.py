import networkx as nx

from sqlalchemy.orm import Session

from app.models.transaction import Transaction


# ----------------------------------------
# Create NetworkX Graph
# ----------------------------------------

def build_graph(db: Session):

    G = nx.DiGraph()

    transactions = db.query(Transaction).all()

    for transaction in transactions:

        G.add_edge(

            transaction.sender,
            transaction.receiver,

            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            status=transaction.status

        )

    return G


# ----------------------------------------
# Graph Summary
# ----------------------------------------

def get_graph_summary(db: Session):

    G = build_graph(db)

    return {

        "total_accounts": G.number_of_nodes(),

        "total_transactions": G.number_of_edges(),

        "connections": G.number_of_edges()

    }


# ----------------------------------------
# Highly Connected Accounts
# ----------------------------------------

def get_highly_connected_accounts(db: Session):

    G = build_graph(db)

    accounts = []

    for node in G.nodes():

        accounts.append({

            "account": node,

            "connections": G.degree(node)

        })

    accounts.sort(

        key=lambda x: x["connections"],

        reverse=True

    )

    return accounts[:10]


# ----------------------------------------
# Mule Accounts
# ----------------------------------------

def get_mule_accounts(db: Session):

    G = build_graph(db)

    mule_accounts = []

    for node in G.nodes():

        incoming = G.in_degree(node)

        if incoming >= 2:

            mule_accounts.append({

                "account": node,

                "received_from": incoming

            })

    mule_accounts.sort(

        key=lambda x: x["received_from"],

        reverse=True

    )

    return mule_accounts


# ----------------------------------------
# Fraud Rings
# ----------------------------------------

def get_fraud_rings(db: Session):

    G = build_graph(db)

    return list(nx.simple_cycles(G))


# ----------------------------------------
# Circular Transfers
# ----------------------------------------

def get_circular_transfers(db: Session):

    G = build_graph(db)

    return list(nx.simple_cycles(G))


# ----------------------------------------
# Network Graph
# ----------------------------------------

def get_network_graph(db: Session):

    transactions = db.query(Transaction).all()

    nodes = {}

    edges = []

    for transaction in transactions:

        sender = transaction.sender

        receiver = transaction.receiver

        # ---------------- Sender Node ----------------

        if sender not in nodes:

            nodes[sender] = {

                "id": sender,

                "label": sender,

                "color": "#4CAF50",

                "size": 20

            }

        # ---------------- Receiver Node ----------------

        if receiver not in nodes:

            nodes[receiver] = {

                "id": receiver,

                "label": receiver,

                "color": "#2196F3",

                "size": 20

            }

        # ---------------- Fraud Highlight ----------------

        if transaction.status == "Fraud":

            nodes[sender]["color"] = "#F44336"

            nodes[sender]["size"] = 35

            nodes[receiver]["color"] = "#F44336"

            nodes[receiver]["size"] = 35

        # ---------------- Edge ----------------

        edges.append({

            "from": sender,

            "to": receiver,

            "label": str(transaction.amount),

            "title": f"""
<b>Transaction Details</b><br><br>

Sender : {sender}<br>

Receiver : {receiver}<br>

Type : {transaction.transaction_type}<br>

Amount : ₹{transaction.amount}<br>

Status : {transaction.status}
""",

            "arrows": "to",

            "smooth": {

                "type": "curvedCW",

                "roundness": 0.2

            }

        })

    return {

        "nodes": list(nodes.values()),

        "edges": edges

    }