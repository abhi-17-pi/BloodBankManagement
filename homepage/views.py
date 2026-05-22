from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import DonorForm, StockForm
from .models import Donor, BloodStock
from django.db.models import Sum
from django.utils.timezone import now
from urllib.parse import quote_plus


def send_notification_email(subject, body, recipient_list):
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as exc:
        return False


@login_required
def call_donor_action(request, donor_id):
    try:
        donor = Donor.objects.get(id=donor_id)
        donor_mobile = ''.join(ch for ch in donor.mobile if ch.isdigit())
        if donor_mobile.startswith('0'):
            donor_mobile = donor_mobile[1:]

        message_text = (
            f"Hello {donor.name},\n\n"
            f"This is an urgent request from our Blood Bank.\n"
            f"We need blood donation of your blood group {donor.blood_group}.\n\n"
            f"Please contact us as soon as possible.\n"
            f"Thank you for being a life saver!\n\n"
            f"- Blood Bank Team"
        )
        message = quote_plus(message_text)

        if len(donor_mobile) >= 10:
            whatsapp_url = f"https://api.whatsapp.com/send?phone={donor_mobile}&text={message}"
        else:
            whatsapp_url = f"https://api.whatsapp.com/send?text={message}"

        if donor.email:
            email_subject = "Urgent: Blood Donation Needed"
            email_body = (
                f"Hello {donor.name},\n\n"
                f"We urgently need a blood donor with blood group {donor.blood_group}.\n\n"
                f"Your Details:\n"
                f"Donor ID: {donor.donor_id}\n"
                f"Blood Group: {donor.blood_group}\n\n"
                f"Please contact us immediately at the Blood Bank.\n"
                f"Thank you for your compassion and willingness to save lives!\n\n"
                f"Best regards,\n"
                f"Blood Bank Team"
            )
            send_notification_email(email_subject, email_body, [donor.email])

        admin_subject = "Donor Called - Urgent Request"
        admin_body = (
            f"A donor has been called for urgent blood donation.\n\n"
            f"Donor Name: {donor.name}\n"
            f"Donor ID: {donor.donor_id}\n"
            f"Blood Group: {donor.blood_group}\n"
            f"Mobile: {donor.mobile}\n"
            f"Email: {donor.email}\n"
            f"Called by: {request.user.get_username()}\n\n"
            f"WhatsApp and Email have been sent to the donor."
        )
        send_notification_email(admin_subject, admin_body, [settings.ADMIN_EMAIL])

        messages.success(request, f"✅ WhatsApp and email sent to {donor.name} successfully.")
        return redirect(whatsapp_url)

    except Donor.DoesNotExist:
        messages.error(request, "❌ Donor not found")
        return redirect("/home/?mode=call")


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
        "search_location_searched": False,
        "search_bg_searched": False,
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
            context["search_location_searched"] = True
            context["city"] = city

            subject = "Donor Search by Location"
            body = (
                f"A search for donors by location was performed.\n\n"
                f"Search Query: {city}\n"
                f"Results Found: {context['donors'].count()}\n"
                f"Searched by: {request.user.get_username()}\n"
            )
            send_notification_email(subject, body, [settings.ADMIN_EMAIL])

        elif mode == "blood" and "blood_group" in request.POST:
            bg = request.POST.get("blood_group")
            context["donors"] = Donor.objects.filter(blood_group=bg)
            context["show_search_bg"] = True
            context["search_bg_searched"] = True
            context["blood_group"] = bg

            subject = "Donor Search by Blood Group"
            body = (
                f"A search for donors by blood group was performed.\n\n"
                f"Blood Group: {bg}\n"
                f"Results Found: {context['donors'].count()}\n"
                f"Searched by: {request.user.get_username()}\n"
            )
            send_notification_email(subject, body, [settings.ADMIN_EMAIL])

        elif mode == "call" and "call_search" in request.POST:
            bg = request.POST.get("blood_group")
            context["call_donors"] = Donor.objects.filter(blood_group=bg)
            context["show_call_form"] = True

            subject = "Donor Call Request"
            body = (
                f"A call request search was initiated.\n\n"
                f"Blood Group: {bg}\n"
                f"Donors Found: {context['call_donors'].count()}\n"
                f"Requested by: {request.user.get_username()}\n\n"
                f"Donor Details:\n"
            )
            for donor in context["call_donors"]:
                body += f"- {donor.name} ({donor.mobile})\n"
            send_notification_email(subject, body, [settings.ADMIN_EMAIL])

        elif mode == "add_stock":
            bg = request.POST.get("blood_group")
            units = int(request.POST.get("units"))

            stock, _ = BloodStock.objects.get_or_create(
                blood_group=bg, defaults={"units": 0}
            )
            stock.units += units
            stock.save()

            subject = "Blood Stock Updated"
            body = (
                f"Blood stock has been updated.\n\n"
                f"Blood Group: {bg}\n"
                f"Units Added: {units}\n"
                f"Current Total Units: {stock.units}\n"
                f"Updated by: {request.user.get_username()}\n"
            )
            if not send_notification_email(subject, body, [settings.ADMIN_EMAIL]):
                messages.warning(request, "Stock updated, but admin notification email failed.")
            else:
                messages.success(request, "Stock added successfully and admin notified.")

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

                    subject = "Blood Stock Decreased"
                    body = (
                        f"Blood stock has been decreased.\n\n"
                        f"Blood Group: {bg}\n"
                        f"Units Removed: {units}\n"
                        f"Current Total Units: {stock.units}\n"
                        f"Updated by: {request.user.get_username()}\n"
                    )
                    if not send_notification_email(subject, body, [settings.ADMIN_EMAIL]):
                        messages.warning(request, "Stock removed, but admin notification email failed.")
                    else:
                        messages.success(request, "Stock removed successfully and admin notified.")
                else:
                    messages.error(request, "Not enough stock")
            except BloodStock.DoesNotExist:
                messages.error(request, "Blood group not found")

            context["show_view_stock"] = True
            context["stocks"] = BloodStock.objects.all()

        elif mode == "delete" and "donor_id" in request.POST:
            donor_id = request.POST.get("donor_id")

            try:
                donor = Donor.objects.get(donor_id=donor_id)
                donor.delete()
                subject = "Donor Removed"
                body = (
                    f"Donor record deleted from the system.\n\n"
                    f"Donor ID: {donor_id}\n"
                    f"Name: {donor.name}\n"
                    f"Deleted by: {request.user.get_username()}\n"
                )
                if not send_notification_email(subject, body, [settings.ADMIN_EMAIL]):
                    messages.warning(request, "Donor deleted, but admin notification email failed.")
                else:
                    messages.success(request, "🗑️ Donor deleted successfully and admin notified.")
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
                # Re-render with form data preserved
                return render(request, 'homepage/home.html', {
                    'show_new_form': True,
                    'new_form': form,
                })

            form.save()
            donor = form.instance
            donor_mobile = ''.join(ch for ch in donor.mobile if ch.isdigit())
            if donor_mobile.startswith('0'):
                donor_mobile = donor_mobile[1:]

            message_text = (
                f"Blood Donor Registration Details:\n"
                f"Donor ID: {donor.donor_id}\n"
                f"Name: {donor.name}\n"
                f"Blood Group: {donor.blood_group}\n"
                f"Mobile: {donor.mobile}\n"
                f"City: {donor.city}\n"
                f"Address: {donor.address}\n"
                f"Registered At: {donor.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            message = quote_plus(message_text)

            if len(donor_mobile) >= 10:
                whatsapp_url = f"https://api.whatsapp.com/send?phone={donor_mobile}&text={message}"
            else:
                whatsapp_url = f"https://api.whatsapp.com/send?text={message}"

            if donor.email:
                subject = "Blood Donor Registration Successful"
                email_body = (
                    f"Hello {donor.name},\n\n"
                    "Thank you for registering as a blood donor. Your registration details are below:\n\n"
                    f"Donor ID: {donor.donor_id}\n"
                    f"Blood Group: {donor.blood_group}\n"
                    f"Mobile: {donor.mobile}\n"
                    f"City: {donor.city}\n"
                    f"Address: {donor.address}\n"
                    f"Registered At: {donor.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    "We appreciate your decision to donate blood.\n"
                    "If you have any questions, reply to this email.\n\n"
                    "— Blood Bank Team"
                )
                try:
                    send_mail(
                        subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [donor.email],
                        fail_silently=False,
                    )
                    messages.success(request, "✅ Donor registered and email sent successfully.")
                except Exception as exc:
                    messages.warning(
                        request,
                        "✅ Donor registered, but the confirmation email could not be sent."
                    )

            return redirect(whatsapp_url)

        else:
            # Form invalid — re-render WITH the user's data preserved
            print("❌ FORM ERRORS:", form.errors)
            messages.error(request, "❌ Invalid input. Please fix the highlighted fields.")
            return render(request, 'homepage/home.html', {
                'show_new_form': True,
                'new_form': form,
            })

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
        old_donor_data = {
            "name": donor.name,
            "blood_group": donor.blood_group,
            "mobile": donor.mobile,
            "city": donor.city,
        }
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()

            subject = "Donor Record Updated"
            body = (
                f"A donor record has been updated in the system.\n\n"
                f"Donor ID: {donor.donor_id}\n"
                f"Name: {donor.name}\n"
                f"Blood Group: {donor.blood_group}\n"
                f"Mobile: {donor.mobile}\n"
                f"City: {donor.city}\n"
                f"Updated by: {request.user.get_username()}\n\n"
                f"Previous Details:\n"
                f"Name: {old_donor_data['name']}\n"
                f"Blood Group: {old_donor_data['blood_group']}\n"
                f"Mobile: {old_donor_data['mobile']}\n"
                f"City: {old_donor_data['city']}\n"
            )
            if not send_notification_email(subject, body, [settings.ADMIN_EMAIL]):
                messages.warning(request, "Donor updated, but admin notification email failed.")
            else:
                messages.success(request, "✅ Donor updated successfully and admin notified.")
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

