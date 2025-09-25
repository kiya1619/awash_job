# accounts/views.py
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from awash.models import Employee, Job
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
def get_employee(request):
    emp_id = request.GET.get("employee_id")
    try:
        employee = Employee.objects.get(employee_id=emp_id)
        # Check if the corresponding User exists
        is_registered = employee.is_registered and User.objects.filter(username=employee.employee_id).exists()

        return JsonResponse({
            "full_name": employee.full_name,
            "department": employee.department,
            "email": employee.email,
            "is_registered": is_registered
        })
    except Employee.DoesNotExist:
        return JsonResponse({"error": "not_found"})
def home(request):
    return render(request, "awash/home.html")

def register(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        phone = request.POST.get("phone")

        # Check password match
        if password1 != password2:
            return render(request, "awash/register.html", {"error": "Passwords do not match"})

        # Get employee
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return render(request, "awash/register.html", {"error": "Employee not found. Please contact HR."})

        # Reset is_registered if User deleted
        if employee.is_registered and not User.objects.filter(username=employee.employee_id).exists():
            employee.is_registered = False
            employee.save()

        # Check if already registered
        if employee.is_registered:
            return render(request, "awash/register.html", {"error": "This employee is already registered. Contact HR."})

        # Create Django user
        user = User.objects.create_user(
            username=employee.employee_id,
            first_name=employee.full_name.split(" ")[0],
            last_name=" ".join(employee.full_name.split(" ")[1:]),
            password=password1
        )

        # Save phone if entered and not already present
        if phone and not employee.phone:
            employee.phone = phone

        # Mark employee as registered
        employee.user = user
        employee.is_registered = True
        employee.save()

        return redirect("login")

    return render(request, "awash/register.html")
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages

def login_user(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        user = authenticate(request, username=employee_id, password=password)
        if user:
            login(request, user)

            # Redirect based on user type
            if user.is_staff:
                return redirect("hr_dashboard")       # HR dashboard
            else:
                return redirect("employee_dashboard") # Employee dashboard
        else:
            messages.error(request, "Invalid Employee ID or password")

    return render(request, "awash/login.html")


def employee_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    try:
        employee = Employee.objects.get(employee_id=request.user.username)
    except Employee.DoesNotExist:
        employee = None  # or handle the error

    return render(request, "awash/employee_dashboard.html", {"employee": employee})
def logout_user(request):
    logout(request)
    return redirect("login")


def hr_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("login")

    employees = Employee.objects.all()
    job = Job.objects.all()
    active_jobs = Job.objects.filter(is_active=True).count()
    inactive_jobs = Job.objects.filter(is_active=False).count()
    recent_jobs = Job.objects.all().order_by("-posted_date")[:5]
    context = {
        "employees": employees,
        "job": job,
        "active_jobs": active_jobs,
        "inactive_jobs": inactive_jobs,
        "recent_jobs": recent_jobs,
    }
    return render(request, "awash/hr_dashboard.html", context)


def post_job(request):
    if request.method == "POST":
        # Basic fields
        title = request.POST.get("title")
        deadline = request.POST.get("deadline")
        is_active = request.POST.get("is_active") == "on"

        # New fields
        job_description = request.POST.get("description")
        qualification = request.POST.get("qualification")
        experience = request.POST.get("experience")
        employment_type = request.POST.get("employment_type")
        job_category = request.POST.get("job_category")
        duty_station = request.POST.get("duty_station")
        job_grade = request.POST.get("job_grade")
        vacancy_type = request.POST.get("vacancy_type")

        # Create Job — vacancy_number is auto-generated in the model
        job = Job.objects.create(
            title=title,
            deadline=deadline,
            is_active=is_active,
            description=job_description,
            qualification=qualification,
            experience=experience,
            employment_type=employment_type,
            job_category=job_category,
            duty_station=duty_station,
            job_grade=job_grade,
            vacancy_type=vacancy_type,
        )

        messages.success(
            request,
            f"Job '{job.title}' posted successfully with Vacancy No: {job.vacancy_number}"
        )
        return redirect("post_job")

    return render(request, "awash/post_job.html")

def all_jobs(request):
    jobs = Job.objects.all().order_by("-posted_date")
    return render(request, "awash/all_jobs.html", {"jobs": jobs})
def view_detail(request, id):
    try:
        job = Job.objects.get(id=id)
    except Job.DoesNotExist:
        job = None  # or handle the error

    return render(request, "awash/view_detail.html", {"job": job})