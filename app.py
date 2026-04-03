"""
app.py  –  APL Logistics Profitability Intelligence Dashboard
Streamlit Cloud compatible | Author: APL Logistics Analytics Team
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="APL Logistics – Profitability Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
.kpi-card { background: linear-gradient(135deg,#1e3a5f,#2d6a9f);
            border-radius:12px; padding:16px; color:white; margin:4px; }
.section-header { font-size:1.3rem; font-weight:700; color:#1e3a5f;
                  border-bottom:3px solid #2d6a9f; padding-bottom:6px; margin:16px 0 8px; }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ────────────────────────────────────────────
@st.cache_data(show_spinner="Loading transformed data …")
def load_data():
    df = pd.read_csv("APL_Logistics_Transformed.csv", low_memory=False)
    df["discount_band"] = df["discount_band"].astype(str)
    return df

df_full = load_data()

# ─── SIDEBAR FILTERS ─────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/APL_logo.svg/320px-APL_logo.svg.png",
             width=160, use_container_width=False)
    st.title("🔍 Filters")

    markets = ["All"] + sorted(df_full["market"].dropna().unique().tolist())
    sel_market = st.multiselect("Market", markets, default=["All"])

    segments = ["All"] + sorted(df_full["customer_segment"].dropna().unique().tolist())
    sel_segment = st.multiselect("Customer Segment", segments, default=["All"])

    categories = ["All"] + sorted(df_full["category_name"].dropna().unique().tolist())
    sel_category = st.multiselect("Category", categories, default=["All"])

    ship_modes = ["All"] + sorted(df_full["shipping_mode"].dropna().unique().tolist())
    sel_ship = st.multiselect("Shipping Mode", ship_modes, default=["All"])

    disc_range = st.slider("Discount Rate Range (%)",
                           0.0, 25.0, (0.0, 25.0), step=0.5)

    st.markdown("---")
    st.caption("APL Logistics © 2024 | Powered by Streamlit")

# ─── APPLY FILTERS ───────────────────────────────────────────
def apply_filters(df):
    d = df.copy()
    if "All" not in sel_market:
        d = d[d["market"].isin(sel_market)]
    if "All" not in sel_segment:
        d = d[d["customer_segment"].isin(sel_segment)]
    if "All" not in sel_category:
        d = d[d["category_name"].isin(sel_category)]
    if "All" not in sel_ship:
        d = d[d["shipping_mode"].isin(sel_ship)]
    d = d[(d["order_item_discount_rate"] * 100 >= disc_range[0]) &
          (d["order_item_discount_rate"] * 100 <= disc_range[1])]
    return d

df = apply_filters(df_full)

# ─── HEADER ──────────────────────────────────────────────────
st.title("🚢 APL Logistics – Profitability Intelligence Dashboard")
st.markdown(f"**Filtered dataset:** `{len(df):,}` orders | "
            f"**Coverage:** {df['market'].nunique()} markets · "
            f"{df['customer_id'].nunique():,} customers · "
            f"{df['product_name'].nunique()} products")
st.markdown("---")

# ─────────────────────────────────────────────────────────────
# TAB LAYOUT
# ─────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Revenue & Profit Overview",
    "👥 Customer Value",
    "📦 Product & Category",
    "💸 Discount Impact",
    "🌍 Market & Region",
    "🚚 Shipping Analytics",
])

# ════════════════════════════════════════════════════════════
# TAB 1 – REVENUE & PROFIT OVERVIEW
# ════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<p class="section-header">Key Performance Indicators</p>', unsafe_allow_html=True)

    total_revenue   = df["sales"].sum()
    total_profit    = df["order_profit_per_order"].sum()
    profit_margin   = (total_profit / total_revenue * 100) if total_revenue else 0
    total_discount  = df["order_item_discount"].sum()
    avg_order_val   = df["sales"].mean()
    loss_orders     = (df["profitability_class"] == "Loss-Making").sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("💰 Total Revenue",     f"${total_revenue:,.0f}")
    c2.metric("📈 Total Profit",      f"${total_profit:,.0f}")
    c3.metric("📉 Profit Margin",     f"{profit_margin:.2f}%")
    c4.metric("🏷️ Total Discounts",  f"${total_discount:,.0f}")
    c5.metric("🛒 Avg Order Value",   f"${avg_order_val:,.2f}")
    c6.metric("⚠️ Loss Orders",       f"{loss_orders:,}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # Revenue vs Profit by Market
        mkt = df.groupby("market").agg(
            Revenue=("sales", "sum"),
            Profit=("order_profit_per_order", "sum")
        ).reset_index().sort_values("Revenue", ascending=False)
        fig = go.Figure()
        fig.add_bar(x=mkt["market"], y=mkt["Revenue"], name="Revenue",
                    marker_color="#2196F3")
        fig.add_bar(x=mkt["market"], y=mkt["Profit"], name="Profit",
                    marker_color="#4CAF50")
        fig.update_layout(title="Revenue vs Profit by Market", barmode="group",
                          height=380, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Profitability class distribution
        pc = df["profitability_class"].value_counts().reset_index()
        pc.columns = ["Class", "Count"]
        color_map = {"Loss-Making":"#f44336","Break-Even":"#FF9800",
                     "Low-Margin":"#FFEB3B","Moderate-Margin":"#8BC34A",
                     "High-Margin":"#4CAF50"}
        fig2 = px.pie(pc, values="Count", names="Class", title="Order Profitability Distribution",
                      color="Class", color_discrete_map=color_map, hole=0.4)
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Margin by segment
        seg = df.groupby("customer_segment").agg(
            Revenue=("sales","sum"), Profit=("order_profit_per_order","sum")
        ).reset_index()
        seg["Margin%"] = seg["Profit"] / seg["Revenue"] * 100
        fig3 = px.bar(seg, x="customer_segment", y="Margin%",
                      title="Profit Margin % by Customer Segment",
                      color="Margin%", color_continuous_scale="RdYlGn",
                      text=seg["Margin%"].round(1).astype(str) + "%")
        fig3.update_layout(height=350, template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Shipping mode revenue breakdown
        sm = df.groupby("shipping_mode").agg(
            Revenue=("sales","sum"), Profit=("order_profit_per_order","sum")
        ).reset_index()
        sm["Margin%"] = sm["Profit"] / sm["Revenue"] * 100
        fig4 = px.bar(sm, x="shipping_mode", y=["Revenue","Profit"],
                      title="Revenue & Profit by Shipping Mode", barmode="group",
                      template="plotly_white")
        fig4.update_layout(height=350)
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 2 – CUSTOMER VALUE DASHBOARD
# ════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<p class="section-header">Customer Value & Contribution Analysis</p>',
                unsafe_allow_html=True)

    cust = df.groupby(["customer_id","customer_name","customer_segment","customer_value_tier"]).agg(
        Total_Sales   =("sales","sum"),
        Total_Profit  =("order_profit_per_order","sum"),
        Order_Count   =("sales","count"),
        Avg_Discount  =("order_item_discount_rate","mean"),
    ).reset_index()
    cust["Margin%"] = (cust["Total_Profit"] / cust["Total_Sales"] * 100).round(2)

    col1, col2 = st.columns(2)
    with col1:
        # Top 15 customers by profit
        top15 = cust.nlargest(15, "Total_Profit")
        fig = px.bar(top15, x="Total_Profit", y="customer_name", orientation="h",
                     title="Top 15 Customers by Total Profit",
                     color="Margin%", color_continuous_scale="Greens",
                     text=top15["Total_Profit"].apply(lambda x: f"${x:,.0f}"))
        fig.update_layout(height=450, template="plotly_white", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bottom 15 customers by profit
        bot15 = cust.nsmallest(15, "Total_Profit")
        fig2 = px.bar(bot15, x="Total_Profit", y="customer_name", orientation="h",
                      title="Bottom 15 Customers by Profit (Loss Risk)",
                      color="Total_Profit", color_continuous_scale="Reds_r",
                      text=bot15["Total_Profit"].apply(lambda x: f"${x:,.0f}"))
        fig2.update_layout(height=450, template="plotly_white", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Customer value tier distribution
        tier_cnt = cust["customer_value_tier"].value_counts().reset_index()
        tier_cnt.columns = ["Tier","Count"]
        tier_color = {"Premium":"#1565C0","High Value":"#42A5F5",
                      "Mid Value":"#A5D6A7","Low Value":"#FFCC80","Loss Customer":"#EF9A9A"}
        fig3 = px.pie(tier_cnt, values="Count", names="Tier",
                      title="Customer Value Tier Distribution",
                      color="Tier", color_discrete_map=tier_color, hole=0.45)
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Scatter – Sales vs Profit by segment
        fig4 = px.scatter(cust, x="Total_Sales", y="Total_Profit",
                          color="customer_segment", size="Order_Count",
                          hover_name="customer_name",
                          title="Sales vs Profit by Customer (bubble=order count)",
                          template="plotly_white")
        fig4.update_layout(height=380)
        st.plotly_chart(fig4, use_container_width=True)

    # Segment contribution
    seg_c = df.groupby("customer_segment").agg(
        Revenue=("sales","sum"), Profit=("order_profit_per_order","sum"),
        Customers=("customer_id","nunique")
    ).reset_index()
    seg_c["Margin%"]             = (seg_c["Profit"]/seg_c["Revenue"]*100).round(2)
    seg_c["Revenue_pct"]         = (seg_c["Revenue"]/seg_c["Revenue"].sum()*100).round(2)
    seg_c["Profit_pct"]          = (seg_c["Profit"]/seg_c["Profit"].sum()*100).round(2)
    st.markdown("#### Customer Segment Contribution Summary")
    st.dataframe(seg_c.style.format({
        "Revenue":"${:,.0f}","Profit":"${:,.0f}",
        "Margin%":"{:.2f}%","Revenue_pct":"{:.1f}%","Profit_pct":"{:.1f}%"
    }), use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 3 – PRODUCT & CATEGORY
# ════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<p class="section-header">Product & Category Profitability Analysis</p>',
                unsafe_allow_html=True)

    prod = df.groupby(["product_name","category_name","product_margin_tier"]).agg(
        Revenue=("sales","sum"),
        Profit=("order_profit_per_order","sum"),
        Orders=("sales","count"),
        Avg_Discount=("order_item_discount_rate","mean"),
    ).reset_index()
    prod["Margin%"] = (prod["Profit"]/prod["Revenue"]*100).round(2)

    col1, col2 = st.columns(2)
    with col1:
        top_prod = prod.nlargest(15,"Profit")
        fig = px.bar(top_prod, y="product_name", x="Profit", orientation="h",
                     title="Top 15 Products by Profit", color="Margin%",
                     color_continuous_scale="Greens", template="plotly_white",
                     text=top_prod["Profit"].apply(lambda x: f"${x:,.0f}"))
        fig.update_layout(height=450, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        low_prod = prod[prod["Profit"] < 0].nsmallest(15,"Profit")
        if len(low_prod) > 0:
            fig2 = px.bar(low_prod, y="product_name", x="Profit", orientation="h",
                          title="Loss-Making Products", color="Profit",
                          color_continuous_scale="Reds_r", template="plotly_white")
            fig2.update_layout(height=450, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No loss-making products under current filters.")

    # Category profitability heatmap
    cat = df.groupby(["category_name","customer_segment"]).agg(
        Profit=("order_profit_per_order","sum"),
    ).reset_index()
    cat_pivot = cat.pivot(index="category_name", columns="customer_segment", values="Profit").fillna(0)
    fig3 = px.imshow(cat_pivot, title="Category Profit Heatmap (by Customer Segment)",
                     color_continuous_scale="RdYlGn", aspect="auto",
                     labels=dict(color="Profit ($)"))
    fig3.update_layout(height=420, template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        cat_s = df.groupby("category_name").agg(
            Revenue=("sales","sum"), Profit=("order_profit_per_order","sum")
        ).reset_index()
        cat_s["Margin%"] = (cat_s["Profit"]/cat_s["Revenue"]*100).round(2)
        fig4 = px.treemap(cat_s, path=["category_name"], values="Revenue",
                          color="Margin%", color_continuous_scale="RdYlGn",
                          title="Revenue Treemap Coloured by Margin%")
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        fig5 = px.scatter(prod, x="Revenue", y="Margin%",
                          color="category_name", size="Orders",
                          hover_name="product_name",
                          title="Revenue vs Margin% by Product",
                          template="plotly_white")
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 4 – DISCOUNT IMPACT ANALYZER
# ════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<p class="section-header">Discount Impact & Margin Erosion Analysis</p>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Discount Given",   f"${df['order_item_discount'].sum():,.0f}")
    col2.metric("Orders w/ Profit Erosion",
                f"{df['discount_erodes_profit'].sum():,}")
    col3.metric("Avg Discount Rate",      f"{df['order_item_discount_rate'].mean()*100:.2f}%")
    col4.metric("Avg Profit Ratio",       f"{df['order_item_profit_ratio'].mean()*100:.2f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        disc_agg = df.groupby("discount_band").agg(
            Avg_Margin =("gross_margin_pct","mean"),
            Orders     =("sales","count"),
            Total_Profit=("order_profit_per_order","sum")
        ).reset_index()
        fig = px.bar(disc_agg, x="discount_band", y="Avg_Margin",
                     title="Avg Profit Margin % by Discount Band",
                     color="Avg_Margin", color_continuous_scale="RdYlGn",
                     text=disc_agg["Avg_Margin"].round(1).astype(str)+"%")
        fig.update_layout(height=380, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Scatter: discount rate vs profit ratio
        sample = df.sample(min(5000, len(df)), random_state=42)
        fig2 = px.scatter(sample, x="order_item_discount_rate",
                          y="order_item_profit_ratio",
                          color="profitability_class", opacity=0.5,
                          title="Discount Rate vs Profit Ratio",
                          labels={"order_item_discount_rate":"Discount Rate",
                                  "order_item_profit_ratio":"Profit Ratio"},
                          template="plotly_white")
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Discount by category
        cat_disc = df.groupby("category_name").agg(
            Avg_Discount =("order_item_discount_rate","mean"),
            Avg_Margin   =("gross_margin_pct","mean"),
        ).reset_index()
        fig3 = px.scatter(cat_disc, x="Avg_Discount", y="Avg_Margin",
                          text="category_name", size_max=20,
                          title="Category Avg Discount vs Avg Margin",
                          template="plotly_white")
        fig3.update_traces(textposition="top center")
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # What-if discount scenario
        st.markdown("#### 🔮 What-If Discount Scenario")
        what_if_disc = st.slider("Simulate new discount rate (%)", 0.0, 25.0, 10.0, 0.5)
        current_margin = df["gross_margin_pct"].mean()
        # Simple linear estimate: each 1% discount ≈ 0.8% margin loss
        simulated_margin = current_margin - (what_if_disc - df["order_item_discount_rate"].mean()*100) * 0.8
        delta = simulated_margin - current_margin
        col_a, col_b = st.columns(2)
        col_a.metric("Current Avg Margin", f"{current_margin:.2f}%")
        col_b.metric("Simulated Margin",   f"{simulated_margin:.2f}%",
                     delta=f"{delta:.2f}%")
        simulated_profit = df["order_profit_per_order"].sum() * (simulated_margin/current_margin) if current_margin else 0
        st.metric("Estimated Total Profit (simulated)",
                  f"${simulated_profit:,.0f}",
                  delta=f"${simulated_profit - df['order_profit_per_order'].sum():,.0f}")

        st.info("💡 **Insight:** Reducing discount rate by 2% could recover "
                f"~${abs(df['order_item_discount'].sum() * 0.2):,.0f} in potential profit annually.")

    # Margin erosion risk heatmap
    ero = df.groupby(["market","discount_band"]).agg(
        Avg_Margin=("gross_margin_pct","mean")
    ).reset_index()
    ero_pivot = ero.pivot(index="market", columns="discount_band", values="Avg_Margin").fillna(0)
    fig5 = px.imshow(ero_pivot, title="Margin Erosion Heatmap: Market × Discount Band",
                     color_continuous_scale="RdYlGn", aspect="auto")
    fig5.update_layout(height=350)
    st.plotly_chart(fig5, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 5 – MARKET & REGION
# ════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<p class="section-header">Market & Regional Profitability Intelligence</p>',
                unsafe_allow_html=True)

    mkt = df.groupby("market").agg(
        Revenue   =("sales","sum"),
        Profit    =("order_profit_per_order","sum"),
        Orders    =("sales","count"),
        Customers =("customer_id","nunique"),
        Avg_Disc  =("order_item_discount_rate","mean"),
    ).reset_index()
    mkt["Margin%"] = (mkt["Profit"]/mkt["Revenue"]*100).round(2)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(mkt.sort_values("Revenue", ascending=False),
                     x="market", y=["Revenue","Profit"],
                     title="Revenue vs Profit by Market", barmode="group",
                     template="plotly_white")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.scatter(mkt, x="Revenue", y="Margin%",
                          size="Orders", color="market",
                          text="market", hover_name="market",
                          title="Revenue vs Margin% by Market (bubble=orders)",
                          template="plotly_white")
        fig2.update_traces(textposition="top center")
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

    # Region breakdown
    reg = df.groupby("order_region").agg(
        Revenue=("sales","sum"),
        Profit =("order_profit_per_order","sum"),
        Orders =("sales","count"),
    ).reset_index()
    reg["Margin%"] = (reg["Profit"]/reg["Revenue"]*100).round(2)
    reg = reg.sort_values("Profit", ascending=False)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(reg, x="order_region", y="Margin%",
                      title="Profit Margin % by Order Region",
                      color="Margin%", color_continuous_scale="RdYlGn",
                      template="plotly_white")
        fig3.update_layout(height=380, xaxis_tickangle=-35)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.treemap(reg, path=["order_region"], values="Revenue",
                          color="Margin%", color_continuous_scale="RdYlGn",
                          title="Region Revenue Treemap by Margin%")
        fig4.update_layout(height=380)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### Market Performance Summary Table")
    st.dataframe(mkt.style.format({
        "Revenue":"${:,.0f}","Profit":"${:,.0f}","Margin%":"{:.2f}%",
        "Avg_Disc":"{:.2%}"
    }).background_gradient(subset=["Margin%"], cmap="RdYlGn"),
    use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 6 – SHIPPING ANALYTICS
# ════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<p class="section-header">Shipping Performance & Delivery Analytics</p>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Late Delivery Rate",    f"{df['is_late_delivery'].mean()*100:.1f}%")
    col2.metric("Avg Shipping Delay",    f"{df['shipping_delay_days'].mean():.1f} days")
    col3.metric("Shipping Cost (proxy)", f"${df['shipping_cost_total'].sum():,.0f}")
    col4.metric("Express Shipping Orders",f"{df['is_express_shipping'].sum():,}")

    col1, col2 = st.columns(2)
    with col1:
        late = df.groupby("shipping_mode").agg(
            Late_Rate=("is_late_delivery","mean"),
            Orders   =("sales","count"),
        ).reset_index()
        late["Late_Rate"] = late["Late_Rate"]*100
        fig = px.bar(late, x="shipping_mode", y="Late_Rate",
                     title="Late Delivery Rate by Shipping Mode (%)",
                     color="Late_Rate", color_continuous_scale="Reds",
                     text=late["Late_Rate"].round(1).astype(str)+"%")
        fig.update_layout(height=360, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        del_s = df["delivery_status"].value_counts().reset_index()
        del_s.columns = ["Status","Count"]
        fig2 = px.pie(del_s, values="Count", names="Status",
                      title="Delivery Status Distribution", hole=0.4)
        fig2.update_layout(height=360)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        delay_box = df[["shipping_mode","shipping_delay_days"]]
        fig3 = px.box(delay_box, x="shipping_mode", y="shipping_delay_days",
                      title="Shipping Delay Distribution by Mode",
                      template="plotly_white", color="shipping_mode")
        fig3.update_layout(height=360)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Profit after shipping cost by mode
        ps = df.groupby("shipping_mode").agg(
            Profit_Before=("order_profit_per_order","sum"),
            Profit_After =("profit_after_shipping","sum"),
        ).reset_index()
        fig4 = px.bar(ps, x="shipping_mode", y=["Profit_Before","Profit_After"],
                      title="Profit Before vs After Shipping Cost (proxy)",
                      barmode="group", template="plotly_white")
        fig4.update_layout(height=360)
        st.plotly_chart(fig4, use_container_width=True)

    # Margin erosion risk
    risk_agg = df.groupby("order_region").agg(
        Avg_Risk=("margin_erosion_risk","mean"),
        Late_Rate=("is_late_delivery","mean"),
    ).reset_index().sort_values("Avg_Risk", ascending=False)
    fig5 = px.bar(risk_agg, x="order_region", y="Avg_Risk",
                  title="Avg Margin Erosion Risk Score by Region",
                  color="Avg_Risk", color_continuous_scale="Reds",
                  template="plotly_white")
    fig5.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig5, use_container_width=True)
