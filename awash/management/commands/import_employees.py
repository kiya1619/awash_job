# employees/management/commands/import_employees.py
import pandas as pd
from django.core.management.base import BaseCommand
from awash.models import Employee

class Command(BaseCommand):
    help = "Import employees from Excel file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            Employee.objects.update_or_create(
                employee_id=row["employee_id"],
                defaults={
                    "full_name": row["full_name"],
                    "department": row.get("department", ""),
                    "email": row.get("email", ""),
                    "phone": row.get("phone", ""),
                }
            )
        self.stdout.write(self.style.SUCCESS("Employees imported successfully!"))
