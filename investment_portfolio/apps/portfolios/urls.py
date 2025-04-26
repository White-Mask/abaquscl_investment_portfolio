from django.urls import path
from apps.portfolios.views import (
    PortfolioValueAPIView,
    TradeSimulationAPIView,
)

PREFIX = "portfolios/"
VERSION = "v1/"


urlpatterns = [
    path(f"{VERSION}{PREFIX}<int:pk>/value/", PortfolioValueAPIView.as_view(), name="portfolio-value"),
    path(f"{VERSION}{PREFIX}<int:pk>/trade/", TradeSimulationAPIView.as_view(), name="portfolio-trade"),
]
