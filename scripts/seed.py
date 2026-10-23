
from pathlib import Path

import pandas as pd
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Float,
    Date,
    DateTime,
    inspect,
    text,
)

from app.config import settings
from app.database import engine
from app import models  # Register existing ORM models


DATA_DIR = Path(settings.data_dir).resolve()
DICTIONARY_FILE = DATA_DIR / "data_dictionary.csv"
CHUNK_SIZE = 5000

# Parent tables first; child tables later.
PRIORITY = [
    "departments",
    "roles",
    "employees",
    "employee_assignments",
    "clients",
    "vendors",
    "chart_of_accounts",
    "leave_types",
    "holidays",
    "statutory_rates",
    "tax_parameters",
    "tax_slabs",
    "users",
    "attendance",
    "leave_balances",
    "leave_requests",
    "salary_components",
    "salary_structures",
    "salary_revisions",
    "performance_reviews",
    "payroll_runs",
    "payroll_items",
    "invoices",
    "invoice_items",
    "invoice_payments",
    "journal_entries",
    "journal_lines",
    "expenses",
]

EXCLUDED = {"data_dictionary"}


def load_dictionary():
    """Read column types from data_dictionary.csv."""
    df = pd.read_csv(DICTIONARY_FILE).fillna("")
    result = {}

    for row in df.to_dict(orient="records"):
        table_name = str(row["sheet"]).strip()
        column_name = str(row["column"]).strip()
        dtype = str(row["data_type"]).strip().lower()

        result.setdefault(table_name, {})[column_name] = dtype

    return result


def sqlalchemy_type(dtype):
    """Map dictionary types to SQLAlchemy types."""
    if dtype == "integer":
        return Integer()
    if dtype == "decimal":
        return Float()
    if dtype == "date":
        return Date()
    if dtype == "timestamp":
        return DateTime()
    return String()


def create_missing_tables(dictionary):
    """Create missing tables without changing existing table schemas."""
    metadata = MetaData()
    existing = set(inspect(engine).get_table_names())

    for name, columns in dictionary.items():
        if name in EXCLUDED or name in existing:
            continue

        table_columns = [
            Column(column_name, sqlalchemy_type(dtype), nullable=True)
            for column_name, dtype in columns.items()
        ]

        Table(name, metadata, *table_columns)

    metadata.create_all(engine)


def normalize_value(value, dtype):
    """Convert pandas values into SQLite-compatible Python values."""
    if pd.isna(value) or value == "":
        return None

    if dtype == "date":
        parsed = pd.to_datetime(value, errors="coerce")
        return parsed.date() if pd.notna(parsed) else None

    if dtype == "timestamp":
        parsed = pd.to_datetime(value, errors="coerce")
        return parsed.to_pydatetime() if pd.notna(parsed) else None

    if dtype == "integer":
        return int(value)

    if dtype == "decimal":
        return float(value)

    return str(value)


def csv_row_count(path):
    """Count CSV data rows without loading the whole file into memory."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        # CSV records can contain newlines inside quoted fields, so use
        # pandas chunking instead of counting physical lines.
        return sum(
            len(chunk)
            for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE)
        )


def main():
    if not DICTIONARY_FILE.exists():
        raise FileNotFoundError(
            f"Missing data dictionary: {DICTIONARY_FILE}"
        )

    dictionary = load_dictionary()

    csv_tables = {
        path.stem: path
        for path in DATA_DIR.glob("*.csv")
        if path.stem not in EXCLUDED
    }

    if not csv_tables:
        raise RuntimeError(f"No business CSV files found in {DATA_DIR}")

    missing = set(dictionary) - set(csv_tables) - EXCLUDED
    if missing:
        raise FileNotFoundError(
            f"CSV files missing for dictionary tables: {sorted(missing)}"
        )

    # Validate CSV headers against the dictionary before modifying data.
    for name, path in csv_tables.items():
        if name not in dictionary:
            raise ValueError(
                f"No data dictionary entries found for table: {name}"
            )

        header = pd.read_csv(path, nrows=0).columns.tolist()
        undocumented = set(header) - set(dictionary[name])

        if undocumented:
            raise ValueError(
                f"{name}.csv has undocumented columns: "
                f"{sorted(undocumented)}"
            )

        dictionary_columns = set(dictionary[name])
        missing_columns = set(header) - dictionary_columns
        if missing_columns:
            raise ValueError(
                f"Missing dictionary columns for {name}: "
                f"{sorted(missing_columns)}"
            )

    # Preserve existing ORM schemas and create only missing tables.
    create_missing_tables(dictionary)

    metadata = MetaData()
    tables = {
        name: Table(name, metadata, autoload_with=engine)
        for name in csv_tables
    }

    order = [name for name in PRIORITY if name in csv_tables]
    order.extend(sorted(set(csv_tables) - set(order)))

    # Calculate expected counts before beginning the refresh.
    expected_counts = {
        name: csv_row_count(path)
        for name, path in csv_tables.items()
    }

    print(f"Database: {engine.url}")
    print(f"CSV tables to load: {len(csv_tables)}")
    print(f"Chunk size: {CHUNK_SIZE}")

    # One transaction: either the complete refresh succeeds, or its
    # deletes and inserts are rolled back.
    with engine.begin() as connection:
        # Clear child tables before parent tables.
        for name in reversed(order):
            connection.execute(text(f'DELETE FROM "{name}"'))

        for name in order:
            path = csv_tables[name]
            loaded_rows = 0
            table = tables[name]
            types = dictionary[name]
            manager_links = []

            for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
                records = []

                for record in chunk.to_dict(orient="records"):
                    clean = {
                        column: normalize_value(value, types[column])
                        for column, value in record.items()
                    }

                    # Employees refer to other employees as managers.
                    # Insert them first without manager links, then restore
                    # the links after every employee row exists.
                    if name == "employees":
                        manager_id = clean.get("manager_id")

                        if manager_id is not None:
                            manager_links.append(
                                (clean["employee_id"], manager_id)
                            )

                        clean["manager_id"] = None

                    records.append(clean)

                if records:
                    connection.execute(table.insert(), records)
                    loaded_rows += len(records)

            if name == "employees" and manager_links:
                for employee_id, manager_id in manager_links:
                    connection.execute(
                        table.update()
                        .where(table.c.employee_id == employee_id)
                        .values(manager_id=manager_id)
                    )

            if loaded_rows != expected_counts[name]:
                raise RuntimeError(
                    f"{name}: expected {expected_counts[name]} rows, "
                    f"loaded {loaded_rows}"
                )

            print(f"{name}: {loaded_rows} rows loaded")

    # Verify persisted row counts after the transaction commits.
    with engine.connect() as connection:
        for name, expected in expected_counts.items():
            actual = connection.execute(
                text(f'SELECT COUNT(*) FROM "{name}"')
            ).scalar_one()

            if actual != expected:
                raise RuntimeError(
                    f"{name}: CSV has {expected} rows, "
                    f"database has {actual}"
                )

            print(f"Verified {name}: {actual} rows")

    print("\nAll CSV row counts verified successfully.")


if __name__ == "__main__":
    main()
