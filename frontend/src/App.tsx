import {useEffect,useState} from "react";
import {NavLink,Route,Routes} from "react-router-dom";
import {AreaChart,Area,XAxis,YAxis,Tooltip,ResponsiveContainer,BarChart,Bar} from "recharts";
import * as A from "./api";

const nav=[
  ["Overview","/overview"],
  ["Datasets","/datasets"],
  ["Data Quality","/data-quality"],
  ["Analytics","/analytics"],
  ["ML Models","/ml-models/forecast"],
  ["AI Analyst","/ai-analyst"],
  ["Insights","/insights"],
  ["Settings","/settings"]
];

const Icon=({children}:{children:string})=>
  <span className="nav-icon">{children}</span>;

function Layout(){
  const [datasets,setDatasets]=useState<any[]>([]);
  const [active,setActive]=useState<number|undefined>();

  useEffect(()=>{
    A.getDataset()
      .then(r=>{
        setDatasets(r.data);
        const ready=r.data.find((x:any)=>x.status==="ready");
        if(ready)setActive(ready.id);
      })
      .catch(()=>{});
  },[]);

  return <div className="app">
    <aside className="sidebar">
      <div className="brand">
        <span className="logo">I</span>
        <span>InsightFlow</span>
      </div>

      <div className="side-label">WORKSPACE</div>

      <nav>
        {nav.map(([n,p])=>
          <NavLink
            key={p}
            to={p}
            className={({isActive})=>isActive?"active":""}
          >
            <Icon>{n[0]}</Icon>
            {n}
          </NavLink>
        )}
      </nav>

      <div className="side-bottom">
        <div className="avatar">NS</div>
        <div>
          <b>Portfolio MVP</b>
          <small>Analytics workspace</small>
        </div>
      </div>
    </aside>

    <div className="main">
      <header className="topbar">
        <div>
          <span className="crumb">Workspace</span>
          <span className="slash">/</span>
          <b>{location.pathname.replace("/","")||"overview"}</b>
        </div>

        <div className="top-actions">
          <span className="live-dot"></span>
          System operational
        </div>
      </header>

      <Routes>
        <Route path="/overview" element={<Overview active={active}/>}/>
        <Route
          path="/datasets"
          element={
            <Datasets
              setActive={setActive}
              datasets={datasets}
              setDatasets={setDatasets}
            />
          }
        />
        <Route path="/data-quality" element={<Quality active={active}/>}/>
        <Route path="/analytics" element={<Analytics active={active}/>}/>
        <Route path="/ml-models/*" element={<ML active={active}/>}/>
        <Route path="/ai-analyst" element={<Analyst active={active}/>}/>
        <Route path="/insights" element={<Insights active={active}/>}/>
        <Route path="/settings" element={<Settings/>}/>
        <Route path="*" element={<Overview active={active}/>}/>
      </Routes>
    </div>
  </div>;
}

function Empty({
  text="Upload a dataset to unlock live analytics."
}:{
  text?:string
}){
  return <div className="empty">
    <div className="empty-icon">↗</div>
    <b>No active dataset</b>
    <span>{text}</span>
    <NavLink to="/datasets" className="button">Upload CSV</NavLink>
  </div>;
}

function Header({
  title,
  sub,
  children
}:{
  title:string,
  sub:string,
  children?:any
}){
  return <div className="page-head">
    <div>
      <div className="eyebrow">INSIGHTFLOW</div>
      <h1>{title}</h1>
      <p>{sub}</p>
    </div>
    {children}
  </div>;
}

function Card({
  title,
  children,
  wide=false
}:{
  title:string,
  children:any,
  wide?:boolean
}){
  return <section className={wide?"card wide":"card"}>
    <div className="card-head">
      <h3>{title}</h3>
    </div>
    {children}
  </section>;
}

