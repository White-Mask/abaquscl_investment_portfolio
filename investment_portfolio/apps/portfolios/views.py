from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from apps.portfolios.models import (Amount, Asset, HoldingSnapshot, Portfolio,
                                    PortfolioEvent, PortfolioValue, Price,
                                    Quantity, Weight)
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView


class PortfolioEvolutionAPIView(APIView):
    def get(self, request, pk):
        fecha_inicio = request.query_params.get("startDate")
        fecha_fin = request.query_params.get("dateEnd")

        # Validaciones
        if not fecha_inicio or not fecha_fin:
            return Response({"error": "Missing fecha_inicio or fecha_fin"}, status=400)

        try:
            start = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            end = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        if start > end:
            return Response({"error": "fecha_inicio cannot be after fecha_fin"}, status=400)

        portfolio = get_object_or_404(Portfolio, pk=pk)

        # Obtener las cantidades c_{i,0} desde el snapshot inicial
        initial_snapshots = HoldingSnapshot.objects.filter(
            portfolio=portfolio, date=start)
        if not initial_snapshots.exists():
            return Response({"error": f"No snapshot data found for {start}"}, status=404)

        cantidades = {s.asset_id: Decimal(s.quantity)
                      for s in initial_snapshots}

        # Obtener precios en el rango
        prices_qs = Price.objects.filter(
            asset_id__in=cantidades.keys(),
            date__range=(start, end)
        ).order_by("date")

        precios_por_fecha = defaultdict(dict)
        for p in prices_qs:
            precios_por_fecha[p.date][p.asset_id] = Decimal(p.price)

        # Calcular evolución
        resultado = []
        for fecha in sorted(precios_por_fecha.keys()):
            total_valor = Decimal("0")
            xit = {}

            for asset_id, cantidad in cantidades.items():
                precio = precios_por_fecha[fecha].get(asset_id)
                if precio:
                    valor = cantidad * precio
                    xit[asset_id] = valor
                    total_valor += valor

            if total_valor > 0:
                weights = {
                    Asset.objects.get(pk=aid).name: round(
                        float(x / total_valor), 6)
                    for aid, x in xit.items()
                }

                resultado.append({
                    "date": fecha,
                    "V_t": round(float(total_valor), 2),
                    "weights": weights
                })

        return Response(resultado, status=200)


class PortfolioWeightsItemSerializer(serializers.Serializer):
    date = serializers.DateField()
    V_t = serializers.FloatField()
    weights = serializers.DictField(child=serializers.FloatField())


