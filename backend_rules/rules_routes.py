from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session  # noqa: F401

from dependecy import create_session, token_verify
from models import Rule, User  # noqa: F401
from schema import RuleOut, RuleSchema, RulesFilter, RulesPageSchema, UserSchema

rules_router = APIRouter(prefix="/rules", tags=["rules"])


@rules_router.post("/insert-rule")
async def insert_rule(
    rule_schema: RuleSchema,
    session: Session = Depends(create_session),
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(
            status_code=403, detail="User not authorized to insert rules"
        )
    gateway_id = (
        session.query(Rule).filter(Rule.gateway_id == rule_schema.gateway_id).first()  # type: ignore
    )
    if gateway_id:
        raise HTTPException(
            status_code=400,
            detail=f"Rule already exists for the gateway ID: {rule_schema.gateway_id}",
        )

    ck = set(rule_schema.composite_key)  # type: ignore
    fp = set(rule_schema.field_paths.keys())
    if not ck.issubset(fp):
        missing = ", ".join(sorted(ck - fp))
        raise HTTPException(
            status_code=422, detail=f"field_paths missing mappings for: {missing}"
        )

    new_rule = Rule(
        gateway_id=rule_schema.gateway_id,
        gateway_name=rule_schema.gateway_name,
        rule_name=rule_schema.rule_name,
        enabled=rule_schema.enabled,
        composite_key=rule_schema.composite_key,  # type: ignore
        field_paths=rule_schema.field_paths,
        tolerance=rule_schema.tolerance,
    )
    session.add(new_rule)
    session.commit()
    return {
        "message": "Rule inserted successfully",
        "rule_id": new_rule.id,
        "rule": new_rule,
    }


@rules_router.get("/get-rules/{gateway_id}")
async def get_rules(
    gateway_id: int,
    session: Session = Depends(create_session),
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="User not authorized to view rules")
    rule = session.query(Rule).filter(Rule.gateway_id == gateway_id).first()  # type: ignore
    if not rule:
        raise HTTPException(
            status_code=404, detail=f"No rule found for the Gateway ID: {gateway_id}"
        )
    return rule


@rules_router.get("", response_model=RulesPageSchema)
async def list_rules(
    filters: Annotated[RulesFilter, Depends()],
    session: Session = Depends(create_session),
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="User not authorized to view rules")

    query = session.query(Rule)

    if filters.gateway_id is not None:
        query = query.filter(Rule.gateway_id == filters.gateway_id)  # type: ignore
    if filters.rule_name is not None:
        query = query.filter(
            func.lower(Rule.rule_name) == filters.rule_name.value.lower()
        )
    if filters.enabled is not None:
        query = query.filter(Rule.enabled == filters.enabled)  # type: ignore
    if filters.q:
        like = f"%{filters.q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Rule.rule_name).like(like),
                func.lower(Rule.gateway_name).like(like),
            )
        )

    sort_col = getattr(Rule, filters.order_by, Rule.id)
    sort = sort_col.asc() if filters.order == "asc" else sort_col.desc()

    total = query.count()
    items = query.order_by(sort).offset(filters.offset).limit(filters.limit).all()

    return RulesPageSchema(
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        items=[RuleOut.model_validate(r) for r in items],
    )


@rules_router.delete("/delete-rule/{gateway_id}")
async def delete_rule(
    gateway_id: int,
    session: Session = Depends(create_session),
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(
            status_code=403, detail="User not authorized to delete rules"
        )
    rule = session.query(Rule).filter(Rule.gateway_id == gateway_id).first()  # type: ignore
    if not rule:
        raise HTTPException(
            status_code=404, detail=f"No rule found for the Gateway ID: {gateway_id}"
        )
    session.delete(rule)
    session.commit()
    return {"message": f"Rule for Gateway ID {gateway_id} deleted successfully"}


@rules_router.put("/rule-update/{gateway_id}")
async def rule_update(
    gateway_id: int,
    rule_schema: RuleSchema,
    session: Session = Depends(create_session),
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(
            status_code=403, detail="User not authorized to update rules"
        )
    rule = session.query(Rule).filter(Rule.gateway_id == gateway_id).first()  # type: ignore
    if not rule:
        raise HTTPException(
            status_code=404, detail=f"No rule found for the Gateway ID: {gateway_id}"
        )

    # Validate composite_key against field_paths
    ck = set(rule_schema.composite_key)  # type: ignore
    fp = set(rule_schema.field_paths.keys())
    if not ck.issubset(fp):
        missing = ", ".join(sorted(ck - fp))
        raise HTTPException(
            status_code=422, detail=f"field_paths missing mappings for: {missing}"
        )

    # Update rule fields
    rule.gateway_name = rule_schema.gateway_name
    rule.rule_name = rule_schema.rule_name
    rule.enabled = rule_schema.enabled
    rule.composite_key = rule_schema.composite_key  # type: ignore
    rule.field_paths = rule_schema.field_paths
    rule.tolerance = rule_schema.tolerance

    session.commit()
    session.refresh(rule)

    return {
        "message": "Rule updated successfully",
        "rule_id": rule.id,
        "rule": rule,
    }


@rules_router.patch("/rule-status/{gateway_id}")
async def update_rule_status(
    gateway_id: int,
    enabled: bool,
    session: Session = Depends(create_session),
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(
            status_code=403, detail="User not authorized to update rule status"
        )
    rule = session.query(Rule).filter(Rule.gateway_id == gateway_id).first()  # type: ignore
    if not rule:
        raise HTTPException(
            status_code=404, detail=f"No rule found for the Gateway ID: {gateway_id}"
        )

    rule.enabled = enabled
    session.commit()
    session.refresh(rule)

    return {
        "message": f"Rule {'enabled' if enabled else 'disabled'} successfully",
        "rule_id": rule.id,
        "rule": rule,
    }


@rules_router.get("/definitions")
async def list_rule_definitions(
    current_user: UserSchema = Depends(token_verify),
):
    if not current_user.admin:
        raise HTTPException(
            status_code=403, detail="User not authorized to view rule definitions"
        )
    return RuleSchema.RULE_NAME_DEFINITIONS