function Overview({active}:{active?:number}){
  const [d,setD]=useState<any>();
  const [t,setT]=useState<any[]>([]);
  const [c,setC]=useState<any[]>([]);

  useEffect(()=>{
    if(active){
      A.overview(active).then(r=>setD(r.data));
      A.trend(active).then(r=>setT(r.data));
      A.category(active).then(r=>setC(r.data.slice(0,6)));
    }
  },[active]);

  if(!active)
    return <main className="content">
      <Header
        title="Good evening"
        sub="Here's an overview of your business data."
      />
      <Empty/>
    </main>;

  return <main className="content">
    <Header
      title="Good evening"
      sub="Here's an overview of your business data."
    />

    <div className="kpis">
      {[
        [
          "Total Revenue",
          `$${(d?.total_revenue||0).toLocaleString()}`,
          "Revenue across the active dataset"
        ],
        [
          "Total Orders",
          (d?.total_orders||0).toLocaleString(),
          "Distinct orders"
        ],
        [
          "Customers",
          (d?.total_customers||0).toLocaleString(),
          "Unique customers"
        ],
        [
          "Average Order Value",
          `$${(d?.average_order_value||0).toLocaleString()}`,
          "Revenue per order"
        ]
      ].map(x=>
        <div className="kpi" key={x[0]}>
          <span>{x[0]}</span>
          <strong>{x[1]}</strong>
          <small>{x[2]}</small>
        </div>
      )}
    </div>

    <div className="grid-2">
      <Card title="Revenue Overview">
        <div className="chart">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={t}>
              <XAxis dataKey="date"/>
              <YAxis/>
              <Tooltip/>
              <Area
                type="monotone"
                dataKey="revenue"
                fill="#4f46e5"
                fillOpacity={.12}
                stroke="#4f46e5"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="Revenue by Category">
        <div className="chart">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={c}>
              <XAxis dataKey="name"/>
              <YAxis/>
              <Tooltip/>
              <Bar dataKey="revenue" fill="#4f46e5"/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  </main>;
}

function Datasets({
  setActive,
  datasets,
  setDatasets
}:{
  setActive:any,
  datasets:any[],
  setDatasets:any
}){
  const [busy,setBusy]=useState(false);

  async function onFile(e:any){
    const f=e.target.files?.[0];

    if(!f)return;

    setBusy(true);

    try{
      const r=await A.upload(f);
      setDatasets((x:any[])=>[r.data,...x]);
      setActive(r.data.id);
    }catch(err:any){
      alert(err?.response?.data?.detail||"Upload failed");
    }finally{
      setBusy(false);
    }
  }

  return <main className="content">
    <Header
      title="Datasets"
      sub="Upload, validate and process your business data."
    />

    <div className="upload card">
      <div className="upload-icon">↑</div>

      <h2>
        {busy?"Processing dataset...":"Upload a CSV dataset"}
      </h2>

      <p>
        Canonical fields: order_id, order_date, customer_id,
        product_id, product_name, category, region, quantity,
        unit_price, revenue.
      </p>

      <label className="button">
        {busy?"Processing...":"Choose CSV file"}
        <input
          type="file"
          accept=".csv"
          onChange={onFile}
          hidden
          disabled={busy}
        />
      </label>
    </div>

    <Card title="Dataset history">
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th>Status</th>
              <th>Rows</th>
              <th>Quality</th>
              <th>Created</th>
            </tr>
          </thead>

          <tbody>
            {datasets.map(x=>
              <tr key={x.id}>
                <td>{x.filename}</td>
                <td>
                  <span className={"badge "+x.status}>
                    {x.status}
                  </span>
                </td>
                <td>{x.row_count}</td>
                <td>{x.quality_score}%</td>
                <td>{new Date(x.created_at).toLocaleString()}</td>
              </tr>
            )}
          </tbody>
        </table>

        {!datasets.length &&
          <div className="muted">No datasets yet.</div>
        }
      </div>
    </Card>
  </main>;
}

