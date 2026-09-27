import random, argparse
from datetime import date,timedelta
import pandas as pd
from .database import Base,engine,SessionLocal
from .models import Dataset
from .services.etl import process_csv

def generate(rows=12000,path="sample_data.csv"):
    random.seed(42)
    products=[("P001","Laptop Pro","Electronics"),("P002","Wireless Headphones","Electronics"),("P003","Office Chair","Home"),("P004","Standing Desk","Home"),("P005","Running Shoes","Sports"),("P006","Fitness Watch","Sports"),("P007","Coffee Maker","Appliances"),("P008","Backpack","Accessories"),("P009","Smartphone","Electronics"),("P010","Desk Lamp","Home")]
    regions=["North","South","East","West","Central"]
    customers=[f"C{i:04d}" for i in range(1,801)]
    start=date.today()-timedelta(days=240)
    out=[]
    for i in range(rows):
        pid,pname,cat=random.choice(products)
        qty=random.randint(1,6); price=random.choice([19.99,29.99,49.99,79.99,119.99,199.99,399.99,799.99])
        discount=random.choice([0,.0,.05,.10,.15])
        revenue=round(qty*price*(1-discount),2)
        if i%997==0: revenue*=4
        out.append({
            "order_id":f"O{i//2+1:06d}","order_date":str(start+timedelta(days=random.randint(0,239))),
            "customer_id":random.choice(customers),"product_id":pid,"product_name":pname,
            "category":cat,"region":random.choice(regions),"quantity":qty,"unit_price":price,
            "discount":discount,"revenue":revenue})
    df=pd.DataFrame(out)
    # Deliberately add a few quality issues
    df.loc[5,"quantity"]=None
    df.loc[10,"revenue"]=None
    df=pd.concat([df,df.iloc[[20,21]]],ignore_index=True)
    df.to_csv(path,index=False)
    return path

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--rows",type=int,default=12000); args=parser.parse_args()
    Base.metadata.create_all(bind=engine)
    path=generate(args.rows)
    db=SessionLocal()
    ds=Dataset(filename=path,status="uploaded"); db.add(ds); db.commit(); db.refresh(ds)
    process_csv(path,ds.id,db)
    print(f"Seeded dataset id={ds.id}")
