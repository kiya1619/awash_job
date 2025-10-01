# accounts/views.py
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from awash.models import Employee, Job, Application, Promotion, Allemployee_record
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from awash.utils.position_list import POSITION_LIST  # Import the position list
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
def get_employee(request):
    emp_id = request.GET.get("employee_id", "").strip()
    if not emp_id:
        return JsonResponse({"error": "not_found"})

    # Check Employee table
    try:
        emp = Employee.objects.get(employee_id=emp_id)

        # If Employee exists but User does not exist, allow registration
        if not emp.user or not User.objects.filter(username=emp.employee_id).exists():
            emp.is_registered = False
            emp.save()

        if emp.is_registered:
            return JsonResponse({"error": "already_registered"})
        else:
            return JsonResponse({
                "full_name": emp.full_name,
                "department": emp.position or "",
                "email": emp.email or "",
                "is_registered": False,
            })

    except Employee.DoesNotExist:
        # Check Allemployee_record
        try:
            record = Allemployee_record.objects.get(employee_id=emp_id)
            return JsonResponse({
                "full_name": record.full_name,
                "department": "",  # optional default
                "email": "",       # optional
                "is_registered": False,
            })
        except Allemployee_record.DoesNotExist:
            return JsonResponse({"error": "not_found"})

def home(request):
    return render(request, "awash/home.html")

