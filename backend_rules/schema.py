from enum import Enum
from typing import ClassVar, Dict, List, Literal, Optional

from fastapi import HTTPException
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

CompositeField = Literal[
    "payment_id",
    "document",
    "bank_accountamount",
    "date",
    "check_provider_status",
    "reference",
    "deposit_id",
    "amount",
    "bank_account",
]


class UserSchema(BaseModel):
    username: str
    email: str
    hashed_password: str
    admin: Optional[bool] = False

    ALLOWED_DOMAINS: ClassVar[set[str]] = {
        "eroninternational.com",
        "directa24.com",
        "d24.com",
    }

    class Config:
        from_attributes = True

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: EmailStr) -> EmailStr:
        domain = v.split("@", 1)[1].lower()
        if not any(
            domain == d or domain.endswith("." + d) for d in cls.ALLOWED_DOMAINS
        ):
            allowed_list = ", ".join(sorted(cls.ALLOWED_DOMAINS))
            raise HTTPException(
                status_code=400,
                detail=f"Company domain not allowed: ({domain}). Allowed domains: ({allowed_list})",
            )
        return v


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class RuleSchema(BaseModel):
    RULE_NAME_DEFINITIONS: ClassVar[dict[str, List[CompositeField]]] = {
        "transaction": ["payment_id", "amount", "date"],
        "document": ["document", "amount", "date"],
        "document_check_provider": [
            "document",
            "amount",
            "date",
            "check_provider_status",
        ],
        "reference": ["reference", "amount", "date"],
        "deposit_id": ["deposit_id", "amount", "date"],
        "customer_document_reference": ["document", "reference", "amount", "date"],
        "bank_account": ["bank_account", "amount", "date"],
    }  # type: ignore

    gateway_id: int
    gateway_name: str
    rule_name: str
    enabled: bool = True
    composite_key: Optional[List[CompositeField]] = None
    field_paths: Dict[CompositeField, str]
    tolerance: Optional[dict] = None

    class Config:
        from_attributes = True

    @field_validator("rule_name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        normalized = v.strip()
        if not normalized:
            raise ValueError("rule_name cannot be empty")
        if normalized not in cls.RULE_NAME_DEFINITIONS:
            allowed = ", ".join(cls.RULE_NAME_DEFINITIONS)
            raise ValueError(f"rule_name must be one of: {allowed}")
        return normalized

    @field_validator("field_paths")
    @classmethod
    def no_empty_paths(cls, v: Dict[str, str]) -> Dict[str, str]:
        for k, path in v.items():
            if not path or not path.strip():
                raise ValueError(f"Empty path for {k}")
        return v

    @model_validator(mode="after")
    def validate_rule_definition(self) -> "RuleSchema":
        expected_fields = self.RULE_NAME_DEFINITIONS[self.rule_name]
        if not self.composite_key:
            self.composite_key = expected_fields.copy()
        elif list(self.composite_key) != expected_fields:
            expected_str = ", ".join(expected_fields)
            raise ValueError(
                f"composite_key for '{self.rule_name}' must be [{expected_str}]"
            )

        provided_keys = set(self.field_paths.keys())
        expected_keys = set(expected_fields)

        missing = expected_keys - provided_keys
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(
                f"field_paths missing mappings for '{self.rule_name}': {missing_str}"
            )

        unexpected = provided_keys - expected_keys
        if unexpected:
            unexpected_str = ", ".join(sorted(unexpected))
            raise ValueError(
                f"field_paths contains unsupported keys for '{self.rule_name}': {unexpected_str}"
            )

        return self


class RuleKind(str, Enum):
    transaction = "transaction"
    document = "document"
    document_check_provider = "document_check_provider"


class RuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    gateway_id: int
    gateway_name: str
    rule_name: RuleKind
    enabled: bool
    composite_key: List[str]
    field_paths: Dict[str, str]
    tolerance: Optional[dict] = None


class RuleStatusUpdate(BaseModel):
    enabled: bool


class RulesPageSchema(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[RuleOut]


class RulesFilter(BaseModel):
    gateway_id: Optional[int] = Field(None, description="Gateway ID to filter")
    rule_name: Optional[RuleKind] = None
    enabled: Optional[bool] = None
    q: Optional[str] = Field(None, description="Busca por rule_name/gateway_name")
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["id", "created_at", "updated_at"] = "id"
    order: Literal["asc", "desc"] = "desc"
