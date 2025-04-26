from django.core.management.base import BaseCommand

from apps.admin_custom.utils import process_excel_file


class Command(BaseCommand):
    help = "Procesa un archivo Excel y carga los datos en la base de datos."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Ruta al archivo Excel")
        parser.add_argument("user_id", type=int, help="ID del usuario")
        parser.add_argument("--initial-amount", type=float, default=1000000000, help="Monto inicial del portafolio")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        user_id = kwargs["user_id"]
        initial_amount = kwargs["initial_amount"]

        self.stdout.write(f"Procesando archivo: {file_path}")
        self.stdout.write(f"Usuario ID: {user_id}")
        self.stdout.write(f"Monto inicial: {initial_amount}")

        try:
            process_excel_file(file_path, user_id, initial_amount)
            self.stdout.write(self.style.SUCCESS("✅ Archivo procesado correctamente."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error al procesar el archivo: {e}"))