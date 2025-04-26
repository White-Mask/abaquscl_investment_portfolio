import datetime

import pandas as pd

from ..portfolios.models import (Amount, Asset, Portfolio, Price, Quantity,
                                 Weight)


def process_excel_file(file_path, user_id, initial_amount=1000000000):
    weights_df = pd.read_excel(file_path, sheet_name=0)
    prices_df = pd.read_excel(file_path, sheet_name=1)

    # Renombrar columnas
    weights_df.columns.values[0] = "date"
    weights_df.columns.values[1] = "asset"
    weights_df.columns.values[2] = "portfolio_1"
    weights_df.columns.values[3] = "portfolio_2"
    prices_df.columns.values[0] = "date"

    weights_df["date"] = pd.to_datetime(weights_df["date"]).dt.date
    prices_df["date"] = pd.to_datetime(prices_df["date"]).dt.date

    v0 = initial_amount

    # Create assets
    asset_symbols = weights_df["asset"].unique()
    assets = [Asset(symbol=symbol, name=symbol) for symbol in asset_symbols]
    Asset.objects.bulk_create(assets)
    asset_map = {a.symbol: a for a in Asset.objects.all()}
    print(f"Assets created: {asset_map}")

    # Create portfolios
    portfolio_names = weights_df.columns[2:]
    portfolios = [Portfolio(user_id=user_id, name=name, created_at=datetime.date.today(), currency="USD") for name in portfolio_names]
    Portfolio.objects.bulk_create(portfolios)
    portfolio_map = {p.name: p for p in Portfolio.objects.all()}

    # Create prices
    try:
        price_entries = []
        for _, row in prices_df.iterrows():
            for asset_name in asset_symbols:
                price_entries.append(Price(
                    asset=asset_map[asset_name],
                    date=row["date"],
                    price=row[asset_name]
                ))
        Price.objects.bulk_create(price_entries)
    except Exception as e:
        print(f"Error creating prices: {e}")

    # Create weights, quantities, and amounts
    weight_entries = []
    quantity_entries = []
    amount_entries = []
    for _, row in weights_df.iterrows():
        asset = asset_map[row["asset"]]
        date = row["date"]
        for name in portfolio_names:
            portfolio = portfolio_map[name]
            weight = row[name]
            price = Price.objects.get(asset=asset, date=date).price
            quantity = (weight * v0) / price
            amount = weight * v0

            weight_entries.append(Weight(portfolio=portfolio, asset=asset, weight=weight, date=date))
            quantity_entries.append(Quantity(portfolio=portfolio, asset=asset, quantity=quantity, date=date))
            amount_entries.append(Amount(portfolio=portfolio, asset=asset, amount=amount, date=date))

    Weight.objects.bulk_create(weight_entries)
    Quantity.objects.bulk_create(quantity_entries)
    Amount.objects.bulk_create(amount_entries)