from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.urls import reverse

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

phone_validator = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message="Enter a valid phone number (9-15 digits, optionally starting with +)."
)


class DonorProfile(models.Model):
    """
    Extended profile for every registered user. Also doubles as the
    donor record: users can mark themselves 'available' to show up in
    donor search results.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donor_profile',
    )
    full_name = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    phone = models.CharField(max_length=16, validators=[phone_validator])
    location = models.CharField(max_length=100, help_text="City / area, e.g. Feni")
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True
    )
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(
        default=True,
        help_text="Uncheck this if you are currently unable to donate."
    )
    description = models.TextField(
        max_length=500, blank=True,
        help_text="A short note about yourself (optional)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.full_name} ({self.blood_group})"

    def get_absolute_url(self):
        return reverse('donor-detail', kwargs={'pk': self.pk})

    @property
    def availability_label(self):
        return "Available" if self.is_available else "Not Available"


class BloodRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_FULFILLED = 'FULFILLED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_FULFILLED, 'Fulfilled'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blood_requests',
    )
    patient_name = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    hospital_name = models.CharField(max_length=150)
    location = models.CharField(max_length=100, help_text="Hospital city / area")
    required_date = models.DateField()
    bags_required = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of blood bags needed"
    )
    contact_number = models.CharField(max_length=16, validators=[phone_validator])
    description = models.TextField(
        max_length=500, blank=True, help_text="Reason / additional details"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('request-detail', kwargs={'pk': self.pk})
