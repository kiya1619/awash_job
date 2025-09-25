from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True)  # e.g. AIB/20821/2022
    full_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)  # For notifications
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_registered = models.BooleanField(default=False)  # Track if employee has created account

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
class Job(models.Model):
    title = models.CharField(max_length=200)
    vacancy_number = models.CharField(max_length=30, unique=True, editable=False)
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)

    # New fields
    description = models.TextField(blank=True)
    qualification = models.TextField(blank=True)
    experience = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(max_length=100, blank=True)  # e.g., Full-time, Part-time
    job_category = models.CharField(max_length=100, blank=True)
    duty_station = models.CharField(max_length=100, blank=True)
    job_grade = models.CharField(max_length=50, blank=True)
    vacancy_type_choices = [
        ('internal', 'Internal'),
        ('external', 'External')
    ]
    vacancy_type = models.CharField(max_length=10, choices=vacancy_type_choices, default='external')

    def __str__(self):
        return f"{self.vacancy_number} — {self.title}"

    def save(self, *args, **kwargs):
        """
        Two-step save:
        1. Initial save to get PK.
        2. Build vacancy_number as VAC-<year>-<pk zero-padded>.
        3. Use update() to avoid recursion.
        """
        if not self.pk:
            super().save(*args, **kwargs)  # Step 1
            year = timezone.now().year
            self.vacancy_number = f"VAC-{year}-{self.pk:06d}"  # Step 2
            Job.objects.filter(pk=self.pk).update(vacancy_number=self.vacancy_number)  # Step 3
        else:
            super().save(*args, **kwargs)