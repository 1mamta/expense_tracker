import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from database import (init_db, register_user, login_user, add_expense,
                      get_expenses, set_budget, get_budgets, delete_expense)
from model import predict_category

#  Page Config 
st.set_page_config(
    page_title="SpendSmart — Expense Tracker",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded"
)

#  Custom CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
* { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #0f1117; color: #e8eaf0; }
.metric-card {
    background: linear-gradient(135deg, #1a1d2e, #252840);
    border: 1px solid #2d3154;
    border-radius: 16px;
    padding: 20px 24px;
    margin: 8px 0;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #7c83fd; }
.metric-label { font-size: 0.85rem; color: #8b90b8; margin-top: 4px; }
.alert-danger {
    background: rgba(255, 75, 75, 0.15);
    border-left: 4px solid #ff4b4b;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
}
.alert-warning {
    background: rgba(255, 171, 0, 0.15);
    border-left: 4px solid #ffab00;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
}
.alert-success {
    background: rgba(0, 200, 150, 0.15);
    border-left: 4px solid #00c896;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 8px 0;
}
.category-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    background: #252840;
    color: #7c83fd;
    border: 1px solid #3a3f6e;
}
</style>
""", unsafe_allow_html=True)

CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Bills & Utilities",
    "Healthcare", "Entertainment", "Education", "Investments & Savings"
]

PAYMENT_MODES = ["UPI", "Card", "Cash", "Net Banking", "EMI"]

CATEGORY_COLORS = {
    "Food & Dining": "#FF6B6B",
    "Transportation": "#4ECDC4",
    "Shopping": "#FFE66D",
    "Bills & Utilities": "#A8E6CF",
    "Healthcare": "#FF8B94",
    "Entertainment": "#B39DDB",
    "Education": "#80DEEA",
    "Investments & Savings": "#A5D6A7"
}

# Init 
init_db()
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

#  Auth Pages 
def show_auth():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px'>
        <h1 style='font-size:3rem; color:#7c83fd;'>₹ SpendSmart</h1>
        <p style='color:#8b90b8; font-size:1.1rem;'>ML-Powered Expense Intelligence for India</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True, type="primary"):
                uid = login_user(username, password)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with tab2:
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password", key="reg_conf")
            if st.button("Create Account", use_container_width=True):
                if new_pass != confirm:
                    st.error("Passwords don't match")
                elif len(new_pass) < 6:
                    st.error("Password too short (min 6 chars)")
                else:
                    uid = register_user(new_user, new_pass)
                    if uid:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("Username already taken")
    
    st.markdown("""
    <div style='text-align:center; margin-top:40px; color:#555'>
        <b>Demo:</b> username: <code>demo</code> | password: <code>demo123</code>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-create demo account
    register_user("demo", "demo123")

#  Main App 
def show_app():
    current_month = datetime.now().strftime("%Y-%m")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:16px 0'>
            <h3 style='color:#7c83fd; margin:0'>₹ SpendSmart</h3>
            <p style='color:#8b90b8; font-size:0.85rem; margin:4px 0'>Hello, {st.session_state.username}!</p>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.radio("Navigate", 
                        ["📊 Dashboard", "➕ Add Expense", "📋 My Expenses", 
                         "🎯 Budget Manager", "🤖 ML Insights"],
                        label_visibility="collapsed")
        
        st.divider()
        
        # Quick stats
        df = get_expenses(st.session_state.user_id, current_month)
        if not df.empty:
            total = df['amount'].sum()
            st.metric("This Month", f"₹{total:,.0f}")
            st.metric("Transactions", len(df))
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    #  Pages 
    if page == "📊 Dashboard":
        show_dashboard(current_month)
    elif page == "➕ Add Expense":
        show_add_expense(current_month)
    elif page == "📋 My Expenses":
        show_expenses()
    elif page == "🎯 Budget Manager":
        show_budget_manager(current_month)
    elif page == "🤖 ML Insights":
        show_ml_insights()

def show_dashboard(current_month):
    st.title("📊 Dashboard")
    
    df_month = get_expenses(st.session_state.user_id, current_month)
    df_all = get_expenses(st.session_state.user_id)
    
    if df_month.empty:
        st.info("🌱 No expenses this month. Add your first expense!")
        return
    
    # ── Metric Cards ──
    total = df_month['amount'].sum()
    avg_daily = total / datetime.now().day
    top_cat = df_month.groupby('category')['amount'].sum().idxmax()
    num_tx = len(df_month)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>₹{total:,.0f}</div>
            <div class='metric-label'>Total This Month</div></div>""",
            unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>₹{avg_daily:,.0f}</div>
            <div class='metric-label'>Daily Average</div></div>""",
            unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{num_tx}</div>
            <div class='metric-label'>Transactions</div></div>""",
            unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value' style='font-size:1.2rem'>{top_cat}</div>
            <div class='metric-label'>Top Category</div></div>""",
            unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        cat_sum = df_month.groupby('category')['amount'].sum().reset_index()
        fig = px.pie(cat_sum, values='amount', names='category',
                     title="Spending by Category",
                     color='category',
                     color_discrete_map=CATEGORY_COLORS,
                     hole=0.4)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar by payment mode
        pm_sum = df_month.groupby('payment_mode')['amount'].sum().reset_index()
        fig2 = px.bar(pm_sum, x='payment_mode', y='amount',
                      title="Spending by Payment Mode",
                      color='amount',
                      color_continuous_scale='Bluyl')
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            xaxis=dict(gridcolor='#1f2235'),
            yaxis=dict(gridcolor='#1f2235')
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Trend line
    if not df_all.empty and len(df_all) > 5:
        df_all['date'] = pd.to_datetime(df_all['date'])
        daily = df_all.groupby('date')['amount'].sum().reset_index()
        daily['cumulative'] = daily['amount'].cumsum()
        
        fig3 = px.line(daily, x='date', y='amount',
                       title="Daily Spending Trend",
                       color_discrete_sequence=['#7c83fd'])
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            xaxis=dict(gridcolor='#1f2235'),
            yaxis=dict(gridcolor='#1f2235')
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Budget alerts
    budgets = get_budgets(st.session_state.user_id, current_month)
    if budgets:
        st.subheader("🚨 Budget Alerts")
        cat_totals = df_month.groupby('category')['amount'].sum().to_dict()
        for cat, limit in budgets.items():
            spent = cat_totals.get(cat, 0)
            pct = (spent / limit) * 100
            if pct >= 100:
                st.markdown(f"""<div class='alert-danger'>
                    🔴 <b>{cat}</b>: Exceeded! Spent ₹{spent:,.0f} / Budget ₹{limit:,.0f} ({pct:.0f}%)
                </div>""", unsafe_allow_html=True)
            elif pct >= 80:
                st.markdown(f"""<div class='alert-warning'>
                    🟡 <b>{cat}</b>: Near limit! Spent ₹{spent:,.0f} / Budget ₹{limit:,.0f} ({pct:.0f}%)
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='alert-success'>
                    🟢 <b>{cat}</b>: ₹{spent:,.0f} / ₹{limit:,.0f} ({pct:.0f}%)
                </div>""", unsafe_allow_html=True)

def show_add_expense(current_month):
    st.title("➕ Add New Expense")
    
    model_exists = os.path.exists("models/expense_model.pkl")
    if not model_exists:
        st.warning("⚠️ ML model not trained yet. Run `python train_model.py` first.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        description = st.text_input("📝 Description", 
                                     placeholder="e.g. Zomato biryani order, Petrol fill up, Netflix subscription")
        
        # Auto-categorize
        predicted_cat = None
        confidence = 0
        if description and len(description) > 3 and model_exists:
            try:
                predicted_cat, confidence = predict_category(description)
                st.markdown(f"""
                <div style='background:#1a1d2e; border:1px solid #2d3154; border-radius:10px; padding:12px; margin:8px 0'>
                    🤖 <b>ML Prediction:</b> 
                    <span class='category-badge'>{predicted_cat}</span>
                    &nbsp; <span style='color:#8b90b8; font-size:0.85rem'>Confidence: {confidence}%</span>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass
        
        default_idx = CATEGORIES.index(predicted_cat) if predicted_cat in CATEGORIES else 0
        category = st.selectbox("📂 Category", CATEGORIES, index=default_idx,
                                 help="ML auto-selects this. You can override.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            amount = st.number_input("₹ Amount (INR)", min_value=1.0, value=100.0, step=10.0)
        with col_b:
            payment_mode = st.selectbox("💳 Payment Mode", PAYMENT_MODES)
        
        expense_date = st.date_input("📅 Date", value=date.today())
        
        if st.button("✅ Add Expense", type="primary", use_container_width=True):
            if description and amount > 0:
                add_expense(
                    st.session_state.user_id,
                    description, amount, category,
                    payment_mode, str(expense_date)
                )
                st.success(f"✅ Added: **{description}** — ₹{amount:,.2f} in *{category}*")
                st.balloons()
            else:
                st.error("Please fill all fields")
    
    with col2:
        st.markdown("""
        <div style='background:#1a1d2e; border-radius:16px; padding:20px; margin-top:0'>
            <h4 style='color:#7c83fd'>💡 Quick Tips</h4>
            <ul style='color:#8b90b8; font-size:0.88rem; line-height:1.8'>
                <li>Type a description and the ML model will auto-predict the category</li>
                <li>UPI payments are auto-tagged for India</li>
                <li>You can override the ML prediction</li>
                <li>Set monthly budgets in Budget Manager</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent 5 expenses
        st.markdown("#### Recent Expenses")
        df = get_expenses(st.session_state.user_id)
        if not df.empty:
            for _, row in df.head(5).iterrows():
                st.markdown(f"""
                <div style='padding:8px 0; border-bottom:1px solid #1f2235'>
                    <div style='font-size:0.88rem'>{row['description'][:30]}</div>
                    <div style='color:#7c83fd; font-weight:600'>₹{row['amount']:,.0f}</div>
                    <div style='font-size:0.75rem; color:#8b90b8'>{row['category']} · {row['date']}</div>
                </div>
                """, unsafe_allow_html=True)

def show_expenses():
    st.title("📋 My Expenses")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_month = st.text_input("Filter Month (YYYY-MM)", 
                                      value=datetime.now().strftime("%Y-%m"))
    with col2:
        filter_cat = st.selectbox("Filter Category", ["All"] + CATEGORIES)
    with col3:
        sort_by = st.selectbox("Sort By", ["Date ↓", "Amount ↓", "Category"])
    
    df = get_expenses(st.session_state.user_id, filter_month if filter_month else None)
    
    if filter_cat != "All":
        df = df[df['category'] == filter_cat]
    
    if sort_by == "Amount ↓":
        df = df.sort_values('amount', ascending=False)
    elif sort_by == "Category":
        df = df.sort_values('category')
    
    if df.empty:
        st.info("No expenses found for selected filters.")
        return
    
    st.markdown(f"**{len(df)} expenses · Total: ₹{df['amount'].sum():,.2f}**")
    
    # Display table
    display_df = df[['date', 'description', 'amount', 'category', 'payment_mode']].copy()
    display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Delete option
    if not df.empty:
        st.markdown("#### Delete an Expense")
        expense_id = st.number_input("Enter Expense ID to delete", min_value=1, step=1)
        if st.button("🗑️ Delete", type="secondary"):
            delete_expense(expense_id, st.session_state.user_id)
            st.success("Deleted!")
            st.rerun()
    
    # CSV export
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Export CSV", csv, "expenses.csv", "text/csv")

def show_budget_manager(current_month):
    st.title("🎯 Budget Manager")
    
    st.markdown("#### Set Monthly Budgets (INR)")
    
    col1, col2 = st.columns(2)
    budgets = get_budgets(st.session_state.user_id, current_month)
    df_month = get_expenses(st.session_state.user_id, current_month)
    cat_totals = df_month.groupby('category')['amount'].sum().to_dict() if not df_month.empty else {}
    
    for i, cat in enumerate(CATEGORIES):
        col = col1 if i % 2 == 0 else col2
        with col:
            current = budgets.get(cat, 0)
            new_limit = st.number_input(
                f"{cat}",
                min_value=0.0, value=float(current),
                step=500.0, key=f"budget_{cat}"
            )
            if new_limit > 0:
                spent = cat_totals.get(cat, 0)
                pct = min((spent / new_limit) * 100, 100) if new_limit > 0 else 0
                color = "#ff4b4b" if pct >= 100 else "#ffab00" if pct >= 80 else "#00c896"
                st.markdown(f"""
                <div style='background:#1a1d2e; border-radius:8px; padding:4px 8px; margin-bottom:12px'>
                    <div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#8b90b8'>
                        <span>Spent: ₹{spent:,.0f}</span>
                        <span style='color:{color}'>{pct:.0f}%</span>
                    </div>
                    <div style='background:#252840; border-radius:4px; height:6px; margin-top:4px'>
                        <div style='background:{color}; width:{pct}%; height:6px; border-radius:4px'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    if st.button("💾 Save All Budgets", type="primary", use_container_width=True):
        for cat in CATEGORIES:
            limit = st.session_state.get(f"budget_{cat}", 0)
            if limit > 0:
                set_budget(st.session_state.user_id, cat, limit, current_month)
        st.success("✅ Budgets saved!")
        st.rerun()

def show_ml_insights():
    st.title("🤖 ML Insights")
    
    model_exists = os.path.exists("models/expense_model.pkl")
    
    if not model_exists:
        st.error("❌ Models not found. Run `python train_model.py` to train first.")
        st.code("python train_model.py", language="bash")
        return
    
    st.markdown("#### 🧪 Test the ML Categorizer")
    test_desc = st.text_input("Enter any expense description to test:")
    if test_desc:
        cat, conf = predict_category(test_desc)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value' style='font-size:1.4rem'>{cat}</div>
                <div class='metric-label'>Predicted Category</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{conf}%</div>
                <div class='metric-label'>Confidence Score</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Compare both models
    st.markdown("---")
    st.markdown("#### 📊 Model Comparison")
    
    comparison_data = {
        "Model": ["Naive Bayes", "Decision Tree"],
        "Algorithm Type": ["Probabilistic", "Rule-based"],
        "Best For": ["Text Classification", "Tabular patterns"],
        "Typical Accuracy": ["88–92%", "85–90%"],
        "Training Speed": ["Very Fast", "Fast"],
        "Used In App": ["✅ Primary", "Fallback"]
    }
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
    
    # Spending insights
    df = get_expenses(st.session_state.user_id)
    if not df.empty and len(df) >= 5:
        st.markdown("---")
        st.markdown("#### 🧠 Your Spending Patterns")
        
        cat_avg = df.groupby('category')['amount'].agg(['mean', 'count', 'sum'])
        cat_avg.columns = ['Avg Amount (₹)', 'Transactions', 'Total (₹)']
        cat_avg = cat_avg.round(2).sort_values('Total (₹)', ascending=False)
        
        st.dataframe(cat_avg, use_container_width=True)
        
        # Most frequent payment mode
        top_payment = df['payment_mode'].value_counts().index[0]
        top_cat = df.groupby('category')['amount'].sum().idxmax()
        avg_txn = df['amount'].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Preferred Payment", top_payment)
        col2.metric("Biggest Spend Area", top_cat)
        col3.metric("Avg Transaction", f"₹{avg_txn:,.0f}")

#  Entry Point 
if st.session_state.user_id is None:
    show_auth()
else:
    show_app()