import pandas as pd
import os
import re

# -------------------------
# File paths (INPUT -> OUTPUT)
# -------------------------
INPUT_PATH = "data/raw/armor_raw.csv"
OUTPUT_PATH = "data/clean/armor_clean.csv"

# -------------------------
# Helpers: cleaning + typing
# -------------------------
MISSING_MARKERS = {"", "-", "—", "None", "null", "NULL"}

def to_text_or_null(value):
    """Normalize text fields: strip whitespace; return <NA> if empty/missing marker."""
    if pd.isna(value):
        return pd.NA
    s = str(value).strip()
    if s in MISSING_MARKERS:
        return pd.NA
    return s

def to_int_or_null(value):
    """
    Convert numeric-ish fields to nullable integers.
    Handles: '-', blanks, NaN, and numbers exported as floats (e.g., '50.0').
    """
    if pd.isna(value):
        return pd.NA
    s = str(value).strip()
    if s in MISSING_MARKERS:
        return pd.NA
    try:
        return int(float(s))
    except ValueError:
        return pd.NA

def safe_divide(numer, denom):
    """Return numer/denom if both valid and denom > 0; else <NA>."""
    if pd.isna(numer) or pd.isna(denom) or denom == 0:
        return pd.NA
    return float(numer) / float(denom)

def classify_acquisition(source_1, source_2, repurchase_shop):
    """
    Create a simple acquisition category from existing dataset fields.
    NOTE: This is a deterministic classification based on text signals.
    """
    repurchase_shop = to_text_or_null(repurchase_shop)
    s1 = to_text_or_null(source_1)
    s2 = to_text_or_null(source_2)

    # If it can be repurchased, that’s a strong "shop" signal.
    if repurchase_shop is not pd.NA:
        return "shop"

    # Combine sources into one string for keyword checks
    combined = " ".join([x for x in [s1, s2] if x is not pd.NA]).lower()

    if combined == "":
        return "unknown"

    # Keyword-based categories (you can expand later)
    if "treasure chest" in combined or "chest" in combined:
        return "chest"
    if "quest" in combined:
        return "quest"
    if "amiibo" in combined:
        return "amiibo"
    if "shop" in combined or "sold" in combined or "cece" in combined or "boutique" in combined:
        return "shop"

    # Default catch-all for other types of acquisition text
    return "other"

