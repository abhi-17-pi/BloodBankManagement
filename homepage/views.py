from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import DonorForm, StockForm
from .models import Donor, BloodStock
from django.db.models import Sum
from django.utils.timezone import now

def login(request):
    # Handle authentication using Django's auth system
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'homepage/login.html')


def signup(request):
    # Allow users to create an account using Django's UserCreationForm
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'homepage/signup.html', {'form': form})
    
@login_required
def home(request):
    mode = request.GET.get("mode")

    context = {
        "show_new_form": False,
        "show_update_form": False,
        "show_all_donor": False,
        "show_search_location": False,
        "show_search_bg": False,
        "show_add_stock": False,
        "show_remove_stock": False,
        "show_view_stock": False,
        "show_delete_donor": False,
        "show_call_form": False,
        "donors": None,
        "call_donors": None,
        "stocks": None,
    }

    # ---------- GET ----------
    if request.method == "GET":
        if mode == "new":
            context["show_new_form"] = True
            context["new_form"] = DonorForm()

        elif mode == "update":
            context["show_update_form"] = True

        elif mode == "all":
            context["show_all_donor"] = True
            context["donors"] = Donor.objects.all()

        elif mode == "location":
            context["show_search_location"] = True

        elif mode == "blood":
            context["show_search_bg"] = True

        elif mode == "add_stock":
            context["show_add_stock"] = True

        elif mode == "remove_stock":
            context["show_remove_stock"] = True

        elif mode == "delete":
            context["show_delete_donor"] = True

        elif mode == "call":
            context["show_call_form"] = True

        elif mode == "view_stock":
            context["show_view_stock"] = True
            context["stocks"] = BloodStock.objects.all()

    # ---------- POST ----------
    if request.method == "POST":

        if mode == "location" and "city" in request.POST:
            city = request.POST.get("city")
            context["donors"] = Donor.objects.filter(city__icontains=city)
            context["show_search_location"] = True

        elif mode == "blood" and "blood_group" in request.POST:
            bg = request.POST.get("blood_group")
            context["donors"] = Donor.objects.filter(blood_group=bg)
            context["show_search_bg"] = True

        elif mode == "call" and "call_search" in request.POST:
            bg = request.POST.get("blood_group")
            context["call_donors"] = Donor.objects.filter(blood_group=bg)
            context["show_call_form"] = True

        elif mode == "add_stock":
            bg = request.POST.get("blood_group")
            units = int(request.POST.get("units"))

            stock, _ = BloodStock.objects.get_or_create(
                blood_group=bg, defaults={"units": 0}
            )
            stock.units += units
            stock.save()

            messages.success(request, "Stock added successfully")
            context["show_view_stock"] = True
            context["stocks"] = BloodStock.objects.all()

        elif mode == "remove_stock":
            bg = request.POST.get("blood_group")
            units = int(request.POST.get("units"))

            try:
                stock = BloodStock.objects.get(blood_group=bg)
                if stock.units >= units:
                    stock.units -= units
                    stock.save()
                    messages.success(request, "Stock removed successfully")
                else:
                    messages.error(request, "Not enough stock")
            except BloodStock.DoesNotExist:
                messages.error(request, "Blood group not found")

            context["show_view_stock"] = True
            context["stocks"] = BloodStock.objects.all()

        elif mode == "delete" and "donor_id" in request.POST:
            donor_id = request.POST.get("donor_id")

            try:
                Donor.objects.get(donor_id=donor_id).delete()
                messages.success(request, "🗑️ Donor deleted successfully")
            except Donor.DoesNotExist:
                messages.error(request, "❌ Donor not found")

            context["show_delete_donor"] = True

    # ---------- DASHBOARD STATS (ALWAYS RUN) ----------
    total_donors = Donor.objects.count()
    total_units = BloodStock.objects.aggregate(total=Sum("units"))["total"] or 0
    blood_groups = BloodStock.objects.filter(units__gt=0).count()

    today_count = Donor.objects.filter(
        created_at__date=now().date()
    ).count() if hasattr(Donor, "created_at") else Donor.objects.count()

    context.update({
        "total_donors": total_donors,
        "total_units": total_units,
        "blood_groups": blood_groups,
        "today_count": today_count,
        "mode": mode,
    })

    return render(request, "homepage/home.html", context)

@login_required
def new_donor(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)

        if form.is_valid():
            donor_id = form.cleaned_data["donor_id"]

            # Duplicate ID check
            if Donor.objects.filter(donor_id=donor_id).exists():
                messages.error(request, "❌ Donor ID already exists")
                return redirect("/home/?mode=new")

            form.save()
            messages.success(request, "✅ Donor registered successfully!")
            return redirect('/home/?mode=new')

        else:
            print("❌ FORM ERRORS:", form.errors)  # 🔥 Debug helper
            messages.error(request, "❌ Invalid input. Fix highlighted fields.")

    return redirect('/home/?mode=new')

@login_required
def update_donor(request):
    donor = None
    form = None

    if request.method == "POST" and "search" in request.POST:
        donor_id = request.POST.get("donor_id")
        try:
            donor = Donor.objects.get(donor_id=donor_id)
            form = DonorForm(instance=donor)
        except Donor.DoesNotExist:
            messages.error(request, "❌ Donor not found")

    elif request.method == "POST" and "update" in request.POST:
        donor = get_object_or_404(Donor, donor_id=request.POST.get("donor_id"))
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Donor updated successfully")
            return redirect("/home/?mode=update")

    return render(request, "homepage/home.html", {
        "show_update_form": True,
        "form": form,
        "donor": donor
    })

@login_required
def delete_donor(request):
    return render(request, 'homepage/delete_donor.html')

@login_required
def stock(request):
    return render(request, 'homepage/stock.html')


@login_required
def delete_donor_popup(request):
    # Render a partial template for the delete donor popup (keeps URL referenced by urls.py)
    return render(request, 'homepage/delete_donor.html')

def logout_view(request):
    logout(request)
    return redirect('login')

