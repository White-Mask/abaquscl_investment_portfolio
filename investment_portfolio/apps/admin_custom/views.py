import tempfile

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from ..portfolios.models import Portfolio
from .utils import process_excel_file
from .forms import ExcelUploadForm, TradeSimulationForm


@login_required
def pre_weights_chart_view(request):
    # Obtener los portafolios del usuario logeado
    portfolios = Portfolio.objects.filter(user=request.user)

    if not portfolios.exists():
        messages.error(request, "No tienes portafolios disponibles.")
        return redirect("admin:index")  # Redirige al índice del admin si no hay portafolios

    # Renderizar la plantilla con la lista de portafolios
    return render(request, "admin/pre_weights_chart.html", {"portfolios": portfolios})


def weights_chart_view(request, pk):    
    fecha_inicio = request.GET.get("dateStart", "2022-02-15")
    fecha_fin = request.GET.get("dateEnd", "2023-02-15")

    print(request)

    # Construcción del endpoint local
    api_url = f"http://localhost:8000/portfolios/v1/portfolios/{pk}/value/?dateStart={fecha_inicio}&dateEnd={fecha_fin}"

    try:
        response = requests.get(api_url, timeout=100)
        response.raise_for_status()
        data = response.json()

        if not data:
            messages.warning(request, "No hay datos disponibles para las fechas seleccionadas.")
            return render(request, "admin/weights_chart.html", {"chart_data": {}})

        # Preparar datos
        fechas = [item["date"] for item in data]
        vt = [item["portfolio_value"] for item in data]

        # Agrupar pesos por activo
        pesos_por_activo = {}
        for item in data:
            for activo, peso in item["weights"].items():
                pesos_por_activo.setdefault(activo, []).append(round(peso*100, 2))

        chart_data = {
            "dates": fechas,
            "vt": vt,
            "weights": pesos_por_activo
        }

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al conectar con el API: {e}")
        chart_data = {"dates": [], "vt": [], "weights": {}}

    return render(request, "admin/weights_chart.html", {"chart_data": chart_data})

def trade_simulation_view(request):
    if request.method == "POST":
        form = TradeSimulationForm(request.POST)
        if form.is_valid():
            pk = form.cleaned_data["portfolio"].id
            date = form.cleaned_data["date"]
            sell_asset = form.cleaned_data["sell_asset"]
            buy_asset = form.cleaned_data["buy_asset"]
            amount = form.cleaned_data["amount"]

            # Llama a la API interna
            url = f"http://localhost:8000/portfolios/v1/portfolios/{pk}/trade/"
            payload = {
                "date": date.strftime("%Y-%m-%d"),
                "sell_asset_symbol": sell_asset.symbol,
                "buy_asset_symbol": buy_asset.symbol,
                "amount": amount,
            }

            try:
                response = requests.post(url, json=payload)

                if response.status_code in [200, 201]:
                    messages.success(request, "Trade simulation successful.")
                    return redirect(f"/admin/")
                else:
                    try:
                        error_data = response.json()
                        error_message = error_data.get("error", "Unknown error")
                    except ValueError:
                        error_message = response.text

                    messages.error(request, f"Error: {response.status_code} - {error_message}")
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to the API: {e}")
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = TradeSimulationForm()

    return render(request, "admin/trade_simulation.html", {"form": form})


def upload_excel_view(request):
    # Verificar permisos del usuario autenticado
    if not request.user.has_perm("portfolios.add_portfolio"):
        messages.error(request, "❌ No tienes permisos para cargar archivos.")
        return redirect("/admin/")

    # Obtener todos los usuarios para el dropdown
    users = User.objects.all()

    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)

        # Obtener el ID del usuario seleccionado
        selected_user_id = request.POST.get("user")
        initial_amount = request.POST.get("initial_amount")  # Capturar el monto inicial

        if not selected_user_id:
            messages.error(request, "❌ Debes seleccionar un usuario.")
            return redirect("/admin/upload-excel/")

        if not initial_amount or float(initial_amount) <= 0:
            messages.error(request, "❌ El monto inicial debe ser mayor a 0.")
            return redirect("/admin/upload-excel/")

        if form.is_valid():
            excel_file = request.FILES["file"]

            # Guardar el archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in excel_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                # Procesar el archivo Excel con el ID del usuario seleccionado y el monto inicial
                process_excel_file(tmp_path, user_id=selected_user_id, initial_amount=float(initial_amount))
                messages.success(request, "✅ Archivo procesado correctamente.")
                return redirect("/admin/")
            except Exception as e:
                messages.error(request, f"❌ Error al procesar: {str(e)}")
    else:
        form = ExcelUploadForm()

    # Renderizar el formulario con la lista de usuarios
    return render(request, "admin/upload_excel.html", {"form": form, "users": users})