@extend_schema(
    tags=["Portfolio Weights"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID of the portfolio to analyze"
        ),
        OpenApiParameter(
            name="fecha_inicio",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Start date of the time window (format: YYYY-MM-DD)"
        ),
        OpenApiParameter(
            name="fecha_fin",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="End date of the time window (format: YYYY-MM-DD)"
        )
    ],
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date", "example": "2022-05-15"},
                    "V_t": {"type": "number", "example": 3303.34},
                    "weights": {
                        "type": "object",
                        "additionalProperties": {"type": "number"},
                        "example": {
                            "USA": 0.23,
                            "Europe": 0.27,
                            "UK": 0.05,
                            "Asia": 0.10,
                            "Cash": 0.35
                        }
                    }
                }
            },
            "description": "Portfolio daily evolution with total value (V_t) and normalized asset weights (w_{i,t})"
        },
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
    description="📊 Returns the portfolio value (V_t) and the weights (w_{i,t}) of each asset between the given dates, assuming constant asset quantities since portfolio creation."
)
class PortfolioWeightsAPIView(APIView):
    def get(self, request, pk):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")

        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            return Response({"error": "Debe proporcionar fecha_inicio y fecha_fin como parámetros"}, status=400)
        try:
            start = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            end = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Fechas inválidas. Use formato YYYY-MM-DD"}, status=400)
        if start > end:
            return Response({"error": "fecha_inicio no puede ser posterior a fecha_fin"}, status=400)

        portfolio = get_object_or_404(Portfolio, pk=pk)

        # Obtener pesos
        weights_qs = Weight.objects.filter(
            portfolio=portfolio).select_related("asset")
        if not weights_qs.exists():
            return Response({"error": "No hay pesos asociados al portafolio"}, status=404)

        # Mapear asset_id a nombre
        asset_name_map = {w.asset.id: w.asset.name for w in weights_qs}

        # Precios iniciales
        initial_prices = {
            p.asset_id: Decimal(p.price)
            for p in Price.objects.filter(date=start, asset_id__in=asset_name_map.keys())
        }

        # Calcular V0
        V0 = sum(
            Decimal(w.weight) * initial_prices.get(w.asset_id, Decimal(0))
            for w in weights_qs if w.asset_id in initial_prices
        )
        if V0 == 0:
            return Response({"error": "No se pudo calcular V0 (precios faltantes para fecha inicial)"}, status=400)

        # Cantidades c_{i,0}
        cantidades = {
            w.asset_id: (Decimal(w.weight) * V0) / initial_prices[w.asset_id]
            for w in weights_qs if w.asset_id in initial_prices
        }

        # Precios en rango
        precios_qs = Price.objects.filter(
            asset_id__in=cantidades.keys(),
            date__range=(start, end)
        ).values("asset_id", "date", "price")

        # Agrupar precios por fecha
        precios_por_fecha = {}
        for p in precios_qs:
            fecha = p["date"]
            if fecha not in precios_por_fecha:
                precios_por_fecha[fecha] = {}
            precios_por_fecha[fecha][p["asset_id"]] = Decimal(p["price"])

        # Construir evolución
        resultado = []
        for fecha in sorted(precios_por_fecha.keys()):
            total_valor = Decimal("0")
            xit = {}

            for asset_id, cantidad in cantidades.items():
                precio = precios_por_fecha[fecha].get(asset_id)
                if precio:
                    x = cantidad * precio
                    xit[asset_id] = x
                    total_valor += x

            if total_valor > 0:
                row = {
                    "date": fecha,
                    "V_t": round(float(total_valor), 2),
                    "weights": {
                        asset_name_map[aid]: round(float(x / total_valor), 6)
                        for aid, x in xit.items()
                    }
                }
                resultado.append(row)

        return Response(resultado)


