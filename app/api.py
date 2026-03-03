from flask import Blueprint, request, jsonify
from .db import get_db

bp = Blueprint("api", __name__)

# Allowlist of sortable columns to prevent SQL injection via ORDER BY
SORTABLE_COLUMNS = {
    "id", "name", "equip_slot", "effect", "acquisition_category",
    "buy_price_rupees", "sell_price_base",
    "defense_base", "defense_max",
    "resale_ratio", "defense_per_rupee", "max_defense_per_rupee",
}

def error(status: int, message: str):
    return jsonify({"error": message}), status

@bp.get("/health")
def health():
    return jsonify({"status": "ok"})

@bp.get("/armor")
def list_armor():
    """
    Examples:
      /armor?effect=Cold%20Resistance
      /armor?acquisition_category=chest
      /armor?min_defense_base=6&max_buy_price_rupees=500
      /armor?repurchasable=true
      /armor?sort=defense_max&order=desc&limit=50&offset=0
    """
    db = get_db()

    where = []
    params = []

    # --- Text filters ---
    name_contains = request.args.get("name_contains")
    if name_contains:
        where.append("name LIKE ?")
        params.append(f"%{name_contains}%")

    effect = request.args.get("effect")
    if effect:
        where.append("effect = ?")
        params.append(effect)

    acquisition_category = request.args.get("acquisition_category")
    if acquisition_category:
        where.append("acquisition_category = ?")
        params.append(acquisition_category)

    equip_slot = request.args.get("equip_slot")
    if equip_slot:
        where.append("equip_slot = ?")
        params.append(equip_slot)

    # --- Numeric filters ---
    def parse_int_arg(key):
        v = request.args.get(key)
        if v is None or v == "":
            return None
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"{key} must be an integer")

    def parse_float_arg(key):
        v = request.args.get(key)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"{key} must be a number")

    try:
        min_defense_base = parse_int_arg("min_defense_base")
        min_defense_max = parse_int_arg("min_defense_max")
        max_buy_price_rupees = parse_int_arg("max_buy_price_rupees")
        min_buy_price_rupees = parse_int_arg("min_buy_price_rupees")
        min_resale_ratio = parse_float_arg("min_resale_ratio")
    except ValueError as e:
        return error(400, str(e))

    if min_defense_base is not None:
        where.append("defense_base >= ?")
        params.append(min_defense_base)

    if min_defense_max is not None:
        where.append("defense_max >= ?")
        params.append(min_defense_max)

    if min_buy_price_rupees is not None:
        where.append("buy_price_rupees >= ?")
        params.append(min_buy_price_rupees)

    if max_buy_price_rupees is not None:
        where.append("buy_price_rupees <= ?")
        params.append(max_buy_price_rupees)

    if min_resale_ratio is not None:
        where.append("resale_ratio >= ?")
        params.append(min_resale_ratio)

    # --- Repurchase filter ---
    repurchasable = request.args.get("repurchasable")
    if repurchasable is not None:
        val = repurchasable.strip().lower()
        if val in {"true", "1", "yes", "y"}:
            where.append("repurchase_shop IS NOT NULL AND repurchase_shop != ''")
        elif val in {"false", "0", "no", "n"}:
            where.append("repurchase_shop IS NULL OR repurchase_shop = ''")
        else:
            return error(400, "repurchasable must be true/false")

    # --- Sorting / pagination ---
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc").lower()

    if sort not in SORTABLE_COLUMNS:
        return error(400, f"Invalid sort column. Allowed: {sorted(SORTABLE_COLUMNS)}")
    if order not in {"asc", "desc"}:
        return error(400, "order must be asc or desc")

    try:
        limit = int(request.args.get("limit", "100"))
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        return error(400, "limit and offset must be integers")

    limit = max(1, min(limit, 500))  # keep it sane
    offset = max(0, offset)

    q = "SELECT * FROM armor"
    if where:
        q += " WHERE " + " AND ".join(where)
    q += f" ORDER BY {sort} {order} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(q, params).fetchall()
    return jsonify([dict(r) for r in rows])

@bp.get("/armor/<int:item_id>")
def get_armor(item_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM armor WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return error(404, "armor item not found")
    return jsonify(dict(row))

@bp.get("/summary/acquisition")
def summary_acquisition():
    db = get_db()
    q = """
    SELECT acquisition_category,
           COUNT(*) AS count
    FROM armor
    GROUP BY acquisition_category
    ORDER BY count DESC;
    """
    rows = db.execute(q).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.get("/summary/effects")
def summary_effects():
    db = get_db()
    q = """
    SELECT COALESCE(effect, 'None') AS effect,
           COUNT(*) AS count
    FROM armor
    GROUP BY COALESCE(effect, 'None')
    ORDER BY count DESC;
    """
    rows = db.execute(q).fetchall()
    return jsonify([dict(r) for r in rows])

@bp.get("/recommendations/defense-value")
def rec_defense_value():
    db = get_db()
    limit = request.args.get("limit", "10")
    try:
        limit = int(limit)
    except ValueError:
        return error(400, "limit must be an integer")
    limit = max(1, min(limit, 50))

    q = """
    SELECT id, name, equip_slot,
           buy_price_rupees,
           defense_base, defense_max,
           defense_per_rupee, max_defense_per_rupee,
           effect, set_bonus, acquisition_category,
           source_1, repurchase_shop
    FROM armor
    WHERE max_defense_per_rupee IS NOT NULL
      AND buy_price_rupees IS NOT NULL
      AND buy_price_rupees > 0
    ORDER BY max_defense_per_rupee DESC
    LIMIT ?;
    """
    rows = db.execute(q, (limit,)).fetchall()
    return jsonify([dict(r) for r in rows])

@bp.get("/recommendations/top-defense")
def rec_top_defense():
    db = get_db()
    limit = request.args.get("limit", "10")
    try:
        limit = int(limit)
    except ValueError:
        return error(400, "limit must be an integer")
    limit = max(1, min(limit, 50))

    q = """
    SELECT id, name, equip_slot,
           defense_base, defense_max,
           effect, set_bonus,
           buy_price_rupees,
           acquisition_category,
           source_1, repurchase_shop
    FROM armor
    WHERE defense_max IS NOT NULL
    ORDER BY defense_max DESC, defense_base DESC
    LIMIT ?;
    """
    rows = db.execute(q, (limit,)).fetchall()
    return jsonify([dict(r) for r in rows])