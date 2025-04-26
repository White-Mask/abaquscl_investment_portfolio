from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path

from ..portfolios.models import (Amount, Asset, HoldingSnapshot, Portfolio,
                                 PortfolioEvent, PortfolioValue, Price,
                                 Quantity, Weight)
from .views import (pre_weights_chart_view, trade_simulation_view,
                    upload_excel_view, weights_chart_view)


class PortfolioAdminSite(AdminSite):
    site_header = "Panel de Inversiones"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("cargar-excel/", self.admin_view(upload_excel_view),
                 name="cargar_excel"),
            path("graficos-pre-evolucion/",
                 self.admin_view(pre_weights_chart_view), name="pre_weights_chart"),
            path("graficos-evolucion/<int:pk>/",
                 self.admin_view(weights_chart_view), name="weights_chart"),
            path("graficos-trade/", self.admin_view(trade_simulation_view),
                 name="admin_trade_simulation"),
        ]
        return custom_urls + urls


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "currency")
    search_fields = ("name", "symbol")
    list_filter = ("currency",)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "currency")
    list_filter = ("created_at", "currency")
    search_fields = ("name", "user__username")


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("asset", "date", "price")
    list_filter = ("asset",)
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset", "weight", "date")
    list_filter = ("portfolio", "asset")
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset", "quantity", "date")
    list_filter = ("portfolio", "asset")
    ordering = ("-date",)
    date_hierarchy = "date"


@admin.register(Amount)
class AmountAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset", "amount")
    list_filter = ("portfolio", "asset")
    ordering = ("-date",)


@admin.register(PortfolioEvent)
class PortfolioEventAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "type", "asset", "amount", "price", "date")
    list_filter = ("portfolio", "type", "asset")
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(HoldingSnapshot)
class HoldingSnapshotAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset", "date", "quantity")
    list_filter = ("portfolio", "asset")
    date_hierarchy = "date"


@admin.register(PortfolioValue)
class PortfolioValueAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "date", "value")
    date_hierarchy = "date"
    ordering = ("-date",)


# ✅ Instancia del Admin personalizado
admin_site = PortfolioAdminSite(name="PortfolioAdmin")

# 🧾 Registro de modelos
admin_site.register(Asset, AssetAdmin)
admin_site.register(Portfolio, PortfolioAdmin)
admin_site.register(Price, PriceAdmin)
admin_site.register(Weight, WeightAdmin)
admin_site.register(Quantity, QuantityAdmin)
admin_site.register(Amount, AmountAdmin)
admin_site.register(PortfolioEvent, PortfolioEventAdmin)
admin_site.register(HoldingSnapshot, HoldingSnapshotAdmin)
admin_site.register(PortfolioValue, PortfolioValueAdmin)
