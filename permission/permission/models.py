from django.contrib.gis.db import models
from django.contrib.postgres import fields as pg_fields
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator

validate_mobile = RegexValidator(
    regex="\d{10}", message=_("Enter a valid indian mobile number.")
)


class Patient(models.Model):
    first_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=20, validators=[validate_mobile],
                             unique=True)
    email = pg_fields.CIEmailField(blank=True, null=True)
    problem = models.CharField(max_length=100, blank=True, default="Nothing")

    class Meta:
        permissions = (
            ("can_view_doctor", "Can view Doctor details"),
            ("can_view_pharmacist", "Can edit Pharmacist details"),
        )

    def __str__(self):
        return self.get_full_name() or self.phone

    @property
    def full_name(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def add_phone(self, phone_number, is_verified=None) -> "Phone":
        return self.phones.create(phone=phone_number, is_verified=is_verified)

    def add_email(self, email, is_verified=None) -> "Email":
        return self.emails.create(email=email, is_verified=is_verified)


class Pharmacist(models.Model):
    name = models.CharField(max_length=100, blank=True, default="")
    shop_name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=20, validators=[validate_mobile],
                             unique=True)
    email = pg_fields.CIEmailField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, default="Nothing")

    class Meta:
        permissions = (
            ("can_view_doctor", "Can view Doctor details"),
            ("can_view_patient", "Can edit Patient details"),
        )

    def __str__(self):
        return self.name() or self.phone

    @property
    def name(self):
        return self.name()

    def get_shop_name(self):
        return self.shop_name

    def get_address(self):
        return self.address

    def get_email(self):
        return self.email

    def add_phone(self, phone_number, is_verified=None) -> "Phone":
        return self.phone.create(phone=phone_number, is_verified=is_verified)

    def add_email(self, email, is_verified=None) -> "Email":
        return self.email.create(email=email, is_verified=is_verified)
