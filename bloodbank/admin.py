from django.contrib import admin

from .models import BloodRequest, DonorProfile


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_group', 'location', 'is_available', 'last_donation_date', 'updated_at')
    list_filter = ('blood_group', 'is_available', 'location')
    search_fields = ('full_name', 'user__username', 'user__email', 'phone', 'location')


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'blood_group', 'hospital_name', 'location', 'required_date', 'status', 'requester')
    list_filter = ('blood_group', 'status', 'location')
    search_fields = ('patient_name', 'hospital_name', 'location', 'requester__username')
    list_editable = ('status',)
