import sqlite3
import os
import csv
import argparse
import re

def clean_sql_col(col: str) -> str:
    """
    Convert CSV column names to safe SQLite column names.
    Your cleaned CSV is already snake_case, but this keeps it robust.
    """
    c = col.strip().lower()
    c = re.sub(r"[^a-z0-9_]+", "_", c)
    c = re.sub(r"_+", "_", c).strip("_")
    if c == "":
        c = "col"
    return c

def infer_type(sample_values):
    """
    Basic type inference for SQLite: INTEGER, REAL, TEXT
    We keep it simple and safe.
    """
    vals = [v for v in sample_values if v not in (None, "", "NA", "NaN")]
    if not vals:
        return "TEXT"
    # try integer
    try:
        for v in vals[:50]:
            int(v)
        return "INTEGER"
    except:
        pass
    # try float
    try:
        for v in vals[:50]:
            float(v)
        return "REAL"
    except:
        return "TEXT"

def create_db_from_csv(db_path: str, csv_path: str, table_name: str = "armor"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if not fieldnames:
            raise ValueError("CSV has no header row.")

        # Peek some rows to infer types
        rows_preview = []
        for _, row in zip(range(200), reader):
            rows_preview.append(row)

    # Map columns to safe SQL column names
    col_map = {c: clean_sql_col(c) for c in fieldnames}

    # Infer types from preview
    col_types = {}
    for orig_col in fieldnames:
        samples = [r.get(orig_col) for r in rows_preview]
        col_types[col_map[orig_col]] = infer_type(samples)

    # Build CREATE TABLE
    cols_sql = ",\n  ".join([f"{col} {col_types[col]}" for col in col_types])
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      {cols_sql}
    );
    """

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(create_sql)
    conn.commit()

    # Insert rows (need to re-read CSV from start)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = [col_map[c] for c in fieldnames]
        placeholders = ", ".join(["?"] * len(cols))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"

        batch = []
        total = 0
        for row in reader:
            values = []
            for orig_col in fieldnames:
                v = row.get(orig_col)
                # Keep empty strings as NULL
                if v is None or v.strip() == "":
                    values.append(None)
                else:
                    values.append(v.strip())
            batch.append(values)

            if len(batch) >= 1000:
                cur.executemany(insert_sql, batch)
                conn.commit()
                total += len(batch)
                batch = []

        if batch:
            cur.executemany(insert_sql, batch)
            conn.commit()
            total += len(batch)

    conn.close()
    print(f"✅ Created/updated {db_path}")
    print(f"✅ Loaded {total} rows into table '{table_name}' from {csv_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="data/armor.db")
    p.add_argument("--csv", required=True, help="Path to cleaned CSV to load")
    p.add_argument("--table", default="armor")
    args = p.parse_args()

    create_db_from_csv(args.db, args.csv, args.table)