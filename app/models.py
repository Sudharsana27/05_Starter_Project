
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Numeric, DateTime, CheckConstraint

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(
        String(10), primary_key=True
    )
    department_name: Mapped[str] = mapped_column(String(100))
    cost_center: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[str] = mapped_column(
        String(10), primary_key=True
    )
    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.department_id"), nullable=False
    )
    role_title: Mapped[str] = mapped_column(String(150))
    level: Mapped[int] = mapped_column(Integer)
    grade: Mapped[str] = mapped_column(String(50))
    band_min_annual: Mapped[int] = mapped_column(Integer)
    band_mid_annual: Mapped[int] = mapped_column(Integer)
    band_max_annual: Mapped[int] = mapped_column(Integer)
    overtime_eligible: Mapped[str] = mapped_column(String(1))
    band_year: Mapped[int] = mapped_column(Integer)


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(
        String(20), primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    full_name: Mapped[str] = mapped_column(String(200))
    work_email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    gender: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    date_of_birth: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    employment_status: Mapped[str] = mapped_column(String(30))
    employment_type: Mapped[str] = mapped_column(String(30))

    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.department_id"), nullable=False
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.role_id"), nullable=False
    )
    manager_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )

    work_location: Mapped[str] = mapped_column(String(100))
    work_mode: Mapped[str] = mapped_column(String(30))
    highest_education: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )
    prior_experience_years: Mapped[float | None] = mapped_column(
        nullable=True
    )
    career_gap_months: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    commute_distance_km: Mapped[float | None] = mapped_column(
        nullable=True
    )
    pf_applicable: Mapped[str] = mapped_column(String(1))
    esi_applicable: Mapped[str] = mapped_column(String(1))
    notice_period_days: Mapped[int] = mapped_column(Integer)
    resignation_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    exit_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    exit_reason: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    created_at: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )


class EmployeeAssignment(Base):
    __tablename__ = "employee_assignments"

    assignment_id: Mapped[str] = mapped_column(
        String(20), primary_key=True
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=False
    )
    effective_from: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    effective_to: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.department_id"), nullable=False
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.role_id"), nullable=False
    )
    job_level: Mapped[int] = mapped_column(Integer)
    manager_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )
    change_reason: Mapped[str] = mapped_column(String(100))


Index("ix_employees_department_id", Employee.department_id)
Index("ix_employees_manager_id", Employee.manager_id)


class SalaryComponent(Base):
    __tablename__ = "salary_components"

    component_id: Mapped[str] = mapped_column(
        String(20), primary_key=True
    )
    component_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    component_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    taxable: Mapped[str] = mapped_column(
        String(1), nullable=False
    )
    calculation_rule: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    is_fixed: Mapped[str] = mapped_column(
        String(1), nullable=False
    )


class SalaryRevision(Base):
    __tablename__ = "salary_revisions"

    revision_id: Mapped[str] = mapped_column(
        String(20), primary_key=True
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=False
    )
    effective_from: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    revision_reason: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    previous_annual_fixed: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    new_annual_fixed: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    pct_change: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 3), nullable=True
    )
    role_id_after: Mapped[str] = mapped_column(
        ForeignKey("roles.role_id"), nullable=False
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )


class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    structure_id: Mapped[str] = mapped_column(
        String(20), primary_key=True
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=False
    )
    component_id: Mapped[str] = mapped_column(
        ForeignKey("salary_components.component_id"), nullable=False
    )
    component_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    component_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    monthly_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    effective_from: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    effective_to: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    revision_id: Mapped[str] = mapped_column(
        ForeignKey("salary_revisions.revision_id"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_salary_structure_date_range",
        ),
        Index(
            "ix_salary_structure_employee_dates",
            "employee_id", "effective_from", "effective_to",
        ),
    )
