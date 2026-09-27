from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from .database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(30), default="uploaded")
    row_count = Column(Integer, default=0)
    valid_row_count = Column(Integer, default=0)
    invalid_row_count = Column(Integer, default=0)
    duplicate_row_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

class SalesTransaction(Base):
    __tablename__ = "sales_transactions"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    order_id = Column(String(100), index=True)
    order_date = Column(Date, index=True)
    customer_id = Column(String(100), index=True)
    product_id = Column(String(100), index=True)
    product_name = Column(String(255))
    category = Column(String(100), index=True)
    region = Column(String(100), index=True)
    quantity = Column(Float)
    unit_price = Column(Float)
    discount = Column(Float, default=0)
    revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DataQualityCheck(Base):
    __tablename__ = "data_quality_checks"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    check_type = Column(String(80))
    field_name = Column(String(100))
    affected_rows = Column(Integer, default=0)
    severity = Column(String(20))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    customer_id = Column(String(100), index=True)
    recency = Column(Float)
    frequency = Column(Float)
    monetary = Column(Float)
    cluster_id = Column(Integer)
    segment_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    transaction_id = Column(Integer, index=True)
    anomaly_score = Column(Float)
    is_anomaly = Column(Boolean)
    reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class ForecastRun(Base):
    __tablename__ = "forecast_runs"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    horizon_days = Column(Integer)
    model_name = Column(String(100))
    model_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ForecastPoint(Base):
    __tablename__ = "forecast_points"
    id = Column(Integer, primary_key=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id"), index=True)
    forecast_date = Column(Date)
    predicted_revenue = Column(Float)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
