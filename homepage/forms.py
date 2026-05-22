from django import forms
from django.forms.widgets import SelectDateWidget
from .models import Donor, BloodStock

CURRENT_YEAR = 2026
YEAR_CHOICES = list(range(CURRENT_YEAR - 80, CURRENT_YEAR - 17))  # age 18–80

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = "__all__"
        widgets = {
            'date_of_birth': SelectDateWidget(
                years=YEAR_CHOICES,
                attrs={'class': 'dob-select'}
            ),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ["blood_group", "units"]