function Analytics({active}:{active?:number}){
  const [d,setD]=useState<any>();
  const [t,setT]=useState<any[]>([]);
  const [r,setR]=useState<any[]>([]);
  const [p,setP]=useState<any[]>([]);

  useEffect(()=>{
    if(active){
      A.overview(active).then(x=>setD(x.data));
      A.trend(active).then(x=>setT(x.data));
      A.region(active).then(x=>setR(x.data.slice(0,8)));
      A.products(active).then(x=>setP(x.data));
    }
  },[active]);

  if(!active)
    return <main className="content">
      <Header
        title="Analytics"
        sub="Explore business performance with database-backed metrics."
      />
      <Empty/>
    </main>;

  return <main className="content">
    <Header
      title="Analytics"
      sub="Explore performance by time, region and product."
    />

    <div className="kpis">
      {Object.entries(d||{}).map(([k,v]:any)=>
        <div className="kpi" key={k}>
          <span>{k.replaceAll("_"," ")}</span>
          <strong>
            {typeof v==="number"?v.toLocaleString():v}
          </strong>
        </div>
      )}
    </div>

    <div className="grid-2">
      <Card title="Revenue Trend">
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={t}>
            <XAxis dataKey="date"/>
            <YAxis/>
            <Tooltip/>
            <Area
              type="monotone"
              dataKey="revenue"
              fill="#4f46e5"
              fillOpacity={.12}
              stroke="#4f46e5"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      <Card title="Revenue by Region">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={r}>
            <XAxis dataKey="name"/>
            <YAxis/>
            <Tooltip/>
            <Bar dataKey="revenue" fill="#0f766e"/>
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>

    <Card title="Top Products">
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Revenue</th>
            <th>Quantity</th>
          </tr>
        </thead>

        <tbody>
          {p.map(x=>
            <tr key={x.name}>
              <td>{x.name}</td>
              <td>${x.revenue.toLocaleString()}</td>
              <td>{x.quantity}</td>
            </tr>
          )}
        </tbody>
      </table>
    </Card>
  </main>;
}

function Quality({active}:{active?:number}){
  const [d,setD]=useState<any>();

  useEffect(()=>{
    if(active)
      A.api
        .get(`/datasets/${active}/quality`)
        .then(x=>setD(x.data));
  },[active]);

  if(!active)
    return <main className="content">
      <Header
        title="Data Quality"
        sub="Validation and ETL quality monitoring."
      />
      <Empty/>
    </main>;

  return <main className="content">
    <Header
      title="Data Quality"
      sub="Inspect validation results from the ETL pipeline."
    />

    <div className="quality-score">
      {d?.dataset?.quality_score||0}
      <span>/100 quality score</span>
    </div>

    <Card title="Checks">
      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Field</th>
            <th>Rows</th>
            <th>Severity</th>
            <th>Message</th>
          </tr>
        </thead>

        <tbody>
          {(d?.checks||[]).map((x:any,i:number)=>
            <tr key={i}>
              <td>{x.check_type}</td>
              <td>{x.field}</td>
              <td>{x.affected_rows}</td>
              <td>{x.severity}</td>
              <td>{x.message}</td>
            </tr>
          )}
        </tbody>
      </table>
    </Card>
  </main>;
}

function ML({active}:{active?:number}){
  const [path,setPath]=useState(location.pathname);
  const [data,setData]=useState<any>();

  useEffect(()=>{
    setPath(location.pathname);
  },[location.pathname]);

  if(!active)
    return <main className="content">
      <Header
        title="ML Models"
        sub="Forecast, segment and detect anomalies."
      />
      <Empty/>
    </main>;

  /*
   * After the check above, TypeScript knows that active is a number.
   * Store the narrowed value in a constant and use it for API calls.
   */
  const datasetId=active;

  async function run(){
    try{
      if(path.includes("segments")){
        setData((await A.segments(datasetId)).data);
      }else if(path.includes("anomalies")){
        setData((await A.anomalies(datasetId)).data);
      }else{
        setData((await A.forecast(datasetId)).data);
      }
    }catch(e:any){
      setData({
        error:e?.response?.data?.detail||"Model failed"
      });
    }
  }

  return <main className="content">
    <Header
      title={
        path.includes("segments")
          ?"Customer Segmentation"
          :path.includes("anomalies")
            ?"Anomaly Detection"
            :"Sales Forecast"
      }
      sub="Run a model against the active dataset."
    />

    <div className="tabs">
      <NavLink to="/ml-models/forecast">Forecast</NavLink>
      <NavLink to="/ml-models/segments">Segments</NavLink>
      <NavLink to="/ml-models/anomalies">Anomalies</NavLink>
    </div>

    <Card title="Model run">
      <button className="button" onClick={run}>
        Run model
      </button>

      {data?.error&&
        <p className="error">{data.error}</p>
      }

      {data?.segments&&
        <div className="mini-grid">
          {data.segments.map((x:any)=>
            <div className="mini-card" key={x.segment}>
              <b>{x.segment}</b>
              <strong>{x.customers}</strong>
              <span>
                customers · avg value $
                {x.avg_monetary.toLocaleString()}
              </span>
            </div>
          )}
        </div>
      }

      {data?.count!==undefined&&
        <div className="quality-score small">
          {data.count}
          <span> anomalies detected</span>
        </div>
      }

      {data?.forecast&&
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={data.forecast}>
            <XAxis dataKey="date"/>
            <YAxis/>
            <Tooltip/>
            <Area
              type="monotone"
              dataKey="predicted_revenue"
              fill="#4f46e5"
              fillOpacity={.12}
              stroke="#4f46e5"
            />
          </AreaChart>
        </ResponsiveContainer>
      }
    </Card>
  </main>;
}

