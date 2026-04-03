"""
data_transformation.py
APL Logistics – Customer, Product & Profitability Performance Analysis
Data Transformation Pipeline
Author: APL Logistics Analytics Team
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. LOAD RAW DATA
# ─────────────────────────────────────────────
print("=" * 60)
print("APL LOGISTICS – DATA TRANSFORMATION PIPELINE")
print("=" * 60)

df = pd.read_csv("APL_Logistics.csv", encoding="latin1")
print(f"[INFO] Raw data loaded   : {df.shape[0]:,} rows × {df.shape[1]} columns")

# ─────────────────────────────────────────────
# 2. COLUMN RENAMING  (snake_case, no spaces)
# ─────────────────────────────────────────────
rename_map = {
    "Type":                       "payment_type",
    "Days for shipping (real)":   "shipping_days_actual",
    "Days for shipment (scheduled)": "shipping_days_scheduled",
    "Benefit per order":          "benefit_per_order",
    "Sales per customer":         "sales_per_customer",
    "Delivery Status":            "delivery_status",
    "Late_delivery_risk":         "late_delivery_risk",
    "Category Id":                "category_id",
    "Category Name":              "category_name",
    "Customer City":              "customer_city",
    "Customer Country":           "customer_country",
    "Customer Fname":             "customer_fname",
    "Customer Id":                "customer_id",
    "Customer Lname":             "customer_lname",
    "Customer Segment":           "customer_segment",
    "Customer State":             "customer_state",
    "Customer Street":            "customer_street",
    "Customer Zipcode":           "customer_zipcode",
    "Department Id":              "department_id",
    "Department Name":            "department_name",
    "Latitude":                   "latitude",
    "Longitude":                  "longitude",
    "Market":                     "market",
    "Order City":                 "order_city",
    "Order Country":              "order_country",
    "Order Customer Id":          "order_customer_id",
    "Order Item Discount":        "order_item_discount",
    "Order Item Discount Rate":   "order_item_discount_rate",
    "Order Item Product Price":   "order_item_product_price",
    "Order Item Profit Ratio":    "order_item_profit_ratio",
    "Order Item Quantity":        "order_item_quantity",
    "Sales":                      "sales",
    "Order Item Total":           "order_item_total",
    "Order Profit Per Order":     "order_profit_per_order",
    "Order Region":               "order_region",
    "Order State":                "order_state",
    "Order Status":               "order_status",
    "Product Name":               "product_name",
    "Product Price":              "product_price",
    "Shipping Mode":              "shipping_mode",
}
df.rename(columns=rename_map, inplace=True)

# ─────────────────────────────────────────────
# 3. DATA CLEANING
# ─────────────────────────────────────────────

# 3a. Fill minor missing values
df["customer_lname"].fillna("Unknown", inplace=True)
df["customer_zipcode"].fillna(df["customer_zipcode"].median(), inplace=True)

# 3b. Trim string columns
str_cols = df.select_dtypes(include="object").columns
for c in str_cols:
    df[c] = df[c].astype(str).str.strip()

# 3c. Standardise categorical values
df["order_status"]    = df["order_status"].str.upper()
df["delivery_status"] = df["delivery_status"].str.strip().str.title()
df["shipping_mode"]   = df["shipping_mode"].str.strip().str.title()
df["customer_segment"]= df["customer_segment"].str.strip().str.title()
df["market"]          = df["market"].str.strip().str.title()
df["payment_type"]    = df["payment_type"].str.strip().str.upper()

# 3d. Remove records with zero/negative sales (data integrity)
before = len(df)
df = df[df["sales"] > 0].copy()
print(f"[CLEAN] Removed {before - len(df):,} records with non-positive sales")

# 3e. Cap extreme profit outliers (keep ±3 SD)
profit_mean = df["order_profit_per_order"].mean()
profit_std  = df["order_profit_per_order"].std()
df["order_profit_per_order"] = df["order_profit_per_order"].clip(
    profit_mean - 3 * profit_std, profit_mean + 3 * profit_std
)

# ─────────────────────────────────────────────
# 4. FEATURE ENGINEERING
# ─────────────────────────────────────────────

# 4a. Core financial metrics
df["gross_margin_pct"]    = (df["order_profit_per_order"] / df["sales"]) * 100
df["discount_amount"]     = df["order_item_product_price"] * df["order_item_discount_rate"]
df["revenue_after_discount"] = df["sales"] - df["order_item_discount"]
df["effective_unit_price"] = np.where(
    df["order_item_quantity"] > 0,
    df["order_item_total"] / df["order_item_quantity"],
    df["order_item_product_price"]
)
df["unit_profit"]         = np.where(
    df["order_item_quantity"] > 0,
    df["order_profit_per_order"] / df["order_item_quantity"],
    0
)

# 4b. Shipping performance features
df["shipping_delay_days"]  = df["shipping_days_actual"] - df["shipping_days_scheduled"]
df["is_late_delivery"]     = (df["shipping_delay_days"] > 0).astype(int)
df["shipping_efficiency"]  = np.where(
    df["shipping_days_scheduled"] > 0,
    df["shipping_days_actual"] / df["shipping_days_scheduled"],
    1.0
)

# 4c. Discount impact features
df["discount_impact_on_profit"] = df["order_item_discount"] - df["order_profit_per_order"]
df["discount_erodes_profit"]    = (df["discount_amount"] > df["order_profit_per_order"]).astype(int)
df["net_margin_after_discount"] = df["gross_margin_pct"] - (df["order_item_discount_rate"] * 100)

# 4d. Order profitability classification
conditions = [
    df["order_profit_per_order"] < 0,
    df["order_profit_per_order"] == 0,
    (df["order_profit_per_order"] > 0) & (df["gross_margin_pct"] < 10),
    (df["gross_margin_pct"] >= 10) & (df["gross_margin_pct"] < 25),
    df["gross_margin_pct"] >= 25,
]
choices = ["Loss-Making", "Break-Even", "Low-Margin", "Moderate-Margin", "High-Margin"]
df["profitability_class"] = np.select(conditions, choices, default="Unknown")

# 4e. Customer-level aggregated features
cust_agg = df.groupby("customer_id").agg(
    cust_total_sales    = ("sales", "sum"),
    cust_total_profit   = ("order_profit_per_order", "sum"),
    cust_order_count    = ("sales", "count"),
    cust_avg_discount   = ("order_item_discount_rate", "mean"),
    cust_avg_margin     = ("gross_margin_pct", "mean"),
).reset_index()
cust_agg["cust_avg_order_value"] = cust_agg["cust_total_sales"] / cust_agg["cust_order_count"]
cust_agg["cust_profit_margin"]   = (cust_agg["cust_total_profit"] / cust_agg["cust_total_sales"]) * 100

# Customer value tier (RFM-lite using profit contribution)
profit_q = cust_agg["cust_total_profit"].quantile([0.25, 0.50, 0.75])
def assign_tier(p):
    if p < 0:              return "Loss Customer"
    elif p < profit_q[0.25]: return "Low Value"
    elif p < profit_q[0.50]: return "Mid Value"
    elif p < profit_q[0.75]: return "High Value"
    else:                  return "Premium"
cust_agg["customer_value_tier"] = cust_agg["cust_total_profit"].apply(assign_tier)

df = df.merge(cust_agg, on="customer_id", how="left")

# 4f. Product-level aggregated features
prod_agg = df.groupby("product_name").agg(
    prod_total_sales   = ("sales", "sum"),
    prod_total_profit  = ("order_profit_per_order", "sum"),
    prod_order_count   = ("sales", "count"),
    prod_avg_margin    = ("gross_margin_pct", "mean"),
).reset_index()
prod_agg["prod_profit_margin"] = (prod_agg["prod_total_profit"] / prod_agg["prod_total_sales"]) * 100
prod_margin_q = prod_agg["prod_profit_margin"].quantile([0.25, 0.75])
def product_tier(m):
    if m < 0:                           return "Loss Product"
    elif m < prod_margin_q[0.25]:       return "Low Margin"
    elif m < prod_margin_q[0.75]:       return "Moderate Margin"
    else:                               return "High Margin"
prod_agg["product_margin_tier"] = prod_agg["prod_profit_margin"].apply(product_tier)
df = df.merge(prod_agg, on="product_name", how="left")

# 4g. Market/Region aggregated features
mkt_agg = df.groupby("market").agg(
    mkt_total_sales  = ("sales", "sum"),
    mkt_total_profit = ("order_profit_per_order", "sum"),
    mkt_order_count  = ("sales", "count"),
).reset_index()
mkt_agg["mkt_profit_margin"] = (mkt_agg["mkt_total_profit"] / mkt_agg["mkt_total_sales"]) * 100
df = df.merge(mkt_agg, on="market", how="left")

# 4h. Category-level margin score
cat_agg = df.groupby("category_name").agg(
    cat_total_sales  = ("sales", "sum"),
    cat_total_profit = ("order_profit_per_order", "sum"),
    cat_avg_discount = ("order_item_discount_rate", "mean"),
).reset_index()
cat_agg["cat_margin_pct"] = (cat_agg["cat_total_profit"] / cat_agg["cat_total_sales"]) * 100
df = df.merge(cat_agg, on="category_name", how="left")

# 4i. Shipping cost proxy (based on mode & weight proxy = quantity)
shipping_cost_map = {
    "Same Day":      15.0,
    "First Class":   10.0,
    "Second Class":  7.0,
    "Standard Class": 4.5,
}
df["shipping_cost_proxy"] = df["shipping_mode"].map(shipping_cost_map).fillna(4.5)
df["shipping_cost_total"] = df["shipping_cost_proxy"] * df["order_item_quantity"]
df["profit_after_shipping"] = df["order_profit_per_order"] - df["shipping_cost_total"]

# 4j. Discount band categorisation
df["discount_band"] = pd.cut(
    df["order_item_discount_rate"],
    bins=[-0.001, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25],
    labels=["No Discount", "1–5%", "6–10%", "11–15%", "16–20%", "21–25%"]
)

# 4k. Shipping mode premium flag
df["is_express_shipping"] = df["shipping_mode"].isin(["Same Day", "First Class"]).astype(int)

# 4l. Revenue concentration flag (high-value orders)
sales_95th = df["sales"].quantile(0.95)
df["is_high_value_order"] = (df["sales"] >= sales_95th).astype(int)

# 4m. Customer full name
df["customer_name"] = df["customer_fname"] + " " + df["customer_lname"]

# 4n. Order is cancelled flag
df["is_order_cancelled"] = (df["order_status"] == "CANCELED").astype(int)

# 4o. Margin erosion risk score (0–100)
df["margin_erosion_risk"] = (
    df["order_item_discount_rate"] * 50 +
    df["late_delivery_risk"] * 20 +
    df["is_order_cancelled"] * 30
).clip(0, 100)

# ─────────────────────────────────────────────
# 5. FINAL VALIDATION & COLUMN ORDERING
# ─────────────────────────────────────────────

# Drop PII columns not needed for analytics
drop_cols = ["customer_street", "customer_fname", "customer_lname",
             "customer_zipcode", "latitude", "longitude"]
df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

# Round numeric columns for cleanliness
float_cols = df.select_dtypes(include="float64").columns
df[float_cols] = df[float_cols].round(4)

print(f"[INFO] Transformed data  : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"[INFO] New features added: {df.shape[1] - 40 + len(drop_cols)} engineered features")
print(f"\n[FEATURE LIST]")
for c in df.columns:
    print(f"  • {c}")

# ─────────────────────────────────────────────
# 6. EXPORT
# ─────────────────────────────────────────────
output_path = "APL_Logistics_Transformed.csv"
df.to_csv(output_path, index=False)
print(f"\n[DONE] Saved → {output_path}")

# Quick financial summary
print("\n" + "=" * 60)
print("FINANCIAL SUMMARY")
print("=" * 60)
print(f"  Total Revenue     : ${df['sales'].sum():>15,.2f}")
print(f"  Total Profit      : ${df['order_profit_per_order'].sum():>15,.2f}")
print(f"  Overall Margin    : {(df['order_profit_per_order'].sum()/df['sales'].sum()*100):>14.2f}%")
print(f"  Total Discount    : ${df['order_item_discount'].sum():>15,.2f}")
print(f"  Avg Discount Rate : {df['order_item_discount_rate'].mean()*100:>13.2f}%")
print(f"  Late Delivery %   : {df['is_late_delivery'].mean()*100:>13.2f}%")
print(f"  Loss-Making Orders: {(df['profitability_class']=='Loss-Making').sum():>15,}")
