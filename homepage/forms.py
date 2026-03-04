from django import forms
from .models import Donor, BloodStock


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = "__all__"


class StockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ["blood_group", "units"]