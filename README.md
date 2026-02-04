# Boutique Management Software

A comprehensive management system for a boutique offering Dress Rentals, Event Planning, and Seamstress Services.

## Features

*   **Dashboard**: Central hub for operations.
*   **Inventory Management**: Track dresses, decor, and accessories with QR code generation.
*   **Rentals**: Date-based booking wizard with availability checking.
*   **Event Planning**: Manage events, guest counts, and reserve decor inventory.
*   **Seamstress Services**: Track alteration jobs linked to rentals or standalone.
*   **Finance**: Automatic invoicing, payment tracking, and financial reports.
*   **Calendar**: Visual monthly schedule of events and rentals.
*   **Authentication**: Role-based access (Manager, Sales, Seamstress).

## Tech Stack

*   **Backend**: Python (Django 6.0)
*   **Database**: SQLite (default) / PostgreSQL (production ready)
*   **Frontend**: Bootstrap 5 + Custom "Boutique" Theme
*   **Deployment**: Docker

## Getting Started

### Prerequisites

*   Docker & Docker Compose

### Installation (Docker)

1.  Clone the repository.
2.  Run the application:
    ```bash
    docker-compose up -d --build
    ```
3.  Create a superuser (Manager):
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
4.  Setup roles:
    ```bash
    docker-compose exec web python manage.py setup_roles
    ```
5.  Access the app at `http://localhost:8000`.

### Manual Installation

1.  Create a virtual environment and activate it.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run migrations:
    ```bash
    python manage.py migrate
    ```
4.  Setup roles:
    ```bash
    python manage.py setup_roles
    ```
5.  Run server:
    ```bash
    python manage.py runserver
    ```

## Roles

*   **Manager**: Full access to all features.
*   **Sales**: Can view/add rentals, events, and customers.
*   **Seamstress**: Can only view/edit seamstress jobs.

## Deployment

For production, update `docker-compose.yml` or your environment variables:
*   Set `DEBUG=0`
*   Set a strong `SECRET_KEY`
*   Configure `ALLOWED_HOSTS`
