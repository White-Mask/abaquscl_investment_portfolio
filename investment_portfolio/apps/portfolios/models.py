from apps.common.constants import CURRENCY_CHOICES
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Asset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=100, unique=True, null=True, blank=True)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default="USD")

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=100)
    created_at = models.DateField()
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default="USD")

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Price(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField(db_index=True)
    price = models.FloatField()

    class Meta:
        unique_together = ("asset", "date")

    def __str__(self):
        return f"{self.asset.symbol or self.asset.name} - {self.date} = {self.price}"


class Weight(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="weights")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = ("portfolio", "asset", "date")

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.name} ({self.date}): {self.weight}"
    

class Quantity(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="quantities")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = ("portfolio", "asset", "date")

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.name} ({self.date}): {self.quantity}"


class Amount(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="amounts")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = ("portfolio", "asset", "date")

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.name} ({self.date}): {self.amount}"


class PortfolioEvent(models.Model):
    class EventType(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"
        DEPOSIT = "deposit", "Deposit"

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="events")
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=EventType.choices)
    amount = models.FloatField(help_text="USD para buy/deposit, cantidad para sell")
    price = models.FloatField(null=True, blank=True)
    date = models.DateField()
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default="USD")

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} | {self.portfolio.name} {self.type.upper()} {self.asset}"


class HoldingSnapshot(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="snapshots")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    quantity = models.FloatField()

    class Meta:
        unique_together = ("portfolio", "asset", "date")

    def __str__(self):
        return f"{self.date} - {self.portfolio.name} - {self.asset.name}"


class PortfolioValue(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="values")
    date = models.DateField(db_index=True)
    value = models.FloatField()

    class Meta:
        unique_together = ("portfolio", "date")

    def __str__(self):
        return f"{self.date} - {self.portfolio.name}: ${self.value:,.2f}"
