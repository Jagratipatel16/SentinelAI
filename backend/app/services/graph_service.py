import json

import networkx as nx
from groq import Groq

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.core.config import settings

# Groq client is created once and reused across requests. Reused for the
# same LLM explanation pattern as ai_explanation.py, but kept separate here
# since graph explanations summarize the whole network rather than a single
# transaction.
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


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


# ----------------------------------------
# Explain Network (LLM)
# ----------------------------------------
# Summarizes the graph's key findings (summary stats, top connected
# accounts, mule accounts, fraud rings) and asks the LLM to explain what's
# happening in the network in plain language for a bank analyst. Falls back
# to a simple templated summary if no API key is configured or the LLM
# call fails, so the endpoint never breaks.

def _fallback_network_explanation(summary, highly_connected, mule_accounts, fraud_rings):

    lines = [
        f"The network contains {summary['total_accounts']} accounts linked by "
        f"{summary['total_transactions']} transactions."
    ]

    if mule_accounts:
        top_mule = mule_accounts[0]
        lines.append(
            f"{len(mule_accounts)} account(s) show mule-like behavior, "
            f"the most notable being '{top_mule['account']}' which received "
            f"funds from {top_mule['received_from']} different senders."
        )
    else:
        lines.append("No mule-like accounts were detected.")

    if fraud_rings:
        lines.append(
            f"{len(fraud_rings)} circular transfer pattern(s) involving a "
            f"fraud-flagged transaction were found, suggesting possible layering."
        )
    else:
        lines.append("No circular fraud rings were detected.")

    if highly_connected:
        top_hub = highly_connected[0]
        lines.append(
            f"'{top_hub['account']}' is the most connected account in the "
            f"network with {top_hub['connections']} connections."
        )

    return " ".join(lines)


def explain_network(db: Session):

    summary = get_graph_summary(db)
    highly_connected = get_highly_connected_accounts(db)
    mule_accounts = get_mule_accounts(db)
    fraud_rings = get_fraud_rings(db)

    if groq_client is None:
        return {
            "explanation": _fallback_network_explanation(
                summary, highly_connected, mule_accounts, fraud_rings
            )
        }

    prompt = f"""You are a fraud analyst assistant for a bank. Explain the following
transaction network summary in plain, professional language for a bank employee
reading a dashboard. Focus on what the patterns mean and why they might be
worth investigating. Keep it to 3-5 sentences.

Network summary:
- Total accounts: {summary['total_accounts']}
- Total transactions: {summary['total_transactions']}

Top highly connected accounts (account, number of connections):
{chr(10).join(f"- {a['account']}: {a['connections']}" for a in highly_connected[:5]) or "- None"}

Suspected mule accounts (account, number of distinct senders):
{chr(10).join(f"- {a['account']}: {a['received_from']}" for a in mule_accounts[:5]) or "- None"}

Fraud rings detected (closed transfer loops involving a fraud-flagged transaction):
{chr(10).join(" -> ".join(ring + [ring[0]]) for ring in fraud_rings[:5]) or "- None"}

Respond with plain text only (no JSON, no markdown headers)."""

    try:

        response = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )

        return {"explanation": response.choices[0].message.content.strip()}

    except Exception as e:

        print(f"[graph_service] LLM network explanation failed, using fallback: {e}")

        return {
            "explanation": _fallback_network_explanation(
                summary, highly_connected, mule_accounts, fraud_rings
            )
        }