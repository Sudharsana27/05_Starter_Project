
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from .models import (
    Employee,
    Role,
    SalaryComponent,
    SalaryRevision,
    SalaryStructure,
)


def get_structure(db: Session, employee_id: str, on_date: date):
    """Return salary components effective on the requested date."""
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise ValueError("Employee not found")

    rows = db.scalars(
        select(SalaryStructure)
        .where(
            SalaryStructure.employee_id == employee_id,
            SalaryStructure.effective_from <= on_date,
            or_(
                SalaryStructure.effective_to.is_(None),
                SalaryStructure.effective_to >= on_date,
            ),
        )
        .order_by(SalaryStructure.component_id)
    ).all()

    # Fail rather than silently returning an ambiguous salary structure.
    for index, row in enumerate(rows):
        for other in rows[index + 1:]:
            if row.component_id == other.component_id:
                raise ValueError(
                    f"Overlapping effective dates for component "
                    f"{row.component_id}"
                )

    return rows


def get_revision_history(db: Session, employee_id: str):
    """Return all revisions, oldest first."""
    if db.get(Employee, employee_id) is None:
        raise ValueError("Employee not found")

    return db.scalars(
        select(SalaryRevision)
        .where(SalaryRevision.employee_id == employee_id)
        .order_by(
            SalaryRevision.effective_from,
            SalaryRevision.revision_id,
        )
    ).all()


def revise_salary(
    db: Session,
    *,
    employee_id: str,
    effective_from: date,
    revision_reason: str,
    new_annual_fixed: Decimal,
    role_id_after: str,
    components: list[dict],
    approved_by: str | None = None,
):
    """Close the previous structure and create a new revision and structure."""
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise ValueError("Employee not found")

    if db.get(Role, role_id_after) is None:
        raise ValueError("Role not found")

    if not components:
        raise ValueError("At least one salary component is required")

    if new_annual_fixed <= 0:
        raise ValueError("Annual fixed salary must be positive")

    component_ids = [item["component_id"] for item in components]
    if len(component_ids) != len(set(component_ids)):
        raise ValueError("Duplicate component IDs are not allowed")

    component_models = {}
    for component_id in component_ids:
        component = db.get(SalaryComponent, component_id)
        if component is None:
            raise ValueError(f"Unknown salary component: {component_id}")
        component_models[component_id] = component

    # Prevent retroactive changes that would overlap existing later periods.
    future_rows = db.scalars(
        select(SalaryStructure).where(
            SalaryStructure.employee_id == employee_id,
            SalaryStructure.effective_from >= effective_from,
        )
    ).all()
    if future_rows:
        raise ValueError(
            "A structure already starts on or after this date; "
            "revise from a later date or correct the existing history first"
        )

    active_rows = db.scalars(
        select(SalaryStructure).where(
            SalaryStructure.employee_id == employee_id,
            SalaryStructure.effective_from < effective_from,
            or_(
                SalaryStructure.effective_to.is_(None),
                SalaryStructure.effective_to >= effective_from,
            ),
        )
    ).all()

    previous_revision = db.scalars(
        select(SalaryRevision)
        .where(SalaryRevision.employee_id == employee_id)
        .order_by(
            SalaryRevision.effective_from.desc(),
            SalaryRevision.revision_id.desc(),
        )
        .limit(1)
    ).first()

    previous_amount = (
        Decimal(str(previous_revision.new_annual_fixed))
        if previous_revision is not None
        else None
    )

    pct_change = None
    if previous_amount is not None and previous_amount > 0:
        pct_change = (
            (new_annual_fixed - previous_amount) / previous_amount
        ) * Decimal("100")

    revision_id = f"SR-{uuid4().hex[:12].upper()}"
    revision = SalaryRevision(
        revision_id=revision_id,
        employee_id=employee_id,
        effective_from=effective_from,
        revision_reason=revision_reason,
        previous_annual_fixed=previous_amount,
        new_annual_fixed=new_annual_fixed,
        pct_change=pct_change,
        role_id_after=role_id_after,
        approved_by=approved_by,
        created_at=datetime.utcnow(),
    )

    try:
        for row in active_rows:
            row.effective_to = effective_from - timedelta(days=1)

        db.add(revision)
        db.flush()

        for item in components:
            amount = Decimal(str(item["monthly_amount"]))
            if amount < 0:
                raise ValueError("Monthly amounts cannot be negative")

            component = component_models[item["component_id"]]
            db.add(
                SalaryStructure(
                    structure_id=f"SS-{uuid4().hex[:12].upper()}",
                    employee_id=employee_id,
                    component_id=component.component_id,
                    component_name=component.component_name,
                    component_type=component.component_type,
                    monthly_amount=amount,
                    effective_from=effective_from,
                    effective_to=None,
                    revision_id=revision_id,
                )
            )

        db.commit()
        db.refresh(revision)
        return revision

    except Exception:
        db.rollback()
        raise