@extend_schema(
    tags=["Portfolio Value"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID of the portfolio"
        ),
        OpenApiParameter(
            name="fecha_inicio",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Start date of the time window (format: YYYY-MM-DD)"
        ),
        OpenApiParameter(
            name="fecha_fin",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="End date of the time window (format: YYYY-MM-DD)"
        )
    ],
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date", "example": "2022-05-15"},
                    "portfolio": {"type": "string", "example": "portfolio_1"},
                    "total_value": {"type": "number", "example": 1000000000.00},
                    "weights": {
                        "type": "object",
                        "additionalProperties": {"type": "number"},
                        "example": {
                            "Asset A": 0.25,
                            "Asset B": 0.75
                        }
                    }
                }
            },
            "description": "List of daily portfolio values (V_t) and asset weights (w_{i,t}) for the given portfolio and date range."
        },
        400: OpenApiTypes.OBJECT
    },
    description="📈 Returns the total portfolio value (V_t) and asset weights (w_{i,t}) for each day in the selected date range."
)
class PortfolioValueAPIView(APIView):
    def get(self, request, pk):
        try:
            # Paso 1: Obtener parámetros de la solicitud
            date_start = request.query_params.get('dateStart')
            date_end = request.query_params.get('dateEnd')

            # Validar fechas
            date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

            # Obtener portafolio y activos
            portfolio = Portfolio.objects.get(id=pk)
            assets = Asset.objects.filter(
                weight__portfolio=portfolio).distinct()

            # Obtener todas las fechas en el rango
            dates = [date_start + timedelta(days=x)
                     for x in range((date_end - date_start).days + 1)]
            valid_dates = []
            for date in dates:
                if Price.objects.filter(asset__in=assets, date=date).count() == assets.count():
                    valid_dates.append(date)

            # Paso 2: Calcular cantidades iniciales
            initial_date = datetime(2022, 2, 15).date()
            initial_prices = {
                p.asset_id: p.price for p in Price.objects.filter(
                    asset__in=assets,
                    date=initial_date
                )
            }
            weights = {
                w.asset_id: w.weight for w in Weight.objects.filter(
                    portfolio=portfolio,
                    date=initial_date
                )
            }

            # Validar que los pesos sumen 1
            weights_sum = sum(weights.values())
            if weights_sum != 1:
                return Response({"error": "Los pesos iniciales no suman 1"}, status=status.HTTP_400_BAD_REQUEST)

            V0 = 1_000_000_000  # Valor inicial del portafolio
            quantities = {}
            for asset in assets:
                price = initial_prices.get(asset.id, 0)
                weight = weights.get(asset.id, 0)
                if price > 0:
                    quantities[asset.id] = (weight * V0) / price
                else:
                    quantities[asset.id] = 0

            # Paso 3: Procesar cada fecha válida
            result = []
            for date in valid_dates:
                # Obtener precios para todos los activos en esta fecha
                prices = {
                    asset.id: Price.objects.filter(
                        asset=asset, date=date).first().price
                    if Price.objects.filter(asset=asset, date=date).exists()
                    else 0
                    for asset in assets
                }

                # Procesar eventos de compra/venta para actualizar cantidades
                events = PortfolioEvent.objects.filter(
                    portfolio=portfolio,
                    date__lte=date
                ).order_by("date")

                for event in events:
                    if event.type == PortfolioEvent.EventType.BUY:
                        price = prices.get(event.asset_id, 0)
                        if price > 0:
                            quantities[event.asset_id] += event.amount / price
                    elif event.type == PortfolioEvent.EventType.SELL:
                        price = prices.get(event.asset_id, 0)
                        if price > 0 and quantities[event.asset_id] >= event.amount / price:
                            quantities[event.asset_id] -= event.amount / price

                # Calcular x_it y V_t
                total_value = 0
                x_it_values = {}
                for asset in assets:
                    quantity = quantities.get(asset.id, 0)
                    price = prices.get(asset.id, 0)
                    x_it = quantity * price
                    x_it_values[asset.id] = x_it
                    total_value += x_it

                # Calcular w_it
                weights_t = {}
                if total_value > 0:
                    for asset in assets:
                        x_it = x_it_values.get(asset.id, 0)
                        weights_t[asset.name] = x_it / total_value
                else:
                    for asset in assets:
                        weights_t[asset.name] = 0

                # Agregar resultado
                result.append({
                    'date': date,
                    'portfolio_value': total_value,
                    'weights': weights_t
                })

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Portfolio Trade"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID of the portfolio to simulate the trade in"
        ),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "example": "2022-05-15",
                    "description": "Trade date (YYYY-MM-DD)"
                },
                "sell_asset_symbol": {
                    "type": "string",
                    "example": "EEUU",
                    "description": "Asset symbol to sell"
                },
                "buy_asset_symbol": {
                    "type": "string",
                    "example": "Europa",
                    "description": "Asset symbol to buy"
                },
                "amount": {
                    "type": "number",
                    "example": 200000000,
                    "description": "Amount in USD for the trade"
                }
            },
            "required": ["date", "sell_asset_symbol", "buy_asset_symbol", "amount"]
        }
    },
    responses={
        201: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date", "example": "2022-05-15"},
                    "V_t": {"type": "number", "example": 3303.34},
                    "weights": {
                        "type": "object",
                        "additionalProperties": {"type": "number"},
                        "example": {
                            "EEUU": -130.683877,
                            "Europa": 131.682486,
                            "UK": 0.00005
                        }
                    }
                }
            },
            "description": "Daily evolution after the trade including total value (V_t) and asset weights (w_{i,t})"
        },
        400: OpenApiTypes.OBJECT
    },
    description=(
        "💱 Simulates a trade by selling and buying assets in a portfolio on a specific date. "
        "Returns the portfolio evolution over time (V_t and w_{i,t}) for the following days."
    )
)
class TradeSimulationAPIView(APIView):
    def post(self, request, pk):
        try:
            # Paso 1: Obtener datos del request
            data = request.data
            transaction_date = datetime.strptime(
                data["date"], "%Y-%m-%d").date()
            sell_asset_symbol = data["sell_asset_symbol"]
            buy_asset_symbol = data["buy_asset_symbol"]
            amount = Decimal(str(data["amount"]))

            # Paso 2: Validar y obtener entidades relacionadas
            try:
                sell_asset = Asset.objects.get(symbol=sell_asset_symbol)
                buy_asset = Asset.objects.get(symbol=buy_asset_symbol)
                portfolio = Portfolio.objects.get(pk=pk)

                # Buscar el precio más reciente antes o en la fecha de la transacción
                sell_price_record = Price.objects.filter(
                    asset=sell_asset, date__lte=transaction_date
                ).order_by("-date").first()

                buy_price_record = Price.objects.filter(
                    asset=buy_asset, date__lte=transaction_date
                ).order_by("-date").first()

                if not sell_price_record or not buy_price_record:
                    return Response(
                        {"error": "No se encontraron precios históricos para los activos"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                sell_price = sell_price_record.price  # Extraer el valor numérico
                buy_price = buy_price_record.price    # Extraer el valor numérico

            except (Portfolio.DoesNotExist, Asset.DoesNotExist) as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Paso 3: Registrar la transacción
            # Evento de venta
            PortfolioEvent.objects.create(
                portfolio=portfolio,
                asset=sell_asset,
                type=PortfolioEvent.EventType.SELL,
                amount=amount,
                price=sell_price,
                date=transaction_date,
                currency="USD"
            )

            # Evento de compra
            PortfolioEvent.objects.create(
                portfolio=portfolio,
                asset=buy_asset,
                type=PortfolioEvent.EventType.BUY,
                amount=amount,
                price=buy_price,
                date=transaction_date,
                currency="USD"
            )

            # Paso 4: Actualizar las cantidades
            # Calcular la cantidad adquirida del activo comprado
            buy_quantity = amount / Decimal(buy_price)

            # Obtener o crear la cantidad del activo comprado
            quantity_record, created = Quantity.objects.get_or_create(
                portfolio=portfolio,
                asset=buy_asset,
                date=transaction_date,
                defaults={"quantity": buy_quantity}
            )
            if not created:
                quantity_record.quantity = Decimal(
                    quantity_record.quantity) + Decimal(buy_quantity)
                quantity_record.save()

            # Paso 5: Calcular el nuevo historial
            # Obtener todas las cantidades y precios del portafolio
            quantities = Quantity.objects.filter(
                portfolio=portfolio, date__gte=transaction_date)
            total_value = Decimal(0)

            for q in quantities:
                price_record = Price.objects.filter(
                    asset=q.asset, date__lte=transaction_date
                ).order_by("-date").first()

                if not price_record:
                    return Response(
                        {"error": f"No se encontró un precio para el activo {q.asset.symbol}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                asset_price = price_record.price
                monetary_value = Decimal(q.quantity) * Decimal(asset_price)
                total_value += monetary_value

                # Actualizar Amount
                Amount.objects.update_or_create(
                    portfolio=portfolio,
                    asset=q.asset,
                    date=transaction_date,
                    defaults={"amount": monetary_value}
                )

            # Calcular pesos y actualizar Weight
            for q in quantities:
                price_record = Price.objects.filter(
                    asset=q.asset, date__lte=transaction_date
                ).order_by("-date").first()

                if not price_record:
                    return Response(
                        {"error": f"No se encontró un precio para el activo {q.asset.symbol}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                asset_amount = Amount.objects.get(
                    portfolio=portfolio, asset=q.asset, date=transaction_date).amount
                weight = Decimal(asset_amount) / \
                    total_value if total_value > 0 else Decimal(0)
                Weight.objects.update_or_create(
                    portfolio=portfolio,
                    asset=q.asset,
                    date=transaction_date,
                    defaults={"weight": weight}
                )

            # Actualizar PortfolioValue
            PortfolioValue.objects.update_or_create(
                portfolio=portfolio,
                date=transaction_date,
                defaults={"value": total_value}
            )

            # Respuesta exitosa
            return Response({"message": "Transacción procesada correctamente"}, status=status.HTTP_200_OK)

        except Portfolio.DoesNotExist:
            return Response({"error": "Portafolio no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
        except Asset.DoesNotExist:
            return Response({"error": "Activo no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
        except Price.DoesNotExist:
            return Response({"error": "Precio no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
