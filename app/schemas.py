
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: str
    department_name: str
    cost_center: str
    description: str | None = None


class EmployeeCreate(BaseModel):
    employee_id: str = Field(min_length=1, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    work_email: EmailStr
    hire_date: date
    employment_status: str = Field(min_length=1, max_length=30)
    employment_type: str = Field(min_length=1, max_length=30)
    department_id: str = Field(min_length=1, max_length=10)
    role_id: str = Field(min_length=1, max_length=10)
    manager_id: str | None = None
    work_location: str = Field(min_length=1, max_length=100)
    work_mode: str = Field(min_length=1, max_length=30)

    gender: str | None = None
    exit_date: date | None = None
    highest_education: str | None = None
    prior_experience_years: float | None = Field(default=None, ge=0)
    career_gap_months: int | None = Field(default=None, ge=0)
    commute_distance_km: float | None = Field(default=None, ge=0)
    pf_applicable: str = "Y"
    esi_applicable: str = "N"
    notice_period_days: int = Field(default=30, ge=0)


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    work_email: EmailStr | None = None
    employment_status: str | None = None
    employment_type: str | None = None
    department_id: str | None = None
    role_id: str | None = None
    manager_id: str | None = None
    work_location: str | None = None
    work_mode: str | None = None
    exit_date: date | None = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    work_email: str
    hire_date: date
    exit_date: date | None = None
    employment_status: str
    employment_type: str
    department_id: str
    role_id: str
    manager_id: str | None = None
    work_location: str
    work_mode: str
