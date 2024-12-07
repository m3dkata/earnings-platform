from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from datetime import timedelta
import random
from apps.accounts.models import CustomUser
from apps.employees.models import Employee, Workshop
from apps.operations.models import Operation, Rate
from apps.reports.models import Report, ReportOperation
from decimal import Decimal
from apps.payrolls.tasks import generate_payroll
from django.db import transaction

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def add_arguments(self, parser):
        parser.add_argument('--employees', type=int, default=30,
                           help='Number of employees to create')
        parser.add_argument('--days', type=int, default=90,
                           help='Number of days to generate data for')

    def handle(self, *args, **kwargs):
        fake = Faker()
        num_employees = kwargs['employees']
        days_back = kwargs['days']
        
        Report.objects.all().delete()
        Employee.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        Operation.objects.all().delete()
        Rate.objects.all().delete()
        Workshop.objects.all().delete()
        
        workshops = []
        for choice in Workshop.WORKSHOP_CHOICES:
            workshop = Workshop.objects.create(name=choice[0])
            workshops.append(workshop)

        rates = []
        rate_prices = [0.106, 0.100, 0.106, 0.100, 0.106, 0.100, 0.106, 0.100]
        for idx, choice in enumerate(Rate.CATEGORY_CHOICES):
            rate = Rate.objects.create(
                category=choice[0],
                price=Decimal(str(rate_prices[idx]))
            )
            rates.append(rate)

        OPERATION_NAMES = [
            "Drilling", "Milling", "Turning", "Grinding", "Welding", "Assembly",
            "Quality Control", "Cutting", "Polishing", "Threading", "Boring",
            "Surface Finishing", "Heat Treatment", "Coating", "Deburring",
            "Inspection", "Packaging", "Material Handling", "CNC Programming",
            "Maintenance", "Tool Setup", "Machine Setup", "Part Marking",
            "Sandblasting", "Painting", "Plating", "Anodizing", "Testing",
            "Calibration", "Documentation", "Material Preparation", "Cleaning",
            "Sorting", "Inventory Control", "Safety Checks", "Equipment Setup",
            "Process Monitoring", "Quality Sampling", "Machine Operation",
            "Component Assembly", "Sub-Assembly", "Final Assembly", "Packing",
            "Labeling", "Storage", "Distribution", "Shipping Preparation",
            "Quality Reporting", "Process Planning"
        ]

        operations = []
        for i in range(len(OPERATION_NAMES)):
            time_value = Decimal(str(round(random.uniform(0.250, 7.050), 2)))
            operation = Operation.objects.create(
                code=i+1,
                name=OPERATION_NAMES[i],
                time=time_value,
                price=Decimal('0'),
                category=random.choice(rates)
            )
            operations.append(operation)

        employees = []
        for i in range(num_employees):
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    username=f'employee{i}',
                    email=f'employee{i}@kidn3y.com',
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone_number=f'+{fake.msisdn()[1:]}',
                    is_employee=True
                )
                
                employee = Employee.objects.create(
                    user=user,
                    number=i+100,
                    position=random.choice(Employee.POSITION_CHOICES)[0],
                    workshop=random.choice(workshops)
                )
                employees.append(employee)

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days_back)
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() >= 5:
                print(f"Skipping weekend: {current_date}")
                current_date += timedelta(days=1)
                continue
                
            print(f"Generating reports for: {current_date}")
            for employee in employees:
                if random.random() < 0.8:
                    report = Report.objects.create(
                        employee=employee,
                        date=current_date,
                        status='APPROVED',
                    )
                    
                    operations_count = random.randint(1, 7)
                    print(f"Creating report for employee {employee.number} with {operations_count} operations")
                    
                    for _ in range(operations_count):
                        ReportOperation.objects.create(
                            report=report,
                            operation=random.choice(operations),
                            quantity=random.randint(100, 500)
                        )
                    
                    generate_payroll.delay(employee.id, current_date.strftime('%Y-%m-%d'))

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
