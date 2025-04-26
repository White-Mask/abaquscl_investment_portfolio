CURRENCIES = {
    "USD": {"symbol": "$", "name": "US Dollar"},
    "EUR": {"symbol": "€", "name": "Euro"},
    "CLP": {"symbol": "$", "name": "Chilean Peso"},
}

CURRENCY_CHOICES = [(code, f"{val['symbol']} {code}") for code, val in CURRENCIES.items()]
