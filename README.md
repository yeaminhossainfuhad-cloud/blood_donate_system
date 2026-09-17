# Blood Donate & Request System

A Django-based web application where users can register as blood donors, create
blood requests, and find suitable donors based on blood group and location.

> "Find a donor. Save a life."

## Features

- **Authentication** — register, login, logout, view/edit profile (Django's
  built-in auth system).
- **Donor Profiles** — every account doubles as a donor profile: blood group,
  phone, location, last donation date, availability toggle, short bio, optional
  profile picture.
- **Blood Requests** — full CRUD for blood requests (patient name, blood group,
  hospital, location, required date, bags needed, contact number, status).
  Only the requester can edit/delete their own requests.
- **Donor Search** — filter donors by blood group, location, and availability.
- **Blood Request Listing** — filter requests by blood group, location, and
  status (Pending / Fulfilled / Cancelled).
- **Detail pages** for both donors and requests.
- **Pagination** on donor and request listings.
- **Form validation** — required fields, phone number format, positive bag
  count, required date can't be in the past, blood group restricted to
  predefined choices.
- **Django messages** for success/error feedback, styled with Bootstrap 5.
- **Admin dashboard** — manage donors and requests from `/admin/`.
- **Seed command** — populate sample data for quick demoing.

## Tech Stack

- Python / Django
- SQLite (default, zero-config)
- Bootstrap 5 (via CDN)
- Pillow (for profile picture uploads)

## Project Structure

```
blood_donate_system/
├── manage.py
├── requirements.txt
├── config/            # project settings, urls, wsgi/asgi
└── bloodbank/         # main app: models, views, forms, templates, static
    ├── models.py       # DonorProfile, BloodRequest
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── signals.py
    ├── management/commands/seed_data.py
    ├── templates/
    └── static/
```

## Setup Instructions

1. **Clone the repository and enter the folder**
   ```bash
   git clone <your-repo-url>
   cd blood_donate_system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **(Optional) Create an admin superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **(Optional) Seed sample data** — creates demo donors (`donor1` … `donorN`,
   password `password123`) and sample blood requests:
   ```bash
   python manage.py seed_data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. Visit **http://127.0.0.1:8000/** in your browser.
   Admin dashboard: **http://127.0.0.1:8000/admin/**

## Key URLs

| Page                  | URL                        |
|------------------------|-----------------------------|
| Home                   | `/`                         |
| Register               | `/register/`                |
| Login / Logout         | `/login/`, `/logout/`       |
| My Profile             | `/profile/`                 |
| Edit Profile           | `/profile/edit/`            |
| Find Donors            | `/donors/`                  |
| Donor Detail           | `/donors/<id>/`             |
| Blood Requests         | `/requests/`                |
| Request Detail         | `/requests/<id>/`           |
| Create Request         | `/requests/create/`         |
| Edit / Delete Request  | `/requests/<id>/edit/`, `/requests/<id>/delete/` |
| My Requests            | `/requests/mine/`           |

## Notes

- `DEBUG = True` and `SECRET_KEY` in `config/settings.py` are set for local
  development only — change both before deploying to production.
- Uploaded profile pictures are stored under `media/profile_pics/`.
