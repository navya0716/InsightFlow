from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from ..models import SalesTransaction

def _base(db, dataset_id):
    return db.query(SalesTransaction).filter(SalesTransaction.dataset_id == dataset_id)

def overview(db: Session, dataset_id: int):
    q=_base(db,dataset_id)
    revenue=q.with_entities(func.coalesce(func.sum(SalesTransaction.revenue),0)).scalar() or 0
    orders=q.with_entities(func.count(func.distinct(SalesTransaction.order_id))).scalar() or 0
    customers=q.with_entities(func.count(func.distinct(SalesTransaction.customer_id))).scalar() or 0
    products=q.with_entities(func.count(func.distinct(SalesTransaction.product_id))).scalar() or 0
    return {"total_revenue":round(revenue,2),"total_orders":orders,"total_customers":customers,
            "average_order_value":round(revenue/orders,2) if orders else 0,
            "total_products":products}

def revenue_trend(db,dataset_id):
    rows=_base(db,dataset_id).with_entities(SalesTransaction.order_date,func.sum(SalesTransaction.revenue)).group_by(SalesTransaction.order_date).order_by(SalesTransaction.order_date).all()
    return [{"date":str(d),"revenue":round(float(v or 0),2)} for d,v in rows]

def grouped(db,dataset_id,field):
    col=getattr(SalesTransaction,field)
    rows=_base(db,dataset_id).with_entities(col,func.sum(SalesTransaction.revenue)).group_by(col).order_by(desc(func.sum(SalesTransaction.revenue))).all()
    return [{"name":str(n),"revenue":round(float(v or 0),2)} for n,v in rows]

def top_products(db,dataset_id):
    rows=_base(db,dataset_id).with_entities(SalesTransaction.product_name,func.sum(SalesTransaction.revenue),func.sum(SalesTransaction.quantity)).group_by(SalesTransaction.product_name).order_by(desc(func.sum(SalesTransaction.revenue))).limit(10).all()
    return [{"name":str(n),"revenue":round(float(r or 0),2),"quantity":round(float(q or 0),2)} for n,r,q in rows]

def customer_value(db,dataset_id):
    rows=_base(db,dataset_id).with_entities(SalesTransaction.customer_id,func.sum(SalesTransaction.revenue)).group_by(SalesTransaction.customer_id).order_by(desc(func.sum(SalesTransaction.revenue))).limit(10).all()
    return [{"customer_id":str(c),"revenue":round(float(r or 0),2)} for c,r in rows]
