from django import forms

from ..portfolios.models import Asset, Portfolio


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Archivo Excel (.xlsx)")


class TradeSimulationForm(forms.Form):
    portfolio = forms.ModelChoiceField(queryset=Portfolio.objects.all(), label="Portfolio")
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    sell_asset = forms.ModelChoiceField(queryset=Asset.objects.all(), label="Asset to sell")
    buy_asset = forms.ModelChoiceField(queryset=Asset.objects.all(), label="Asset to buy")
    amount = forms.FloatField(min_value=1, label="Amount in USD")
