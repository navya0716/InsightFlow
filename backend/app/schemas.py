from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    status: str
    row_count: int
    valid_row_count: int
    invalid_row_count: int
    duplicate_row_count: int
    quality_score: float
    created_at: datetime
    processed_at: datetime | None = None
    error_message: str | None = None

class AnalystRequest(BaseModel):
    dataset_id: int
    question: str

class AnalystResponse(BaseModel):
    supported: bool
    intent: str
    answer: str
    metrics: dict = {}
