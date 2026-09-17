from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import (
    BloodRequestForm,
    DonorProfileForm,
    DonorSearchForm,
    RegisterForm,
    RequestFilterForm,
)
from .models import BloodRequest, DonorProfile

PAGE_SIZE = 9


def home(request):
    stats = {
        'donor_count': DonorProfile.objects.filter(is_available=True).count(),
        'pending_requests': BloodRequest.objects.filter(status=BloodRequest.STATUS_PENDING).count(),
        'fulfilled_requests': BloodRequest.objects.filter(status=BloodRequest.STATUS_FULFILLED).count(),
    }
    recent_requests = BloodRequest.objects.filter(
        status=BloodRequest.STATUS_PENDING
    )[:5]
    return render(request, 'bloodbank/home.html', {
        'stats': stats,
        'recent_requests': recent_requests,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_detail(request):
    profile, _ = DonorProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'blood_group': 'O+',
            'phone': '',
            'location': '',
        },
    )
    return render(request, 'bloodbank/profile_detail.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = DonorProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'blood_group': 'O+',
            'phone': '',
            'location': '',
        },
    )
    if request.method == 'POST':
        form = DonorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile-detail')
    else:
        form = DonorProfileForm(instance=profile)
    return render(request, 'bloodbank/profile_form.html', {'form': form})


def donor_list(request):
    form = DonorSearchForm(request.GET or None)
    donors = DonorProfile.objects.select_related('user')

    if form.is_valid():
        blood_group = form.cleaned_data.get('blood_group')
        location = form.cleaned_data.get('location')
        available_only = form.cleaned_data.get('available_only')

        if blood_group:
            donors = donors.filter(blood_group=blood_group)
        if location:
            donors = donors.filter(location__icontains=location)
        if available_only:
            donors = donors.filter(is_available=True)

    paginator = Paginator(donors, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bloodbank/donor_list.html', {
        'form': form,
        'page_obj': page_obj,
        'donors': page_obj.object_list,
    })


def donor_detail(request, pk):
    donor = get_object_or_404(DonorProfile, pk=pk)
    return render(request, 'bloodbank/donor_detail.html', {'donor': donor})


def request_list(request):
    form = RequestFilterForm(request.GET or None)
    requests_qs = BloodRequest.objects.select_related('requester')

    if form.is_valid():
        blood_group = form.cleaned_data.get('blood_group')
        location = form.cleaned_data.get('location')
        status = form.cleaned_data.get('status')

        if blood_group:
            requests_qs = requests_qs.filter(blood_group=blood_group)
        if location:
            requests_qs = requests_qs.filter(location__icontains=location)
        if status:
            requests_qs = requests_qs.filter(status=status)

    paginator = Paginator(requests_qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bloodbank/request_list.html', {
        'form': form,
        'page_obj': page_obj,
        'requests': page_obj.object_list,
    })


def request_detail(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    return render(request, 'bloodbank/request_detail.html', {'blood_request': blood_request})


@login_required
def request_create(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()
            messages.success(request, "Blood request created successfully.")
            return redirect('request-detail', pk=blood_request.pk)
    else:
        form = BloodRequestForm()
    return render(request, 'bloodbank/request_form.html', {'form': form, 'is_create': True})


@login_required
def request_update(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    if blood_request.requester_id != request.user.id:
        messages.error(request, "You can only edit your own requests.")
        return redirect('request-detail', pk=pk)

    if request.method == 'POST':
        form = BloodRequestForm(request.POST, instance=blood_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Blood request updated.")
            return redirect('request-detail', pk=blood_request.pk)
    else:
        form = BloodRequestForm(instance=blood_request)
    return render(request, 'bloodbank/request_form.html', {'form': form, 'is_create': False})


@login_required
def request_delete(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    if blood_request.requester_id != request.user.id:
        messages.error(request, "You can only delete your own requests.")
        return redirect('request-detail', pk=pk)

    if request.method == 'POST':
        blood_request.delete()
        messages.success(request, "Blood request deleted.")
        return redirect('my-requests')
    return render(request, 'bloodbank/request_confirm_delete.html', {'blood_request': blood_request})


@login_required
def my_requests(request):
    requests_qs = BloodRequest.objects.filter(requester=request.user)
    paginator = Paginator(requests_qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'bloodbank/my_requests.html', {
        'page_obj': page_obj,
        'requests': page_obj.object_list,
    })
