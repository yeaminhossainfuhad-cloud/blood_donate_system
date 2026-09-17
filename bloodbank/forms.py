from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import BLOOD_GROUP_CHOICES, BloodRequest, DonorProfile

BOOTSTRAP_INPUT = 'form-control'
BOOTSTRAP_SELECT = 'form-select'


class RegisterForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm with the extra profile
    fields requested in the spec, so registration creates both the
    User and its DonorProfile in one step.
    """
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, label="Full Name")
    phone = forms.CharField(max_length=16, label="Phone Number")
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)
    location = forms.CharField(max_length=100)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date of Birth"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'full_name', 'phone',
            'blood_group', 'location', 'date_of_birth',
            'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = BOOTSTRAP_SELECT if isinstance(field, forms.ChoiceField) else BOOTSTRAP_INPUT
            field.widget.attrs.update({'class': css})

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # The post_save signal creates a blank DonorProfile stub;
            # fill it in with the real submitted data.
            profile, _ = DonorProfile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data['full_name']
            profile.phone = self.cleaned_data['phone']
            profile.blood_group = self.cleaned_data['blood_group']
            profile.location = self.cleaned_data['location']
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.is_available = True
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': BOOTSTRAP_INPUT})


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = [
            'full_name', 'blood_group', 'phone', 'location',
            'date_of_birth', 'profile_picture', 'last_donation_date',
            'is_available', 'description',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_available':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field, forms.ChoiceField):
                field.widget.attrs.update({'class': BOOTSTRAP_SELECT})
            elif name == 'profile_picture':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': BOOTSTRAP_INPUT})

    def clean_last_donation_date(self):
        last_date = self.cleaned_data.get('last_donation_date')
        if last_date and last_date > date.today():
            raise forms.ValidationError("Last donation date cannot be in the future.")
        return last_date


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'patient_name', 'blood_group', 'hospital_name', 'location',
            'required_date', 'bags_required', 'contact_number',
            'description', 'status',
        ]
        widgets = {
            'required_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, forms.ChoiceField):
                field.widget.attrs.update({'class': BOOTSTRAP_SELECT})
            else:
                field.widget.attrs.update({'class': BOOTSTRAP_INPUT})
        # Status only matters once a request already exists; hide it on create.
        if not (self.instance and self.instance.pk):
            self.fields.pop('status')

    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        if required_date and required_date < date.today():
            raise forms.ValidationError("Required date cannot be in the past.")
        return required_date

    def clean_bags_required(self):
        bags = self.cleaned_data.get('bags_required')
        if bags is not None and bags <= 0:
            raise forms.ValidationError("Number of bags must be a positive number.")
        return bags


class DonorSearchForm(forms.Form):
    blood_group = forms.ChoiceField(
        choices=[('', 'Any Blood Group')] + BLOOD_GROUP_CHOICES,
        required=False,
    )
    location = forms.CharField(required=False)
    available_only = forms.BooleanField(required=False, label="Available only")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['blood_group'].widget.attrs.update({'class': BOOTSTRAP_SELECT})
        self.fields['location'].widget.attrs.update(
            {'class': BOOTSTRAP_INPUT, 'placeholder': 'e.g. Feni'}
        )
        self.fields['available_only'].widget.attrs.update({'class': 'form-check-input'})


class RequestFilterForm(forms.Form):
    blood_group = forms.ChoiceField(
        choices=[('', 'Any Blood Group')] + BLOOD_GROUP_CHOICES,
        required=False,
    )
    location = forms.CharField(required=False)
    status = forms.ChoiceField(
        choices=[('', 'Any Status')] + BloodRequest.STATUS_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['blood_group'].widget.attrs.update({'class': BOOTSTRAP_SELECT})
        self.fields['status'].widget.attrs.update({'class': BOOTSTRAP_SELECT})
        self.fields['location'].widget.attrs.update(
            {'class': BOOTSTRAP_INPUT, 'placeholder': 'e.g. Feni'}
        )
