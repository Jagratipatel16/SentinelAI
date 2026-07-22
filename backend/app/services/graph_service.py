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
# A "fraud ring" is a circular transfer pattern (A -> B -> C -> A) where at
# least one transaction along the cycle was predicted/marked as "Fraud".
# This is a more actionable subset of circular_transfers below - it points
# investigators straight at loops that involve a confirmed-risky transaction,
# instead of every closed loop in the network (many of which may be
# legitimate, e.g. recurring payments between the same small group of users).

def get_fraud_rings(db: Session):

    G = build_graph(db)

    rings = []

    for cycle in nx.simple_cycles(G):

        has_fraud_edge = False

        for i in range(len(cycle)):

            source = cycle[i]
            target = cycle[(i + 1) % len(cycle)]

            edge_data = G.get_edge_data(source, target)

            if edge_data and edge_data.get("status") == "Fraud":
                has_fraud_edge = True
                break

        if has_fraud_edge:
            rings.append(cycle)

    return rings


# ----------------------------------------
# Circular Transfers
# ----------------------------------------
# All closed-loop transfer patterns in the network, regardless of fraud
# status. This is the broader signal (fraud_rings is a filtered subset of
# this) - useful for spotting unusual money-movement structures even before
# the ML model has flagged any single transaction as fraudulent.

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