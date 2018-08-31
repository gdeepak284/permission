from django.contrib.gis.db import models
from django.contrib.postgres import fields as pg_fields
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator

validate_mobile = RegexValidator(
    regex="\d{10}", message=_("Enter a valid indian mobile number.")
)


class UserManager(BaseUserManager):
    def create_user(self, email, name, phone, user_type, password=None):
        if not email:
            raise ValueError('Enter the email')

        if not name:
            raise ValueError('Enter the Name')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            user_type=user_type
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password):
        user = self.create_user(email,
                                password=password,
                                name=name,
                                phone=phone,
                                user_type='NA'
                                )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('PHT', 'Pharmacist'),
        ('PAT', 'Patient'),
        ('DOC', 'Doctor')
    )
    name = models.CharField(verbose_name='Full name', max_length=255)
    email = models.EmailField(verbose_name='email address', max_length=50, unique=True)
    created_at = models.DateTimeField(verbose_name='created at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='updated at', auto_now=True)
    user_type = models.CharField(
        verbose_name='user type',
        max_length=2,
        default='PA',
        choices=USER_TYPES
    )
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_active = models.BooleanField(default=True,
                                    help_text='active/inactive.')

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    class Meta:
        ordering = ["created_at"]
        verbose_name = 'User'

    def get_full_name(self):
        return self.name

    def get_first_name(self):
        return self.name.split(' ')[0]

    def __str__(self):
        return self.email


class MedicalRecord(models.Model):
    diagnosis = models.TextField(blank=True)
    user = models.ForeignKey(to=User, related_name='medicalrecord_user')
    doctor = models.ForeignKey(to=User, related_name='medicalrecord_doctor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Doctor -> {}, User -> {}, Diagnosis -> {}".format(self.doctor.name,
                                                            self.user.name,
                                                            self.diagnosis)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('medicalrecord-detail', args=[str(self.id)])


class Prescription(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, related_name='prescription_user')
    doctor = models.ForeignKey(to=User, related_name='prescription_doctor')
    medical_record = models.ForeignKey(to=MedicalRecord, blank=True, null=True)

    def __str__(self):
        return self.user.email

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('prescription-detail', args=[str(self.id)])


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    qty = models.IntegerField()
    strength = models.IntegerField()
    frequency = models.CharField(max_length=50)
    prescription = models.ForeignKey(to=Prescription)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Approval(models.Model):
    STATUS_TYPES = (
        ('PE', 'Pending'),
        ('RE', 'Rejected'),
        ('AP', 'Approved')
    )
    prescription = models.ForeignKey(to=Prescription)
    user = models.ForeignKey(to=User)
    status = models.CharField(
        max_length=2,
        default='PE',
        choices=STATUS_TYPES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


