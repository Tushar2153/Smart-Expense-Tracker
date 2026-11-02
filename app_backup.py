import os
from datetime import date

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(
    page_title="Finora | Smart Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("EXPENSE_API_URL", "http://127.0.0.1:8000").rstrip("/")



st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
      :root { --ink:#e8edf7; --muted:#91a0b8; --panel:#111a2b; --line:rgba(157,177,210,.15); }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
      .stApp { background:radial-gradient(ellipse at 15% 0%,rgba(74,101,180,.17),transparent 34%),#0a1020; color:var(--ink); }
      [data-testid="stHeader"] { background:rgba(10,16,32,.72); }
      [data-testid="stSidebar"] { background:#0d1526; border-right:1px solid var(--line); }
      .block-container { padding-top:1.8rem; padding-bottom:3rem; max-width:1500px; }
      h1,h2,h3 { font-family:'Manrope',sans-serif!important; letter-spacing:-.035em; }
      [data-testid="stMetric"] { background:linear-gradient(145deg,rgba(21,31,51,.96),rgba(15,24,42,.96)); border:1px solid var(--line); padding:19px 20px; border-radius:18px; }
      [data-testid="stMetricLabel"] { color:#aab6cc!important; font-size:.88rem; }
      [data-testid="stMetricValue"] { color:#f2f5fc!important; font-family:'Manrope',sans-serif; }
      div[data-testid="stForm"] { background:rgba(17,26,43,.72); border:1px solid var(--line); border-radius:18px; padding:22px; }
      div.stButton>button,div.stFormSubmitButton>button { border-radius:10px; border:1px solid rgba(124,156,255,.4); font-weight:700; min-height:2.7rem; transition:.18s ease; }
      div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"] { background:linear-gradient(100deg,#6d8cff,#8c7cf7); color:white; border:0; }
      div.stButton>button:hover,div.stFormSubmitButton>button:hover { transform:translateY(-1px); border-color:#a9baff; }
      div[data-baseweb="input"]>div,div[data-baseweb="select"]>div,[data-testid="stDateInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input { background:#0e1728!important; border-color:var(--line)!important; border-radius:10px!important; }
      .brand { display:flex; align-items:center; gap:11px; margin:0 0 24px; }
      .brand-icon { display:flex; align-items:center; justify-content:center; width:42px; height:42px; border-radius:14px; background:linear-gradient(135deg,#7c9cff,#9b85ff); color:white; font-size:22px; }
      .brand-name { font-family:'Manrope',sans-serif; font-size:1.2rem; font-weight:800; color:#f3f6ff; line-height:1.1; }
      .brand-sub { color:#8998b3; font-size:.72rem; margin-top:4px; }
      .eyebrow { color:#9eafff; text-transform:uppercase; letter-spacing:.15em; font-size:.72rem; font-weight:700; }
      .hero-title { font-family:'Manrope',sans-serif; font-size:2.2rem; font-weight:800; letter-spacing:-.055em; line-height:1.13; margin:.35rem 0 .55rem; color:#f4f6ff; }
      .hero-copy { color:#9aa9c2; font-size:1rem; max-width:720px; }
      .surface { background:linear-gradient(145deg,rgba(21,31,51,.96),rgba(15,24,42,.96)); border:1px solid var(--line); border-radius:18px; padding:20px 22px; }
      .muted { color:#93a2bb; font-size:.88rem; }
      .pill { display:inline-block; border:1px solid rgba(124,156,255,.3); color:#c6d1ff; background:rgba(124,156,255,.10); border-radius:999px; padding:5px 10px; font-size:.75rem; font-weight:700; }
      .stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:1px solid var(--line); }
      .stTabs [data-baseweb="tab"] { border-radius:10px 10px 0 0; padding:10px 16px; color:#9ba9c0; }
      [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
      hr { border-color:var(--line); } footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=5)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def api_post(path, payload):
    try:
        response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=10)
        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            return None, f"API returned {response.status_code}: {detail}"
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def get_transactions():
    result, error = api_get("/transactions", params={"limit": 500})
    if error:
        return pd.DataFrame(), error
    rows = result.get("transactions", []) if isinstance(result, dict) else result
    df = pd.DataFrame(rows)
    if not df.empty:
        for col in ["amount", "confidence", "review_required"]:
            if col in df:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "transaction_date" in df:
            df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    return df, None


def money(value):
    return f"₹{float(value):,.2f}"


def theme(fig):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans", color="#aab6cc"),
        margin=dict(l=8, r=8, t=35, b=8),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(157,177,210,.10)", zeroline=False)
    return fig


with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-icon">↗</div><div><div class="brand-name">finora</div><div class="brand-sub">SMART EXPENSE TRACKER</div></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio("WORKSPACE", ["Overview", "Transactions", "Add expense", "AI categorizer"])
    st.markdown("---")
    st.markdown("**API connection**")
    health, health_error = api_get("/health")
    if health_error:
        st.error("Backend offline")
        st.caption("Run `python -m uvicorn main:app --reload` in another terminal.")
    else:
        st.success("Backend connected")
        st.caption(API_BASE_URL)
    st.markdown("---")
    st.caption("Finora · Personal finance workspace")
    st.caption("AI category suggestions may be incorrect. Review uncertain results.")

st.markdown('<div class="eyebrow">YOUR MONEY, IN FOCUS</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Good decisions start<br>with a clearer picture.</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">Track spending, understand where your money goes, and let AI help organize your transactions.</div>', unsafe_allow_html=True)
st.write("")

df, load_error = get_transactions()
if load_error:
    st.warning(f"Couldn't load transactions from FastAPI. Start the backend and refresh. Details: {load_error}")
    df = pd.DataFrame()

if page == "Overview":
    st.markdown("### Financial overview")
    st.caption(f"Updated {date.today().strftime('%d %b %Y')} · Based on saved transactions")
    if not df.empty:
        today = pd.Timestamp(date.today())
        month_start = today.replace(day=1)
        valid = df["transaction_date"].notna()
        month_df = df[valid & (df["transaction_date"] >= month_start) & (df["transaction_date"] <= today)]
        total = float(df["amount"].fillna(0).sum())
        month_total = float(month_df["amount"].fillna(0).sum())
        count = len(df)
        review_count = int((df["review_required"].fillna(0) == 1).sum())
    else:
        total = month_total = 0
        count = review_count = 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total tracked", money(total))
    c2.metric("This month", money(month_total))
    c3.metric("Transactions", f"{count:,}")
    c4.metric("Needs review", f"{review_count:,}", delta="Check categories" if review_count else "All clear", delta_color="off")

    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("#### Spending over time")
        if not df.empty and df["transaction_date"].notna().any():
            trend = df.dropna(subset=["transaction_date"]).copy()
            trend["day"] = trend["transaction_date"].dt.date
            daily = trend.groupby("day", as_index=False)["amount"].sum().sort_values("day")
            fig = px.area(daily, x="day", y="amount")
            fig.update_traces(line_color="#8b9cff", fillcolor="rgba(124,156,255,.16)", line_width=3)
            fig.update_layout(xaxis_title="", yaxis_title="Amount (₹)", hovermode="x unified")
            st.plotly_chart(theme(fig), use_container_width=True)
        else:
            st.info("Add a few expenses to see your spending trend.")
    with right:
        st.markdown("#### Where it goes")
        if not df.empty and "category" in df:
            cats = df.groupby("category", dropna=False)["amount"].sum().reset_index()
            cats["category"] = cats["category"].fillna("Uncategorized")
            fig = px.pie(cats, names="category", values="amount", hole=.68)
            fig.update_traces(textposition="inside", textinfo="percent", marker=dict(line=dict(color="#111a2b", width=2)))
            fig.update_layout(showlegend=True, legend_title_text="", annotations=[dict(text=money(total), x=.5, y=.5, font_size=18, font_color="#f4f6ff", showarrow=False)])
            st.plotly_chart(theme(fig), use_container_width=True)
        else:
            st.info("Your category breakdown appears after your first transaction.")

    st.markdown("#### Latest activity")
    if not df.empty:
        latest = df.sort_values(["transaction_date", "id"], ascending=False).head(6).copy()
        latest = latest.rename(columns={"transaction_date":"Date","description":"Description","category":"Category","amount":"Amount (₹)","review_required":"Review"})
        cols = [c for c in ["Date","Description","Category","Amount (₹)","Review"] if c in latest]
        latest = latest[cols]
        if "Date" in latest:
            latest["Date"] = pd.to_datetime(latest["Date"], errors="coerce").dt.strftime("%d %b %Y")
        if "Amount (₹)" in latest:
            latest["Amount (₹)"] = latest["Amount (₹)"].map(lambda x: f"{x:,.2f}")
        if "Review" in latest:
            latest["Review"] = latest["Review"].map({1:"Review",0:"OK"}).fillna("—")
        st.dataframe(latest, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Choose **Add expense** in the sidebar to get started.")

elif page == "Transactions":
    st.markdown("### Transaction history")
    st.caption("Search, filter, and explore transactions saved in your database.")
    if df.empty:
        st.info("No transactions yet. Add your first expense from the sidebar.")
    else:
        f1, f2, f3 = st.columns([1.4, 1, 1])
        with f1:
            search = st.text_input("Search descriptions", placeholder="Netflix, Jio, groceries…")
        categories = sorted(df["category"].dropna().astype(str).unique())
        with f2:
            chosen = st.multiselect("Category", categories, default=categories)
        with f3:
            status = st.selectbox("Review status", ["All", "Needs review", "No review needed"])
        filtered = df.copy()
        if search:
            filtered = filtered[filtered["description"].astype(str).str.contains(search, case=False, na=False)]
        filtered = filtered[filtered["category"].astype(str).isin(chosen)] if chosen else filtered.iloc[0:0]
        if status == "Needs review":
            filtered = filtered[filtered["review_required"] == 1]
        elif status == "No review needed":
            filtered = filtered[filtered["review_required"] == 0]
        st.markdown(f'<span class="pill">{len(filtered)} matching transactions</span>', unsafe_allow_html=True)
        display = filtered.rename(columns={"transaction_date":"Date","description":"Description","category":"Category","amount":"Amount (₹)","confidence":"Model score","review_required":"Review","id":"ID"})
        display = display[[c for c in ["Date","Description","Category","Amount (₹)","Model score","Review","ID"] if c in display]].copy()
        if "Date" in display:
            display["Date"] = pd.to_datetime(display["Date"], errors="coerce").dt.strftime("%d %b %Y")
        if "Amount (₹)" in display:
            display["Amount (₹)"] = display["Amount (₹)"].map(lambda x: f"{x:,.2f}")
        if "Model score" in display:
            display["Model score"] = display["Model score"].map(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
        if "Review" in display:
            display["Review"] = display["Review"].map({1:"Review",0:"OK"}).fillna("—")
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), "finora_transactions.csv", "text/csv", type="primary")

elif page == "Add expense":
    st.markdown("### Add a transaction")
    st.caption("The API predicts a category and saves the transaction.")
    with st.form("add_expense_form", clear_on_submit=True):
        description = st.text_input("Merchant or description", placeholder="e.g. Netflix monthly subscription")
        c1, c2 = st.columns(2)
        with c1:
            amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=50.0, format="%.2f")
        with c2:
            tx_date = st.date_input("Transaction date", value=date.today(), max_value=date.today())
        submitted = st.form_submit_button("Save transaction", type="primary", use_container_width=True)
    if submitted:
        if not description.strip():
            st.error("Please enter a description.")
        elif amount <= 0:
            st.error("Enter an amount greater than ₹0.")
        else:
            result, error = api_post("/transactions", {"description":description.strip(),"amount":amount,"transaction_date":tx_date.isoformat()})
            if error:
                st.error(f"Couldn't save transaction: {error}")
            else:
                st.success(f"Saved transaction #{result.get('id', '')}.")
                st.markdown(
                    f'<div class="surface"><div class="muted">AI CATEGORY SUGGESTION</div><div style="font-size:1.55rem;font-weight:800;margin:.3rem 0">{result.get("category","Unknown")}</div><span class="pill">Model score: {result.get("confidence",0)}%</span><p class="muted" style="margin-top:12px">{"Manual review recommended." if result.get("review_required") else "Check the suggested category if needed."}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Refresh dashboard"):
                    st.rerun()

elif page == "AI categorizer":
    st.markdown("### AI category assistant")
    st.caption("Preview a category suggestion before saving. Predictions are suggestions, not guarantees.")
    with st.form("predict_form"):
        description = st.text_input("Transaction description", placeholder="e.g. Blinkit grocery order")
        predict_clicked = st.form_submit_button("Predict category", type="primary", use_container_width=True)
    if predict_clicked:
        if not description.strip():
            st.error("Enter a description first.")
        else:
            prediction, error = api_post("/predict", {"description":description.strip()})
            if error:
                st.error(f"Prediction failed: {error}")
            else:
                st.session_state["last_prediction"] = prediction
                st.session_state["last_description"] = description.strip()
    prediction = st.session_state.get("last_prediction")
    if prediction and page == "AI categorizer":
        a, b = st.columns([1.3,1])
        with a:
            st.markdown('<div class="surface"><div class="muted">PREDICTED CATEGORY</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:Manrope;font-size:1.8rem;font-weight:800;margin:.35rem 0 1rem">{prediction["category"]}</div>', unsafe_allow_html=True)
            st.progress(min(max(float(prediction["confidence_percent"])/100,0),1))
            st.markdown(f'<div class="muted">Model score · {prediction["confidence_percent"]:.1f}%</div></div>', unsafe_allow_html=True)
        with b:
            if prediction["review_required"]:
                st.warning("Needs manual review")
                st.write("The score is below the current threshold. Confirm merchant and purchase details.")
            else:
                st.success("Suggestion available")
                st.write("The model can still be wrong, especially for short or ambiguous descriptions.")
        st.write("")
        with st.form("save_predicted_expense"):
            amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=50.0, format="%.2f", key="pred_amount")
            tx_date = st.date_input("Transaction date", value=date.today(), max_value=date.today(), key="pred_date")
            save_clicked = st.form_submit_button("Save transaction", type="primary")
        if save_clicked:
            if amount <= 0:
                st.error("Enter an amount greater than ₹0.")
            else:
                saved, save_error = api_post("/transactions", {"description":st.session_state["last_description"],"amount":amount,"transaction_date":tx_date.isoformat()})
                if save_error:
                    st.error(f"Couldn't save transaction: {save_error}")
                else:
                    st.success(f"Saved transaction #{saved.get('id', '')}. The backend generated the saved category.")

st.markdown("---")
st.caption("Finora is a local prototype. Verify AI-generated categories and keep your transaction data secure.")
