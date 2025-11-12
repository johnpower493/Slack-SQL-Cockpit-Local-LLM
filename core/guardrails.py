import re

ALLOWED_SELECT = re.compile(r"^\s*(WITH\s+.+?AS\s*\(.*?\)\s*)*SELECT\b", re.IGNORECASE | re.DOTALL)

def sanitize_sql(sql: str, default_limit: int = 500) -> tuple[bool, str, str]:
    """
    Returns (ok, sql_out, reason_if_not_ok).
    - Only allow SELECT (and optional CTE `WITH`…).
    - Strip trailing semicolon.
    - If no LIMIT present, append LIMIT <default_limit>.
    """
    if not sql or not isinstance(sql, str):
        return False, "", "empty_sql"

    # drop fences / accidental prefixes
    s = sql.strip().strip("`")
    s = re.sub(r"^sql\s*\n", "", s, flags=re.IGNORECASE).strip()
    s = s.rstrip(";").strip()

    # must start with SELECT (optionally WITH…)
    if not ALLOWED_SELECT.match(s):
        return False, "", "non_select_or_unsafe"

    # basic disallow (best-effort)
    forbidden = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|ATTACH|DETACH|PRAGMA)\b"
    if re.search(forbidden, s, flags=re.IGNORECASE):
        return False, "", "forbidden_keyword"

    # Add LIMIT if not present
    if not re.search(r"\bLIMIT\b\s+\d+", s, flags=re.IGNORECASE):
        s = f"{s} LIMIT {default_limit}"

    return True, s, ""