def main():
    # -------------------------
    # 1) Read raw CSV (DO NOT MODIFY RAW FILE)
    # -------------------------
    df = pd.read_csv(INPUT_PATH)

    # -------------------------
    # 2) Select columns we care about for analysis + context
    #    (Everything else stays in raw)
    # -------------------------
    keep_cols = [
        # Identity / context
        "Name",
        "Equip Slot",
        "Object Map Link",
        "Source 1",
        "Source 2",
        "Repurchase Shop",

        # Economics
        "Buy Price (Rupees)",
        "Buy Price (Poes)",
        "Sell Price (Base)",
        "Sell Price ★",
        "Sell Price ★★",
        "Sell Price ★★★",
        "Sell Price ★★★★",

        # Effects / bonuses
        "Effect",
        "Hidden Effect",
        "Set Bonus",
        "Hidden Set Bonus",
        "Dyeable",

        # Defense progression
        "Defense (Base)",
        "Defense ★",
        "Defense ★★",
        "Defense ★★★",
        "Defense ★★★★",
    ]

    # Upgrade materials (all stars + quantities)
    upgrade_cols = [
        "Upgrade Material ★ (1)", "Upgrade Material Quantity ★ (1)",
        "Upgrade Material ★ (2)", "Upgrade Material Quantity ★ (2)",
        "Upgrade Material ★ (3)", "Upgrade Material Quantity ★ (3)",

        "Upgrade Material ★★ (1)", "Upgrade Material Quantity ★★ (1)",
        "Upgrade Material ★★ (2)", "Upgrade Material Quantity ★★ (2)",
        "Upgrade Material ★★ (3)", "Upgrade Material Quantity ★★ (3)",

        "Upgrade Material ★★★ (1)", "Upgrade Material Quantity ★★★ (1)",
        "Upgrade Material ★★★ (2)", "Upgrade Material Quantity ★★★ (2)",
        "Upgrade Material ★★★ (3)", "Upgrade Material Quantity ★★★ (3)",

        "Upgrade Material ★★★★ (1)", "Upgrade Material Quantity ★★★★ (1)",
        "Upgrade Material ★★★★ (2)", "Upgrade Material Quantity ★★★★ (2)",
        "Upgrade Material ★★★★ (3)", "Upgrade Material Quantity ★★★★ (3)",
    ]

    keep_cols.extend(upgrade_cols)

    # Some CSV exports may omit a few columns. This keeps the script resilient.
    existing = [c for c in keep_cols if c in df.columns]
    missing = [c for c in keep_cols if c not in df.columns]
    if missing:
        print("Missing columns in CSV export (skipping):")
        for c in missing:
            print(f"  - {c}")

    df = df[existing].copy()

    # -------------------------
    # 3) Rename columns to clean snake_case
    # -------------------------
    rename_map = {
        "Name": "name",
        "Equip Slot": "equip_slot",
        "Object Map Link": "map_link",
        "Source 1": "source_1",
        "Source 2": "source_2",
        "Repurchase Shop": "repurchase_shop",

        "Buy Price (Rupees)": "buy_price_rupees",
        "Buy Price (Poes)": "buy_price_poes",
        "Sell Price (Base)": "sell_price_base",
        "Sell Price ★": "sell_price_1",
        "Sell Price ★★": "sell_price_2",
        "Sell Price ★★★": "sell_price_3",
        "Sell Price ★★★★": "sell_price_4",

        "Effect": "effect",
        "Hidden Effect": "hidden_effect",
        "Set Bonus": "set_bonus",
        "Hidden Set Bonus": "hidden_set_bonus",
        "Dyeable": "dyeable",

        "Defense (Base)": "defense_base",
        "Defense ★": "defense_1",
        "Defense ★★": "defense_2",
        "Defense ★★★": "defense_3",
        "Defense ★★★★": "defense_4",
    }

    # Upgrade columns: convert to snake_case-ish consistently
    # (We keep them explicit so you can see exactly what's happening.)
    for col in upgrade_cols:
        if col in df.columns:
            clean = col.lower()
            clean = clean.replace("upgrade material", "upgrade_material")
            clean = clean.replace("upgrade material quantity", "upgrade_material_qty")
            clean = clean.replace("quantity", "qty")
            clean = clean.replace("(", "").replace(")", "")
            clean = clean.replace(" ", "_")
            clean = clean.replace("★", "star")
            clean = re.sub(r"__+", "_", clean)
            rename_map[col] = clean

    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # -------------------------
    # 4) CLEANING / TYPE CONVERSIONS
    #    This is where we "treat" columns for analysis.
    # -------------------------

    # 4a) Text fields: strip whitespace & normalize missing markers to NULL
    text_cols = [
        "name", "equip_slot", "map_link", "source_1", "source_2", "repurchase_shop",
        "effect", "hidden_effect", "set_bonus", "hidden_set_bonus"
    ]
    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].apply(to_text_or_null)

    # 4b) Dyeable: normalize to boolean-ish (True/False/NULL)
    if "dyeable" in df.columns:
        def to_bool_or_null(v):
            v = to_text_or_null(v)
            if v is pd.NA:
                return pd.NA
            s = str(v).strip().lower()
            if s in {"true", "t", "yes", "y", "1"}:
                return True
            if s in {"false", "f", "no", "n", "0"}:
                return False
            return pd.NA
        df["dyeable"] = df["dyeable"].apply(to_bool_or_null)

    # 4c) Numeric fields: prices + defense as nullable integers
    numeric_int_cols = [
        "buy_price_rupees", "buy_price_poes",
        "sell_price_base", "sell_price_1", "sell_price_2", "sell_price_3", "sell_price_4",
        "defense_base", "defense_1", "defense_2", "defense_3", "defense_4",
    ]
    for c in numeric_int_cols:
        if c in df.columns:
            df[c] = df[c].apply(to_int_or_null).astype("Int64")

    # 4d) Upgrade quantities should be numeric; materials should be text
    # Materials
    for c in df.columns:
        if c.startswith("upgrade_material_star") and not c.startswith("upgrade_material_qty"):
            df[c] = df[c].apply(to_text_or_null)

    # Quantities
    for c in df.columns:
        if c.startswith("upgrade_material_qty_star"):
            df[c] = df[c].apply(to_int_or_null).astype("Int64")

    # -------------------------
    # 5) Derived fields / metrics (optional but helpful)
    # -------------------------

    # Acquisition category (NEW)
    df["acquisition_category"] = df.apply(
        lambda r: classify_acquisition(
            r.get("source_1", pd.NA),
            r.get("source_2", pd.NA),
            r.get("repurchase_shop", pd.NA),
        ),
        axis=1
    )

    # Defense max: use defense_4 as "max" where present
    if "defense_4" in df.columns:
        df["defense_max"] = df["defense_4"]
    else:
        df["defense_max"] = pd.NA

    # Resale ratio + efficiency metrics (only computed when buy_price exists)
    if "sell_price_base" in df.columns and "buy_price_rupees" in df.columns:
        df["resale_ratio"] = df.apply(lambda r: safe_divide(r["sell_price_base"], r["buy_price_rupees"]), axis=1)
        df["defense_per_rupee"] = df.apply(lambda r: safe_divide(r.get("defense_base", pd.NA), r["buy_price_rupees"]), axis=1)
        df["max_defense_per_rupee"] = df.apply(lambda r: safe_divide(r.get("defense_max", pd.NA), r["buy_price_rupees"]), axis=1)
    else:
        df["resale_ratio"] = pd.NA
        df["defense_per_rupee"] = pd.NA
        df["max_defense_per_rupee"] = pd.NA

    # -------------------------
    # 6) Basic row hygiene
    # -------------------------
    # Drop rows with no name (shouldn't happen, but safe)
    df = df[df["name"].notna()].copy()

    # -------------------------
    # 7) Write cleaned CSV
    # -------------------------
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Cleaned dataset saved to {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")
    print("Null counts (selected):")
    cols_to_check = [c for c in ["buy_price_rupees", "sell_price_base", "defense_base", "defense_max"] if c in df.columns]
    if cols_to_check:
        print(df[cols_to_check].isna().sum())

if __name__ == "__main__":
    main()
