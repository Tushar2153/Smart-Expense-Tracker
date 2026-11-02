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


def api_put(path, payload):
    try:
        response = requests.put(
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=10,
        )
        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            return None, f"API returned {response.status_code}: {detail}"
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def api_delete(path, params=None):
    try:
        response = requests.delete(
            f"{API_BASE_URL}{path}",
            params=params,
            timeout=10,
        )
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
    page = st.radio(
    "WORKSPACE",
    [
        "Overview",
        "Transactions",
        "Add expense",
        "AI categorizer",
        "Budgets",
    ],
)
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
    st.caption(
        f"Updated {date.today().strftime('%d %b %Y')} "
        "· Based on saved transactions"
    )

    # Reporting period
    today = date.today()
    month_start = today.replace(day=1)

    st.markdown("#### Reporting period")
    selected_dates = st.date_input(
        "Choose date range",
        value=(month_start, today),
        max_value=today,
        key="overview_date_range",
    )

    # Streamlit may return a single date until both dates are selected.
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = selected_dates[0] if isinstance(
            selected_dates, (tuple, list)
        ) else selected_dates
        end_date = start_date

    if start_date > end_date:
        st.error("Start date must be on or before end date.")
        st.stop()

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1)

    if not df.empty and "amount" in df.columns:
        # Prepare a clean working copy without modifying the original data.
        data = df.copy()
        data["amount"] = pd.to_numeric(
            data["amount"], errors="coerce"
        ).fillna(0)

        if "transaction_date" in data.columns:
            data["transaction_date"] = pd.to_datetime(
                data["transaction_date"], errors="coerce"
            )
            valid_dates = data["transaction_date"].notna()

            # Selected period; end date is inclusive.
            period_df = data[
                valid_dates
                & (data["transaction_date"] >= start_ts)
                & (data["transaction_date"] < end_ts)
            ].copy()

            # Compare with the immediately preceding period of equal length.
            period_days = (end_ts - start_ts).days
            previous_start = start_ts - pd.Timedelta(days=period_days)

            previous_df = data[
                valid_dates
                & (data["transaction_date"] >= previous_start)
                & (data["transaction_date"] < start_ts)
            ].copy()
        else:
            period_df = data.iloc[0:0].copy()
            previous_df = data.iloc[0:0].copy()
    else:
        data = pd.DataFrame()
        period_df = pd.DataFrame()
        previous_df = pd.DataFrame()

    period_total = float(period_df["amount"].sum()) if not period_df.empty else 0.0
    previous_total = float(previous_df["amount"].sum()) if not previous_df.empty else 0.0
    all_time_total = float(data["amount"].sum()) if not data.empty else 0.0

    # Handle installations/data that don't yet contain the review field.
    if not period_df.empty and "review_required" in period_df.columns:
        review_count = int(
            (pd.to_numeric(
                period_df["review_required"], errors="coerce"
            ).fillna(0) == 1).sum()
        )
    else:
        review_count = 0

    # Spending comparison
    if previous_total > 0:
        change_pct = (
            (period_total - previous_total) / previous_total
        ) * 100
        spending_delta = f"{change_pct:+.1f}% vs previous period"
        delta_color = "inverse"
    elif period_total > 0:
        spending_delta = "No previous-period baseline"
        delta_color = "off"
    else:
        spending_delta = None
        delta_color = "off"

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Selected-period spending",
        money(period_total),
        delta=spending_delta,
        delta_color=delta_color,
        help="Compared with the immediately preceding period of equal length.",
    )
    c2.metric(
        "All-time tracked",
        money(all_time_total),
        help="Sum of all saved transaction amounts.",
    )
    c3.metric(
        "Transactions in period",
        f"{len(period_df):,}",
    )
    c4.metric(
        "Needs review",
        f"{review_count:,}",
        delta="Check categories" if review_count else "None flagged",
        delta_color="off",
    )

    st.write("")

    # Charts use the selected reporting period.
    left, right = st.columns([1.35, 1])

    with left:
        st.markdown("#### Spending over time")

        if (
            not period_df.empty
            and "transaction_date" in period_df.columns
        ):
            trend = period_df.dropna(
                subset=["transaction_date"]
            ).copy()

            trend["day"] = trend["transaction_date"].dt.date

            daily = (
                trend.groupby("day", as_index=False)["amount"]
                .sum()
                .sort_values("day")
            )

            fig = px.area(
                daily,
                x="day",
                y="amount",
                markers=True,
                labels={
                    "day": "Date",
                    "amount": "Amount (₹)",
                },
            )
            fig.update_traces(
                line_color="#8b9cff",
                fillcolor="rgba(124,156,255,.16)",
                line_width=3,
                marker=dict(size=5),
                hovertemplate="%{x|%d %b %Y}<br>₹%{y:,.2f}<extra></extra>",
            )
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Amount (₹)",
                hovermode="x unified",
            )
            st.plotly_chart(
                theme(fig),
                use_container_width=True,
                key="overview_spending_trend",
            )
        else:
            st.info(
                "No transactions in this period. "
                "Choose another date range or add a transaction."
            )

    with right:
        st.markdown("#### Where it goes")

        if (
            not period_df.empty
            and "category" in period_df.columns
        ):
            cats = period_df.copy()
            cats["category"] = (
                cats["category"]
                .fillna("Uncategorized")
                .replace("", "Uncategorized")
            )

            cats = (
                cats.groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            # Avoid drawing a misleading pie if there is no positive spend.
            cats = cats[cats["amount"] > 0]

            if not cats.empty:
                fig = px.pie(
                    cats,
                    names="category",
                    values="amount",
                    hole=0.68,
                    labels={
                        "category": "Category",
                        "amount": "Amount (₹)",
                    },
                )
                fig.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    marker=dict(
                        line=dict(color="#111a2b", width=2)
                    ),
                    hovertemplate=(
                        "%{label}<br>₹%{value:,.2f}"
                        "<br>%{percent}<extra></extra>"
                    ),
                )
                fig.update_layout(
                    showlegend=True,
                    legend_title_text="",
                    annotations=[
                        dict(
                            text=money(float(cats["amount"].sum())),
                            x=0.5,
                            y=0.5,
                            font_size=18,
                            font_color="#f4f6ff",
                            showarrow=False,
                        )
                    ],
                )
                st.plotly_chart(
                    theme(fig),
                    use_container_width=True,
                    key="overview_category_breakdown",
                )
            else:
                st.info(
                    "No positive transaction amounts to display "
                    "in the category chart."
                )
        else:
            st.info(
                "Your category breakdown will appear "
                "when transactions are available."
            )

    # Recent activity for the selected period
    st.markdown("#### Latest activity")

    if not period_df.empty:
        latest = period_df.copy()

        sort_cols = [
            col for col in ["transaction_date", "id"]
            if col in latest.columns
        ]
        if sort_cols:
            latest = latest.sort_values(
                sort_cols,
                ascending=[False] * len(sort_cols),
            )

        latest = latest.head(6).copy()

        latest = latest.rename(
            columns={
                "transaction_date": "Date",
                "description": "Description",
                "category": "Category",
                "amount": "Amount (₹)",
                "review_required": "Review",
            }
        )

        display_cols = [
            col for col in [
                "Date", "Description", "Category",
                "Amount (₹)", "Review"
            ]
            if col in latest.columns
        ]
        latest = latest[display_cols]

        if "Date" in latest.columns:
            latest["Date"] = pd.to_datetime(
                latest["Date"], errors="coerce"
            ).dt.strftime("%d %b %Y")

        if "Amount (₹)" in latest.columns:
            latest["Amount (₹)"] = latest["Amount (₹)"].map(
                lambda value: f"{value:,.2f}"
            )

        if "Review" in latest.columns:
            latest["Review"] = latest["Review"].map(
                {1: "Review", 0: "OK", 1.0: "Review", 0.0: "OK"}
            ).fillna("—")

        st.dataframe(
            latest,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No transactions found for the selected period.")

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

elif page == "Budgets":
    st.markdown("### Monthly budgets")
    st.caption(
        "Set spending limits and track your saved transactions "
        "against each budget."
    )

    # Choose the month being managed.
    selected_month_date = st.date_input(
        "Budget month",
        value=date.today().replace(day=1),
        key="budget_month",
    )
    selected_month = selected_month_date.strftime("%Y-%m")

    # Show category names already present in transaction history.
    if not df.empty and "category" in df.columns:
        existing_categories = sorted(
            category
            for category in df["category"].dropna().astype(str).unique()
            if category.strip() and category != "Overall"
        )
        if existing_categories:
            st.caption(
                "Existing transaction categories: "
                + ", ".join(existing_categories)
            )
    else:
        st.caption(
            "Add transactions first, or enter a category name manually."
        )

    st.markdown("---")
    st.markdown("#### Create or update a budget")

    budget_tab_overall, budget_tab_category = st.tabs(
        ["Overall monthly limit", "Category limit"]
    )

    with budget_tab_overall:
        st.write(
            "Set one spending limit for all transactions in the selected month."
        )
        with st.form("overall_budget_form"):
            overall_amount = st.number_input(
                "Monthly budget (₹)",
                min_value=1.0,
                value=15000.0,
                step=500.0,
                key="overall_budget_amount",
            )
            save_overall = st.form_submit_button(
                "Save overall budget",
                type="primary",
                use_container_width=True,
            )

        if save_overall:
            result, error = api_put(
                "/budgets",
                {
                    "month": selected_month,
                    "category": "Overall",
                    "amount": overall_amount,
                },
            )
            if error:
                st.error(f"Couldn't save budget: {error}")
            else:
                st.success(
                    f"Overall budget saved for {selected_month}."
                )
                st.rerun()

    with budget_tab_category:
        st.write(
            "Use the exact category name assigned to your transactions."
        )
        with st.form("category_budget_form"):
            category_name = st.text_input(
                "Category name",
                placeholder="e.g. Food",
                help=(
                    "Category names must match saved transaction "
                    "categories exactly."
                ),
            )
            category_amount = st.number_input(
                "Category budget (₹)",
                min_value=1.0,
                value=4000.0,
                step=250.0,
                key="category_budget_amount",
            )
            save_category = st.form_submit_button(
                "Save category budget",
                type="primary",
                use_container_width=True,
            )

        if save_category:
            clean_category = category_name.strip()
            if not clean_category:
                st.error("Enter a category name.")
            elif clean_category.casefold() == "overall":
                st.error(
                    "'Overall' is reserved for the monthly total budget."
                )
            else:
                result, error = api_put(
                    "/budgets",
                    {
                        "month": selected_month,
                        "category": clean_category,
                        "amount": category_amount,
                    },
                )
                if error:
                    st.error(f"Couldn't save budget: {error}")
                else:
                    st.success(
                        f"Budget saved for {clean_category}."
                    )
                    st.rerun()

    st.markdown("---")
    st.markdown("#### Budget status")
    st.caption(f"Showing saved budgets for {selected_month}.")

    budget_result, budget_error = api_get(
        "/budgets",
        params={"month": selected_month},
    )

    if budget_error:
        st.error(f"Couldn't load budgets: {budget_error}")
    else:
        budgets = budget_result.get("budgets", [])

        if not budgets:
            st.info(
                "No budgets saved for this month yet. "
                "Create an overall or category budget above."
            )
        else:
            overall_budget = next(
                (
                    item for item in budgets
                    if item.get("category") == "Overall"
                ),
                None,
            )
            category_budgets = [
                item for item in budgets
                if item.get("category") != "Overall"
            ]

            if overall_budget:
                st.markdown("##### Overall spending")

                spent = float(overall_budget.get("spent", 0))
                limit = float(overall_budget.get("budget", 0))
                remaining = float(
                    overall_budget.get("remaining", 0)
                )
                percent = float(
                    overall_budget.get("percent_used", 0)
                )

                m1, m2, m3 = st.columns(3)
                m1.metric("Spent", money(spent))
                m2.metric("Budget limit", money(limit))
                m3.metric("Remaining", money(remaining))

                st.progress(
                    min(max(percent / 100, 0.0), 1.0)
                )
                st.caption(f"{percent:.1f}% of the budget used")

                if spent > limit:
                    st.error(
                        f"Over budget by {money(spent - limit)}."
                    )
                elif percent >= 80:
                    st.warning(
                        "You've used at least 80% of your monthly budget."
                    )
                else:
                    st.success("You're within your overall budget.")

            if category_budgets:
                st.markdown("##### Category spending")

                for index, item in enumerate(category_budgets):
                    category = item["category"]
                    spent = float(item.get("spent", 0))
                    limit = float(item.get("budget", 0))
                    remaining = float(item.get("remaining", 0))
                    percent = float(item.get("percent_used", 0))

                    with st.container(border=True):
                        st.markdown(f"**{category}**")

                        a, b, c = st.columns(3)
                        a.metric("Spent", money(spent))
                        b.metric("Limit", money(limit))
                        c.metric("Remaining", money(remaining))

                        st.progress(
                            min(max(percent / 100, 0.0), 1.0)
                        )
                        st.caption(
                            f"{percent:.1f}% of category budget used"
                        )

                        if spent > limit:
                            st.error(
                                f"{category} is over budget by "
                                f"{money(spent - limit)}."
                            )
                        elif percent >= 80:
                            st.warning(
                                f"{category} has reached at least "
                                "80% of its budget."
                            )

            st.markdown("---")
            st.markdown("#### Remove a budget")

            budget_options = [
                (item["category"], item)
                for item in budgets
            ]

            selected_budget_category = st.selectbox(
                "Choose a budget to remove",
                options=[item[0] for item in budget_options],
                key="delete_budget_category",
            )

            if st.button(
                "Delete selected budget",
                type="secondary",
            ):
                _, error = api_delete(
                    "/budgets",
                    params={
                        "month": selected_month,
                        "category": selected_budget_category,
                    },
                )
                if error:
                    st.error(f"Couldn't delete budget: {error}")
                else:
                    st.success(
                        f"Deleted the {selected_budget_category} budget."
                    )
                    st.rerun()

st.markdown("---")
st.caption("Finora is a local prototype. Verify AI-generated categories and keep your transaction data secure.")
