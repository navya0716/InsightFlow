import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import SalesTransaction, CustomerSegment, Anomaly, ForecastRun, ForecastPoint

def forecast(db: Session, dataset_id:int, horizon:int=14):
    rows=db.query(SalesTransaction.order_date,func.sum(SalesTransaction.revenue)).filter(SalesTransaction.dataset_id==dataset_id).group_by(SalesTransaction.order_date).order_by(SalesTransaction.order_date).all()
    if len(rows)<3: return {"error":"At least 3 historical dates are required."}
    df=pd.DataFrame(rows,columns=["date","revenue"])
    df["date"]=pd.to_datetime(df["date"])
    idx=pd.date_range(df.date.min(),df.date.max(),freq="D")
    df=df.set_index("date").reindex(idx,fill_value=0).rename_axis("date").reset_index()
    x=np.arange(len(df)).reshape(-1,1); y=df.revenue.to_numpy()
    coef=np.polyfit(x.ravel(),y,1)
    future=np.arange(len(df),len(df)+horizon)
    preds=np.maximum(0,np.polyval(coef,future))
    run=ForecastRun(dataset_id=dataset_id,horizon_days=horizon,model_name="Linear Trend Baseline",model_summary="Transparent MVP baseline using daily revenue trend.")
    db.add(run); db.flush()
    recent_std=float(np.std(y[-min(14,len(y)):])) if len(y)>1 else 0
    points=[]
    last=df.date.max()
    for i,p in enumerate(preds,1):
        d=(last+pd.Timedelta(days=i)).date()
        point=ForecastPoint(forecast_run_id=run.id,forecast_date=d,predicted_revenue=float(p),
                            lower_bound=max(0,float(p-recent_std)),upper_bound=float(p+recent_std))
        db.add(point); points.append(point)
    db.commit()
    return {"run_id":run.id,"model_name":run.model_name,
            "history":[{"date":str(r.date.date()),"revenue":float(r.revenue)} for r in df.itertuples()],
            "forecast":[{"date":str(p.forecast_date),"predicted_revenue":round(p.predicted_revenue,2),
                         "lower_bound":round(p.lower_bound,2),"upper_bound":round(p.upper_bound,2)} for p in points]}

def segment(db,dataset_id:int,k:int=4):
    rows=db.query(SalesTransaction.customer_id,SalesTransaction.order_date,SalesTransaction.revenue).filter(SalesTransaction.dataset_id==dataset_id).all()
    if not rows: return {"error":"No data."}
    df=pd.DataFrame(rows,columns=["customer_id","date","revenue"]); df["date"]=pd.to_datetime(df.date)
    ref=df.date.max()+pd.Timedelta(days=1)
    r=df.groupby("customer_id").date.max().rsub(ref).dt.days
    f=df.groupby("customer_id").size()
    m=df.groupby("customer_id").revenue.sum()
    rfm=pd.DataFrame({"recency":r,"frequency":f,"monetary":m}).replace([np.inf,-np.inf],0).fillna(0)
    k=min(k,max(2,min(6,len(rfm))))
    X=StandardScaler().fit_transform(rfm)
    labels=KMeans(n_clusters=k,n_init=10,random_state=42).fit_predict(X)
    centers=rfm.assign(cluster=labels).groupby("cluster")[["recency","frequency","monetary"]].mean()
    names={}
    for c,row in centers.iterrows():
        if row.monetary >= centers.monetary.quantile(.75): names[c]="Champions"
        elif row.recency <= centers.recency.quantile(.25): names[c]="Loyal / Recent"
        elif row.recency >= centers.recency.quantile(.75): names[c]="At Risk"
        else: names[c]="Growth Customers"
    db.query(CustomerSegment).filter(CustomerSegment.dataset_id==dataset_id).delete()
    for cid,row in rfm.iterrows():
        db.add(CustomerSegment(dataset_id=dataset_id,customer_id=str(cid),recency=float(row.recency),
            frequency=float(row.frequency),monetary=float(row.monetary),cluster_id=int(labels[list(rfm.index).index(cid)]),
            segment_name=names[int(labels[list(rfm.index).index(cid)])]))
    db.commit()
    summary=rfm.assign(cluster=labels,segment=[names[int(x)] for x in labels]).groupby("segment").agg(
        customers=("cluster","size"),avg_recency=("recency","mean"),avg_frequency=("frequency","mean"),avg_monetary=("monetary","mean")).reset_index()
    return {"segments":[{k: (round(float(v),2) if isinstance(v,(float,np.floating)) else int(v) if isinstance(v,(int,np.integer)) else str(v)) for k,v in row.items()} for row in summary.to_dict("records")]}

def anomalies(db,dataset_id:int):
    rows=db.query(SalesTransaction).filter(SalesTransaction.dataset_id==dataset_id).all()
    if len(rows)<10: return {"error":"At least 10 transactions are required."}
    X=np.array([[r.revenue,r.quantity,r.unit_price] for r in rows],dtype=float)
    scores=IsolationForest(contamination="auto",random_state=42).fit_predict(X)
    model=IsolationForest(contamination=0.05,random_state=42).fit(X)
    decision=model.decision_function(X)
    db.query(Anomaly).filter(Anomaly.dataset_id==dataset_id).delete()
    out=[]
    for r,pred,score in zip(rows,scores,decision):
        flag=pred==-1
        if flag:
            a=Anomaly(dataset_id=dataset_id,transaction_id=r.id,anomaly_score=float(score),is_anomaly=True,reason="Unusual combination of revenue, quantity, and unit price")
            db.add(a)
            out.append({"transaction_id":r.id,"order_id":r.order_id,"revenue":r.revenue,"score":round(float(score),4),"category":r.category,"region":r.region})
    db.commit()
    return {"count":len(out),"anomalies":sorted(out,key=lambda x:x["score"])[:50]}
