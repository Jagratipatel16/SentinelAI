import networkx as nx

from sqlalchemy.orm import Session

from app.models.transaction import Transaction


# ----------------------------------------
# Create Graph
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

        connections = G.degree(node)

        accounts.append({

            "account": node,

            "connections": connections

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

    rings = list(nx.simple_cycles(G))

    return rings


# ----------------------------------------
# Circular Transfers
# ----------------------------------------

def get_circular_transfers(db: Session):

    G = build_graph(db)

    cycles = list(nx.simple_cycles(G))

    return cycles