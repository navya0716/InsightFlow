import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Dataset, SalesTransaction, DataQualityCheck

REQUIRED = ["order_id","order_date","customer_id","product_id","product_name","category","region","quantity","unit_price","revenue"]

ALIASES = {
    "date":"order_date","sales":"revenue","amount":"revenue","qty":"quantity",
    "customer":"customer_id","product":"product_id","productname":"product_name"
}

def normalize_columns(df):
    df = df.copy()
    normalized = {}
    for c in df.columns:
        key = str(c).strip().lower().replace(" ","_").replace("-","_")
        normalized[c] = ALIASES.get(key, key)
    return df.rename(columns=normalized)

def process_csv(path: str, dataset_id: int, db: Session):
    ds = db.get(Dataset, dataset_id)
    ds.status = "processing"
    db.commit()
    try:
        raw = pd.read_csv(path)
        ds.row_count = len(raw)
        df = normalize_columns(raw)
        missing_cols = [c for c in REQUIRED if c not in df.columns]
        if missing_cols:
            ds.status="failed"
            ds.error_message=f"Missing required columns: {', '.join(missing_cols)}"
            db.commit()
            return ds

        df = df[REQUIRED].copy()
        original = len(df)
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce").dt.date
        for c in ["quantity","unit_price","discount","revenue"]:
            if c not in df.columns:
                df[c] = 0.0
            df[c] = pd.to_numeric(df[c], errors="coerce")

        # Calculate revenue when absent/invalid from quantity * unit price * (1-discount)
        computed = df["quantity"] * df["unit_price"] * (1 - df.get("discount", 0).fillna(0))
        df["revenue"] = df["revenue"].fillna(computed)

        duplicate_mask = df.duplicated(subset=["order_id","product_id"], keep="first")
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count:
            db.add(DataQualityCheck(dataset_id=dataset_id, check_type="duplicates",
                field_name="order_id/product_id", affected_rows=duplicate_count,
                severity="warning", message="Duplicate order-product records detected."))

        invalid = (
            df["order_date"].isna() |
            df["customer_id"].isna() |
            df["product_id"].isna() |
            df["quantity"].isna() | (df["quantity"] <= 0) |
            df["unit_price"].isna() | (df["unit_price"] < 0) |
            df["revenue"].isna() | (df["revenue"] < 0)
        )
        invalid_count = int(invalid.sum())
        missing_counts = df.isna().sum()
        for field, count in missing_counts[missing_counts > 0].items():
            db.add(DataQualityCheck(dataset_id=dataset_id, check_type="missing",
                field_name=str(field), affected_rows=int(count), severity="warning",
                message=f"{int(count)} missing values in {field}."))

        clean = df.loc[~invalid & ~duplicate_mask].copy()
        records = clean.to_dict("records")
        db.bulk_insert_mappings(SalesTransaction, [
            {"dataset_id":dataset_id, **r} for r in records
        ])

        quality = max(0, min(100, 100 * (1 - (invalid_count + duplicate_count) / max(original,1))))
        ds.valid_row_count = len(clean)
        ds.invalid_row_count = invalid_count
        ds.duplicate_row_count = duplicate_count
        ds.quality_score = round(quality,2)
        ds.status = "ready"
        ds.processed_at = datetime.utcnow()
        db.commit()
        return ds
    except Exception as exc:
        db.rollback()
        ds = db.get(Dataset, dataset_id)
        ds.status="failed"
        ds.error_message=str(exc)
        db.commit()
        return ds
