from .analytics import overview,revenue_trend,grouped,top_products,customer_value

def answer(db,dataset_id,q):
    s=q.lower().strip()
    if any(x in s for x in ["category","categories"]) and any(x in s for x in ["highest","most","top","revenue","sales"]):
        rows=grouped(db,dataset_id,"category")
        if not rows:return {"supported":True,"intent":"category","answer":"There is no data available yet.","metrics":{}}
        x=rows[0]; return {"supported":True,"intent":"highest_revenue_category","answer":f"{x['name']} is the highest-revenue category with ${x['revenue']:,.2f} in revenue.","metrics":x}
    if "region" in s and any(x in s for x in ["highest","most","top","revenue","sales"]):
        rows=grouped(db,dataset_id,"region"); x=rows[0] if rows else None
        return {"supported":True,"intent":"highest_region","answer":f"{x['name']} has the highest revenue at ${x['revenue']:,.2f}." if x else "No data available.","metrics":x or {}}
    if "product" in s and any(x in s for x in ["top","highest","best","revenue"]):
        rows=top_products(db,dataset_id); x=rows[0] if rows else None
        return {"supported":True,"intent":"top_product","answer":f"{x['name']} is the top product by revenue at ${x['revenue']:,.2f}." if x else "No data available.","metrics":x or {}}
    if "customer" in s and any(x in s for x in ["valuable","top","highest","best"]):
        rows=customer_value(db,dataset_id); x=rows[0] if rows else None
        return {"supported":True,"intent":"valuable_customer","answer":f"Customer {x['customer_id']} has the highest recorded revenue at ${x['revenue']:,.2f}." if x else "No data available.","metrics":x or {}}
    if "order" in s and any(x in s for x in ["how many","count","number"]):
        x=overview(db,dataset_id); return {"supported":True,"intent":"order_count","answer":f"There are {x['total_orders']:,} distinct orders in this dataset.","metrics":{"orders":x["total_orders"]}}
    if "trend" in s or "over time" in s:
        rows=revenue_trend(db,dataset_id); return {"supported":True,"intent":"revenue_trend","answer":f"The dataset contains {len(rows)} daily revenue observations. The trend can be explored in the Revenue Trend chart.","metrics":{"observations":len(rows)}}
    return {"supported":False,"intent":"unsupported","answer":"I can currently answer questions about highest-revenue categories, regions, top products, valuable customers, order count, and revenue trend.","metrics":{}}
