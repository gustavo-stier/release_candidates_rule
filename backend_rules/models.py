from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base

db_engine = create_engine("sqlite:///banco.db")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)
    username = Column("username", String, unique=True, index=True, nullable=False)
    email = Column("email", String, unique=True, index=True, nullable=False)
    hashed_password = Column("hashed_password", String, nullable=False)
    admin = Column("admin", Boolean, default=False)

    def __init__(
        self, username: str, email: str, hashed_password: str, admin: bool = False
    ):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.admin = admin


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        UniqueConstraint("gateway_id", name="uq_rules_gateway"),  # 1 regra por gateway
    )

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)
    gateway_id = Column("gateway_id", Integer, nullable=False, index=True)
    gateway_name = Column("gateway_name", String(120), nullable=False)
    rule_name = Column("rule_name", String(120), nullable=False)
    enabled = Column("enabled", Boolean, nullable=False, default=True)

    # Quais campos canônicos compõem a regra (ordem importa)
    # Ex.: ["document", "amount", "date"]
    composite_key = Column("composite_key", JSON, nullable=False)

    # Mapeamento canônico -> paths no JSON do RC (com fallback)
    # Ex.: {"document": ["payment_information.user_document_number", "payment_information.reference_1"], ...}
    field_paths = Column("field_paths", JSON, nullable=False)

    # Tolerâncias (parametrização; sem aplicar lógica agora)
    # Ex.: {"date_window_days": 2, "amount": {"mode": "pct", "value": 1.0}}
    tolerance = Column("tolerance", JSON, nullable=True)

    def __init__(
        self,
        gateway_id: int,
        gateway_name: str,
        rule_name: str,
        enabled: bool,
        composite_key: list,
        field_paths: dict,
        tolerance: dict | None = None,
    ):
        self.gateway_id = gateway_id
        self.gateway_name = gateway_name
        self.rule_name = rule_name
        self.enabled = enabled
        self.composite_key = composite_key
        self.field_paths = field_paths
        self.tolerance = tolerance
