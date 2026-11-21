"""Tiny helper to run the .sql files in /sql against a local DuckDB database."""
import duckdb

from config import DB_PATH, RAW_PATH, SQL_DIR


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def run_file(con, name, **params):
    """Execute a SQL file. Returns a DataFrame for files whose last statement is a SELECT."""
    sql = (SQL_DIR / name).read_text().replace("{raw_path}", str(RAW_PATH))
    for k, v in params.items():
        sql = sql.replace("{" + k + "}", str(v))
    # Strip "--" comments first so a ';' inside a comment can't split a statement.
    # (The project's SQL never uses '--' inside string literals.)
    sql = "\n".join(line.split("--", 1)[0] for line in sql.splitlines())
    statements = [s for s in sql.split(";") if s.strip()]
    result = None
    for stmt in statements:
        result = con.execute(stmt)
    try:
        return result.df()
    except Exception:
        return None


def build():
    con = connect()
    run_file(con, "00_build_clean_table.sql")
    n = con.execute("SELECT count(*) FROM bookings").fetchone()[0]
    print(f"[db] built table `bookings` with {n:,} rows")
    return con
