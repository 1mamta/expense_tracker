import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

categories = {
    "Food & Dining": [
        "Zomato order biryani", "Swiggy pizza delivery", "Dominos burger meal",
        "Restaurant dinner family", "McDonald's lunch", "Cafe coffee snacks",
        "Chai samosa street food", "Grocery vegetables fruits", "Milk bread eggs",
        "Hotel breakfast buffet", "Dosa idli breakfast", "Paneer sabzi rotis",
        "Online food order", "Snacks biscuits chips", "Ice cream dessert parlour"
    ],
    "Transportation": [
        "Uber cab ride office", "Ola auto rickshaw", "Rapido bike taxi",
        "Petrol fuel bike", "Petrol car fill up", "Metro card recharge",
        "Bus pass monthly", "Train ticket booking", "Flight ticket travel",
        "Parking charges mall", "Toll road highway", "Diesel vehicle refill",
        "Local taxi station", "Auto rickshaw fare", "BEST bus Mumbai"
    ],
    "Shopping": [
        "Amazon online shopping", "Flipkart order clothes", "Myntra dress kurta",
        "Ajio fashion clothing", "Mall shopping shoes", "Grocery supermarket",
        "Reliance Smart groceries", "D-Mart household items", "Electronics gadget",
        "Mobile accessories buy", "Books stationery purchase", "Gift birthday present",
        "Home decor items", "Kitchen utensils buy", "Cosmetics beauty products"
    ],
    "Bills & Utilities": [
        "Electricity bill payment", "Water bill monthly", "Gas cylinder booking",
        "Internet broadband bill", "Jio recharge mobile", "Airtel postpaid bill",
        "BSNL landline bill", "DTH recharge tata sky", "Society maintenance fee",
        "House rent payment", "Insurance premium LIC", "Credit card bill",
        "EMI loan payment", "Property tax payment", "Municipal water bill"
    ],
    "Healthcare": [
        "Doctor consultation fee", "Medicine pharmacy purchase", "Apollo pharmacy",
        "Hospital OPD charges", "Diagnostic lab test", "Blood test report",
        "Dental checkup clinic", "Eye checkup glasses", "Gym membership fees",
        "Yoga class monthly", "Health insurance premium", "Vitamin supplements",
        "Physio therapy session", "Ambulance emergency", "Vaccination shot"
    ],
    "Entertainment": [
        "Netflix subscription monthly", "Amazon Prime renewal", "Hotstar Disney plus",
        "Movie ticket PVR", "INOX cinema show", "BookMyShow event",
        "Concert music show", "Gaming purchase online", "Spotify premium music",
        "YouTube premium plan", "OTT subscription combo", "Amusement park entry",
        "Cricket match ticket", "Comedy show event", "Zoo theme park visit"
    ],
    "Education": [
        "Tuition fees coaching", "Online course Udemy", "Coursera subscription",
        "Books college semester", "Stationery notebooks pen", "School fees monthly",
        "University exam fee", "NEET coaching fees", "JEE preparation course",
        "Skill development class", "Language learning app", "Workshop seminar fee",
        "Library membership fee", "Certification exam cost", "Study material purchase"
    ],
    "Investments & Savings": [
        "Mutual fund SIP payment", "PPF account deposit", "Fixed deposit bank",
        "Gold coin purchase", "Stock market shares", "Zerodha brokerage charge",
        "Crypto investment buy", "NPS pension fund", "RD recurring deposit",
        "Sovereign gold bond", "ELSS tax saving fund", "NSC post office",
        "EPF employee provident", "Share market demat", "ULIPpremium payment"
    ]
}

records = []
for category, descriptions in categories.items():
    for _ in range(75):
        desc = random.choice(descriptions)
        if category == "Bills & Utilities":
            amount = round(random.uniform(200, 5000), 2)
        elif category == "Investments & Savings":
            amount = round(random.uniform(500, 25000), 2)
        elif category == "Healthcare":
            amount = round(random.uniform(100, 3000), 2)
        elif category == "Transportation":
            amount = round(random.uniform(30, 2000), 2)
        elif category == "Food & Dining":
            amount = round(random.uniform(50, 1500), 2)
        elif category == "Shopping":
            amount = round(random.uniform(200, 8000), 2)
        elif category == "Entertainment":
            amount = round(random.uniform(99, 2000), 2)
        else:
            amount = round(random.uniform(500, 15000), 2)

        payment = random.choice(["UPI", "Card", "Cash", "Net Banking", "EMI"])
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        records.append({
            "description": desc,
            "amount": amount,
            "category": category,
            "payment_mode": payment,
            "date": f"2024-{month:02d}-{day:02d}"
        })

df = pd.DataFrame(records).sample(frac=1).reset_index(drop=True)
df.to_csv("data/expenses_dataset.csv", index=False)
print(f"✅ Generated {len(df)} records")
print(df["category"].value_counts())