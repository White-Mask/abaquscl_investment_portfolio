from rest_framework import serializers

from .models import (Asset, HoldingSnapshot, Portfolio, PortfolioEvent,
                     PortfolioValue, Price, Weight)


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = "__all__"


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"


class PriceSerializer(serializers.ModelSerializer):
    asset = serializers.StringRelatedField()

    class Meta:
        model = Price
        fields = "__all__"


class WeightSerializer(serializers.ModelSerializer):
    portfolio = serializers.StringRelatedField()
    asset = serializers.StringRelatedField()
    total_value = serializers.FloatField(source="portfolio.total_value", read_only=True)
    date = serializers.DateField()

    class Meta:
        model = Weight
        fields = "__all__"


class PortfolioEventSerializer(serializers.ModelSerializer):
    portfolio = serializers.StringRelatedField()
    asset = serializers.StringRelatedField()

    class Meta:
        model = PortfolioEvent
        fields = "__all__"


class HoldingSnapshotSerializer(serializers.ModelSerializer):
    portfolio = serializers.StringRelatedField()
    asset = serializers.StringRelatedField()

    class Meta:
        model = HoldingSnapshot
        fields = "__all__"


class PortfolioValueSerializer(serializers.ModelSerializer):
    portfolio = serializers.StringRelatedField()

    class Meta:
        model = PortfolioValue
        fields = "__all__"