function Analyst({active}:{active?:number}){
  const [q,setQ]=useState("");
  const [a,setA]=useState<any[]>([]);

  async function ask(){
    if(!active||!q)return;

    try{
      const r=await A.ask(active,q);

      setA(x=>[
        ...x,
        {
          q,
          a:r.data
        }
      ]);

      setQ("");
    }catch(e:any){
      alert(
        e?.response?.data?.detail||
        "Unable to answer"
      );
    }
  }

  return <main className="content">
    <Header
      title="AI Business Analyst"
      sub="Ask supported questions grounded in your actual dataset."
    />

    <Card title="Ask your data anything">
      <div className="suggestions">
        {[
          "Which category generated the most revenue?",
          "Which region has the highest sales?",
          "What are the top products?",
          "Which customers are most valuable?",
          "What is the revenue trend?",
          "How many orders were processed?"
        ].map(x=>
          <button
            key={x}
            onClick={()=>setQ(x)}
          >
            {x}
          </button>
        )}
      </div>

      <div className="ask">
        <input
          value={q}
          onChange={e=>setQ(e.target.value)}
          onKeyDown={e=>e.key==="Enter"&&ask()}
          placeholder="Ask your data anything..."
        />

        <button className="button" onClick={ask}>
          Ask
        </button>
      </div>

      {a.map((x,i)=>
        <div className="answer" key={i}>
          <small>{x.q}</small>
          <p>{x.a.answer}</p>

          {Object.entries(x.a.metrics||{}).map(([k,v])=>
            <span className="metric" key={k}>
              {k}: {String(v)}
            </span>
          )}
        </div>
      )}
    </Card>
  </main>;
}

function Insights({active}:{active?:number}){
  return <main className="content">
    <Header
      title="Insights"
      sub="Business observations generated from real metrics."
    />

    <Card title="Insight engine">
      <p>
        Run analytics and ML models to populate evidence-backed
        business observations. InsightFlow deliberately avoids
        invented numbers.
      </p>

      {active?
        <div className="insight-list">
          <div>
            <b>Dataset connected</b>
            <span>
              Insights are grounded in the active
              PostgreSQL/SQLite-backed dataset.
            </span>
          </div>

          <div>
            <b>ML available</b>
            <span>
              Forecasting, segmentation and anomaly detection
              can be run from the ML Models section.
            </span>
          </div>
        </div>
        :
        <Empty/>
      }
    </Card>
  </main>;
}

function Settings(){
  return <main className="content">
    <Header
      title="Settings"
      sub="Application and dataset configuration."
    />

    <Card title="InsightFlow">
      <div className="settings">
        <b>Version</b>
        <span>1.0.0 MVP</span>

        <b>Analytics principle</b>
        <span>
          All displayed business metrics are database-backed.
        </span>

        <b>AI Analyst</b>
        <span>
          Deterministic grounded intents in the MVP;
          external LLM integration can be added later.
        </span>
      </div>
    </Card>
  </main>;
}

export default function App(){
  return <Layout/>;
}