# Pharmacy Management System

A web-based Pharmacy Management System developed using Python, Django, HTML, CSS, JavaScript, and SQL.

## Features

### User
- User registration and login
- View available medicines
- View medicine details
- Place medicine orders
- View order history
- Track order status

### Shopkeeper
- Shopkeeper registration and login
- Add medicines
- Edit medicine details
- Manage medicine inventory
- Manage medicine count
- View customer orders
- Update order status

### Admin
- Admin dashboard
- Manage users and shopkeepers
- Manage medicines
- Manage orders
- Monitor pharmacy operations

## Technologies Used

- Python
- Django
- HTML
- CSS
- JavaScript
- SQL
- SQLite
- Bootstrap

## Project Structure

PMS/
- manage.py
- pharmacy/
  - migrations/
  - static/
  - templates/
  - admin.py
  - apps.py
  - models.py
  - urls.py
  - views.py
- pharmacy_project/
  - settings.py
  - urls.py
  - asgi.py
  - wsgi.py
- .gitignore
- README.md

## Installation

Clone the repository:

git clone https://github.com/nikhilgodi/pharmacy-management-system.git

Open the project directory:

cd pharmacy-management-system

Create a virtual environment:

python -m venv venv

Activate the virtual environment on Windows:

venv\Scripts\activate

Install Django:

pip install django

Run migrations:

python manage.py makemigrations

python manage.py migrate

Start the development server:

python manage.py runserver

Open the application in your browser:

http://127.0.0.1:8000/

## Database

The project uses SQLite for database management during development.

## Responsive Design

The application is designed for desktop, tablet, and mobile devices.

## Future Enhancements

- AI-powered pharmacy assistant
- Low stock notifications
- Advanced analytics
- Automated inventory management
- Online payment integration
- Email notifications

## Developer

Nikhil Godi

B.Tech Artificial Intelligence and Machine Learning

## Purpose

This project is developed for academic and educational purposes.
