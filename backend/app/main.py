import os, shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .config import settings
from .database import Base, engine, get_db
from .models import Dataset, DataQualityCheck
from .schemas import DatasetOut, AnalystRequest
from .services.etl import process_csv
from .services.analytics import overview,revenue_trend,grouped,top_products,customer_value
from .services.ml import forecast,segment,anomalies
from .services.analyst import answer

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir,exist_ok=True)

app=FastAPI(title="InsightFlow API",version="1.0.0",description="Business intelligence and ML API")

origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins or ["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status":"ok","service":"insightflow-api","database":"configured"}

@app.get("/api/datasets",response_model=list[DatasetOut])
def datasets(db:Session=Depends(get_db)):
    return db.query(Dataset).order_by(desc(Dataset.created_at)).all()

@app.get("/api/datasets/{dataset_id}",response_model=DatasetOut)
def dataset(dataset_id:int,db:Session=Depends(get_db)):
    x=db.get(Dataset,dataset_id)
    if not x: raise HTTPException(404,"Dataset not found")
    return x

@app.post("/api/datasets/upload",response_model=DatasetOut)
async def upload(file:UploadFile=File(...),db:Session=Depends(get_db)):
    if not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Only CSV files are supported.")
    safe=os.path.basename(file.filename)
    ds=Dataset(filename=safe,status="uploaded",created_at=datetime.utcnow())
    db.add(ds); db.commit(); db.refresh(ds)
    path=os.path.join(settings.upload_dir,f"dataset_{ds.id}.csv")
    with open(path,"wb") as out: shutil.copyfileobj(file.file,out)
    process_csv(path,ds.id,db)
    db.refresh(ds)
    return ds

@app.get("/api/datasets/{dataset_id}/quality")
def quality(dataset_id:int,db:Session=Depends(get_db)):
    ds=db.get(Dataset,dataset_id)
    if not ds: raise HTTPException(404,"Dataset not found")
    checks=db.query(DataQualityCheck).filter(DataQualityCheck.dataset_id==dataset_id).all()
    return {"dataset":DatasetOut.model_validate(ds).model_dump(),"checks":[
        {"check_type":c.check_type,"field":c.field_name,"affected_rows":c.affected_rows,"severity":c.severity,"message":c.message} for c in checks]}

def require_ready(dataset_id,db):
    ds=db.get(Dataset,dataset_id)
    if not ds or ds.status!="ready": raise HTTPException(400,"Dataset is not ready.")
    return ds

@app.get("/api/analytics/overview")
def analytics_overview(dataset_id:int,db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return overview(db,dataset_id)

@app.get("/api/analytics/revenue-trend")
def analytics_trend(dataset_id:int,db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return revenue_trend(db,dataset_id)

@app.get("/api/analytics/category-performance")
def category_performance(dataset_id:int,db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return grouped(db,dataset_id,"category")

@app.get("/api/analytics/region-performance")
def region_performance(dataset_id:int,db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return grouped(db,dataset_id,"region")

@app.get("/api/analytics/top-products")
def products(dataset_id:int,db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return top_products(db,dataset_id)

@app.get("/api/analytics/customer-distribution")
def customers(dataset_id:int,db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return customer_value(db,dataset_id)

@app.post("/api/ml/forecast")
def ml_forecast(dataset_id:int=Query(...),horizon:int=Query(14,ge=7,le=30),db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return forecast(db,dataset_id,horizon)

@app.post("/api/ml/segments")
def ml_segments(dataset_id:int=Query(...),db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return segment(db,dataset_id)

@app.post("/api/ml/anomalies")
def ml_anomalies(dataset_id:int=Query(...),db:Session=Depends(get_db)):
    require_ready(dataset_id,db); return anomalies(db,dataset_id)

@app.post("/api/analyst/ask")
def analyst(req:AnalystRequest,db:Session=Depends(get_db)):
    require_ready(req.dataset_id,db); return answer(db,req.dataset_id,req.question)
