from pydantic import BaseModel


class GraphSummary(BaseModel):
    total_accounts: int
    total_transactions: int
    connections: int


class ConnectedAccount(BaseModel):
    account: str
    connections: int


class MuleAccount(BaseModel):
    account: str
    received_from: int