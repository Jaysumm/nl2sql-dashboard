"""
Generates a synthetic retail sales dataset (orders + line items) and saves
it as data/sales.csv. Structure is intentionally similar to the classic
"Sample Superstore" dataset so it plugs into an existing analytics story:
orders, products, categories, regions, customers, sales, profit, discount.

Run:
    python data/generate_data.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_ROWS = 5000

CATEGORIES = {
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Labels"],
    "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
}

REGIONS = ["East", "West", "Central", "South"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]

start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 6, 30)
date_range_days = (end_date - start_date).days

rows = []
customer_ids = [f"CUST-{i:05d}" for i in range(1, 901)]
product_id_counter = 1

for i in range(1, N_ROWS + 1):
    order_id = f"ORD-{i:06d}"
    order_date = start_date + timedelta(days=int(np.random.randint(0, date_range_days)))
    ship_date = order_date + timedelta(days=int(np.random.randint(1, 8)))

    category = np.random.choice(list(CATEGORIES.keys()), p=[0.25, 0.45, 0.30])
    sub_category = np.random.choice(CATEGORIES[category])

    product_id = f"PROD-{product_id_counter:04d}"
    product_id_counter = (product_id_counter % 300) + 1

    region = np.random.choice(REGIONS)
    segment = np.random.choice(SEGMENTS, p=[0.5, 0.3, 0.2])
    ship_mode = np.random.choice(SHIP_MODES, p=[0.6, 0.2, 0.15, 0.05])
    customer_id = np.random.choice(customer_ids)

    quantity = int(np.random.randint(1, 12))
    unit_price = float(np.round(np.random.uniform(5, 900), 2))
    discount = float(np.random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.3, 0.5], p=[0.35,0.15,0.1,0.15,0.1,0.08,0.05,0.02]))

    sales = round(quantity * unit_price * (1 - discount), 2)
    margin_rate = np.random.uniform(-0.1, 0.4)  # some categories run at a loss when heavily discounted
    profit = round(sales * margin_rate, 2)

    rows.append({
        "order_id": order_id,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "ship_date": ship_date.strftime("%Y-%m-%d"),
        "ship_mode": ship_mode,
        "customer_id": customer_id,
        "segment": segment,
        "region": region,
        "product_id": product_id,
        "category": category,
        "sub_category": sub_category,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount": discount,
        "sales": sales,
        "profit": profit,
    })

df = pd.DataFrame(rows)
df.to_csv("data/sales.csv", index=False)
print(f"Generated {len(df)} rows -> data/sales.csv")
print(df.head())
