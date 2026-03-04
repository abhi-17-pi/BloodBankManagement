from django.db import models


class Donor(models.Model):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    donor_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    mobile = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    email = models.EmailField(blank=True, null=True)  # allow optional email

    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    city = models.CharField(max_length=50)
    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)  # 🔥 audit trail

    def __str__(self):
        return f"{self.donor_id} - {self.name}"


class BloodStock(models.Model):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        unique=True
    )

    units = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)  # 🔥 stock tracking

    def __str__(self):
        return f"{self.blood_group} - {self.units} units"