def register(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id").strip()
        email = request.POST.get("email")
        position = request.POST.get("position")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "awash/register.html", {"error": "Passwords do not match", "positions": POSITION_LIST})

        try:
            record = Allemployee_record.objects.get(employee_id=employee_id)
        except Allemployee_record.DoesNotExist:
            return render(request, "awash/register.html", {"error": "Employee not found. Contact HR.", "positions": POSITION_LIST})

        # Check if Employee account already exists
        employee, created = Employee.objects.get_or_create(employee_id=employee_id, defaults={
            "full_name": record.full_name,
            "position": position,
            "email": email
        })

        if employee.is_registered:
            return render(request, "awash/register.html", {"has_account": True, "positions": POSITION_LIST})

        # Create Django User
        user = User.objects.create_user(
            username=employee.employee_id,
            email=email,
            password=password1,
            first_name=employee.full_name.split()[0],
            last_name=" ".join(employee.full_name.split()[1:])
        )

        employee.user = user
        employee.position = position
        employee.email = email
        employee.is_registered = True
        employee.save()

        return redirect("login")

    return render(request, "awash/register.html", {"positions": POSITION_LIST})
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
    jobs = Job.objects.all()
    active_jobs = Job.objects.filter(is_active=True).count()
    inactive_jobs = Job.objects.filter(is_active=False).count()
    recent_jobs = Job.objects.all().order_by("-posted_date")[:5]
    total_applications = Application.objects.count()

    # Promotion stats
    today = timezone.now().date()
    one_year_ago = today - timedelta(days=365)
    six_months_ago = today - timedelta(days=182)  # approx
    three_months_ago = today - timedelta(days=91)  # approx

    promotions = Promotion.objects.all()
    promoted_this_year = promotions.filter(promoted_at__gte=one_year_ago).count()
    promoted_last_6_months = promotions.filter(promoted_at__gte=six_months_ago).count()
    promoted_last_3_months = promotions.filter(promoted_at__gte=three_months_ago).count()

    context = {
        "employees": employees,
        "job": jobs,
        "active_jobs": active_jobs,
        "inactive_jobs": inactive_jobs,
        "recent_jobs": recent_jobs,
        "total_applications": total_applications,
        "promoted_this_year": promoted_this_year,
        "promoted_last_6_months": promoted_last_6_months,
        "promoted_last_3_months": promoted_last_3_months,
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
    applied_job_ids = []
    if request.user.is_authenticated:
        try:
            employee = request.user.employee  # Assuming OneToOne link
            applied_job_ids = Application.objects.filter(employee=employee).values_list('job_id', flat=True)
        except Employee.DoesNotExist:
            applied_job_ids = []
    context = {
        "jobs": jobs,
        "applied_job_ids": applied_job_ids
    }
    return render(request, "awash/all_jobs.html", context)
def view_detail(request, id):
    try:
        job = Job.objects.get(id=id)
    except Job.DoesNotExist:
        job = None  # or handle the error

    return render(request, "awash/view_detail.html", {"job": job})


def apply(request, id):
    job = get_object_or_404(Job, id=id)
    employee = Employee.objects.get(user=request.user)  # logged-in employee

    # 🔹 Check promotion eligibility before applying
    if not employee.can_apply():
        messages.error(request, "You cannot apply for this job because you were promoted within the last year.")
        return redirect("all_jobs")  # or job detail page

    if request.method == "POST":
        recommendation_letter = request.FILES.get("recommendation_letter")

        application, created = Application.objects.get_or_create(
            employee=employee,
            job=job,
            defaults={"recommendation_letter": recommendation_letter}
        )

        if not created:
            messages.warning(request, "You have already applied for this job.")
        else:
            messages.success(request, f"Application submitted for {job.title}!")

        return redirect("all_jobs")  # redirect to job list

    return render(request, "awash/apply.html", {"job": job})

def applicants_list(request):
    jobs = Job.objects.all().order_by("-posted_date")

    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to view this page.")
        return redirect("login")

    applications = Application.objects.select_related("employee", "job").all()
    
    context = {
        "jobs": jobs,
        "applications": applications,
    }
    return render(request, "awash/applicants.html", context) 

def view_applicants_per_job(request, id):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to view this page.")
        return redirect("login")

    job = get_object_or_404(Job, id=id)
    applications = Application.objects.filter(job=job).select_related("employee")

    context = {
        "job": job,
        "applications": applications,
    }
    return render(request, "awash/view_applicants_per_job.html", context)


def my_applications(request):
    if not request.user.is_authenticated:
        return redirect("login")

    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect("employee_dashboard")

    applications = Application.objects.filter(employee=employee).select_related("job").order_by("-applied_at")

    return render(request, "awash/my_applications.html", {"applications": applications})


def delete_job(request, id):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to perform this action.")
        return redirect("login")

    job = get_object_or_404(Job, id=id)
    job_title = job.title
    job.delete()
    messages.success(request, f"Job '{job_title}' has been deleted successfully.")
    return redirect("all_jobs")


def edit_job(request, id):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to perform this action.")
        return redirect("login")

    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        # Basic fields
        job.title = request.POST.get("title")
        job.deadline = request.POST.get("deadline")
        job.is_active = request.POST.get("is_active") == "on"

        # New fields
        job.description = request.POST.get("description")
        job.qualification = request.POST.get("qualification")
        job.experience = request.POST.get("experience")
        job.employment_type = request.POST.get("employment_type")
        job.job_category = request.POST.get("job_category")
        job.duty_station = request.POST.get("duty_station")
        job.job_grade = request.POST.get("job_grade")
        job.vacancy_type = request.POST.get("vacancy_type")

        job.save()
        messages.success(request, f"Job '{job.title}' updated successfully.")
        return redirect("all_jobs")

    return render(request, "awash/edit_job.html", {"job": job})


def all_users(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to view this page.")
        return redirect("login")

    employees = Employee.objects.select_related("user").all().order_by("full_name")
    users = User.objects.all()  # rename variable to 'users' to avoid confusion

    context = {
        "employees": employees,
        "users": users,
    }
    return render(request, "awash/users.html", context)
def delete_user(request, id):
    user_to_delete = get_object_or_404(User, id=id)
    
    # Check if this user has a linked Employee record
    try:
        employee = Employee.objects.get(user=user_to_delete)
        employee.delete()  # delete the employee record
    except Employee.DoesNotExist:
        pass  # no linked employee, continue

    username = user_to_delete.username
    user_to_delete.delete()  # delete the user
    messages.success(request, f"User '{username}' and linked employee record (if any) have been deleted successfully.")

    return redirect("users")

def promotion(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to perform this action.")
        return redirect("login")

    if request.method == "POST":
        employee_id = request.POST.get("employee")       # matches form name
        new_position = request.POST.get("new_position")
        promotion_date = request.POST.get("promoted_at") # matches form name
        remarks = request.POST.get("remarks", "")

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, "Employee not found.")
            return redirect("promotion")

        # Check eligibility
        if not employee.can_apply():
            messages.error(request, f"Employee {employee.full_name} is not eligible for promotion (promoted within last year).")
            return redirect("promotion")

        # Record the promotion
        Promotion.objects.create(
            employee=employee,
            new_grade=new_position,
            promoted_at=promotion_date,
            remarks=remarks
        )

        # Update employee details
        employee.last_promotion_date = promotion_date
        employee.save(update_fields=["last_promotion_date"])

        messages.success(request, f"Employee {employee.full_name} promoted to {new_position} successfully.")
        return redirect("promotion")

    employees = Employee.objects.all().order_by("full_name")
    context = {
        "employees": employees,
        "positions": POSITION_LIST
    }
    return render(request, "awash/promotion.html", context)
def promotion_list(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You must be logged in as HR to view this page.")
        return redirect("login")

    promotions = Promotion.objects.select_related("employee").order_by("-promoted_at")
    return render(request, "awash/promotion_list.html", {"promotions": promotions})