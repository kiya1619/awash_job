import os
import django
import pandas as pd

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_application.settings')  # replace 'yourproject' with your project name
django.setup()

from awash.models import Allemployee_record  # replace 'yourapp' with your app name

# Load the Excel file
df = pd.read_excel('employees.xlsx')  # ensure the path is correct

# Loop through rows and insert
for index, row in df.iterrows():
    employee_id = str(row['employee_id']).strip()
    full_name = str(row['full_name']).strip()

    obj, created = Allemployee_record.objects.get_or_create(
        employee_id=employee_id,
        defaults={'full_name': full_name}
    )
    if created:
        print(f"Created: {employee_id} - {full_name}")
    else:
        print(f"Skipped (already exists): {employee_id}")
