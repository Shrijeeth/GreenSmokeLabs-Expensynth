from sqlalchemy import TIMESTAMP, Column, Integer, MetaData, Numeric, String, Table

metadata = MetaData()

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("created_at", TIMESTAMP),
    Column("updated_at", TIMESTAMP),
    Column("user_id", Integer),
    Column("transaction_type", String),
    Column("amount", Numeric),
    Column("category", String),
    Column("third_party", String),
    Column("message", String),
)