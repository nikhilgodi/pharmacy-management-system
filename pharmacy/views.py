from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Medicine, Order


def is_admin(user):
    return user.is_authenticated and user.is_superuser


# =========================================================
# LOGIN / LOGOUT
# =========================================================

def login_page(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    return render(request, 'pharmacy/login.html')


@require_POST
def login_user(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        return JsonResponse({
            'success': False,
            'message': 'Please enter username and password.'
        })

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({
            'success': False,
            'message': 'Invalid username or password.'
        })

    if not user.is_active:
        return JsonResponse({
            'success': False,
            'message': 'This account is inactive.'
        })

    login(request, user)

    return JsonResponse({
        'success': True,
        'message': 'Login successful.',
        'redirect': '/admin-dashboard/' if is_admin(user) else '/user-dashboard/'
    })


def logout_user(request):
    logout(request)
    return redirect('login')


# =========================================================
# SHOPKEEPER REGISTRATION
# Registered accounts are NORMAL USERS / CUSTOMERS.
# Only the original Django superuser is the admin.
# =========================================================

def shopkeeper_register_page(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    return render(request, 'pharmacy/shopkeeper_register.html')


@require_POST
def shopkeeper_register_user(request):
    full_name = request.POST.get('fullName', '').strip()
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirmPassword', '')

    if not full_name:
        return JsonResponse({'success': False, 'message': 'Please enter your full name.'})

    if not username:
        return JsonResponse({'success': False, 'message': 'Please enter a username.'})

    if not email:
        return JsonResponse({'success': False, 'message': 'Please enter your email.'})

    if not password:
        return JsonResponse({'success': False, 'message': 'Please enter a password.'})

    if password != confirm_password:
        return JsonResponse({'success': False, 'message': 'Passwords do not match.'})

    if len(password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must contain at least 6 characters.'})

    if User.objects.filter(username__iexact=username).exists():
        return JsonResponse({'success': False, 'message': 'Username already exists.'})

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'success': False, 'message': 'Email already exists.'})

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=full_name,
    )

    # Explicitly keep every registered account as a normal user.
    user.is_superuser = False
    user.is_staff = False
    user.save(update_fields=['is_superuser', 'is_staff'])

    return JsonResponse({
        'success': True,
        'message': 'Account created successfully. You can now login.',
        'redirect': '/login/'
    })


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not is_admin(request.user):
        return redirect('user_dashboard')

    medicines = Medicine.objects.all().order_by('name')
    orders = Order.objects.select_related('medicine', 'user').order_by('-order_date')

    for order in orders:
        order.total_price = order.medicine.price * order.count

    total_medicines = medicines.count()
    low_stock_medicines = medicines.filter(count__gt=0, count__lte=10).count()
    out_of_stock_medicines = medicines.filter(count=0).count()
    total_orders = orders.count()

    # Medicine expiry/expiry-warning metrics used by the existing dashboard.
    # These are calculated from the existing manufacture/expiry-date fields.
    today = timezone.localdate()
    expiry_warning_date = today + timedelta(days=30)

    expired_medicines = medicines.filter(expiry_date__lt=today).count()
    expiring_soon_medicines = medicines.filter(
        expiry_date__gte=today,
        expiry_date__lte=expiry_warning_date,
    ).count()

    pending_orders = orders.filter(status='Pending').count()
    in_progress_orders = orders.filter(status='In Progress').count()
    delivered_orders = orders.filter(status='Delivered').count()
    rejected_orders = orders.filter(status='Rejected').count()

    # The existing dashboard still contains a few legacy "approved"
    # variables. Keep them available so the complete original UI continues
    # to render while the actual workflow remains Pending -> In Progress ->
    # Delivered / Rejected.
    delivered_count = sum(
        order.count
        for order in orders
        if order.status == 'Delivered'
    )

    inventory_value = sum(
        medicine.price * medicine.count
        for medicine in medicines
    )

    delivered_sales = sum(
        order.medicine.price * order.count
        for order in orders
        if order.status == 'Delivered'
    )

    return render(
        request,
        'pharmacy/admin_dashboard.html',
        {
            'medicines': medicines,
            'orders': orders,
            'total_medicines': total_medicines,
            'low_stock_medicines': low_stock_medicines,
            'out_of_stock_medicines': out_of_stock_medicines,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'in_progress_orders': in_progress_orders,
            'delivered_orders': delivered_orders,
            'rejected_orders': rejected_orders,
            # Kept for compatibility with the existing dashboard template.
            'approved_orders': delivered_orders,
            'approved_sales': delivered_sales,
            'delivered_sales': delivered_sales,
            'delivered_count': delivered_count,
            # Keep the legacy key available for any older template that may still reference it.
            'approved_count': delivered_count,
            'expired_medicines': expired_medicines,
            'expiring_soon_medicines': expiring_soon_medicines,
            'inventory_value': inventory_value,
        }
    )


# =========================================================
# MEDICINE MANAGEMENT
# =========================================================

def add_medicine_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not is_admin(request.user):
        return redirect('user_dashboard')
    return render(request, 'pharmacy/add_medicine.html')


@require_POST
def add_medicine(request):
    if not request.user.is_authenticated or not is_admin(request.user):
        return JsonResponse({'success': False, 'message': 'You are not authorized.'}, status=403)

    name = request.POST.get('name', '').strip()
    category = request.POST.get('category', '').strip()
    manufacture_date = request.POST.get('manufacture_date', '').strip()
    expiry_date = request.POST.get('expiry_date', '').strip()
    price = request.POST.get('price', '').strip()
    count = request.POST.get('count', '').strip()

    if not all([name, category, manufacture_date, expiry_date, price, count]):
        return JsonResponse({'success': False, 'message': 'Please fill all fields.'})

    try:
        price_value = float(price)
        count_value = int(count)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Price and count must be valid numbers.'})

    if price_value < 0:
        return JsonResponse({'success': False, 'message': 'Price cannot be negative.'})

    if count_value < 0:
        return JsonResponse({'success': False, 'message': 'Count cannot be negative.'})

    if expiry_date <= manufacture_date:
        return JsonResponse({'success': False, 'message': 'Expiry date must be after manufacture date.'})

    Medicine.objects.create(
        name=name,
        category=category,
        manufacture_date=manufacture_date,
        expiry_date=expiry_date,
        price=price_value,
        count=count_value,
    )

    return JsonResponse({'success': True, 'message': 'Medicine added successfully!'})


def edit_medicine_page(request, medicine_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not is_admin(request.user):
        return redirect('user_dashboard')

    medicine = get_object_or_404(Medicine, id=medicine_id)
    return render(request, 'pharmacy/edit_medicine.html', {'medicine': medicine})


@require_POST
def edit_medicine(request, medicine_id):
    if not request.user.is_authenticated or not is_admin(request.user):
        return JsonResponse({'success': False, 'message': 'You are not authorized.'}, status=403)

    medicine = get_object_or_404(Medicine, id=medicine_id)

    name = request.POST.get('name', '').strip()
    category = request.POST.get('category', '').strip()
    manufacture_date = request.POST.get('manufacture_date', '').strip()
    expiry_date = request.POST.get('expiry_date', '').strip()
    price = request.POST.get('price', '').strip()
    count = request.POST.get('count', '').strip()

    if not all([name, category, manufacture_date, expiry_date, price, count]):
        return JsonResponse({'success': False, 'message': 'Please fill all fields.'})

    try:
        price_value = float(price)
        count_value = int(count)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Price and count must be valid numbers.'})

    if price_value < 0:
        return JsonResponse({'success': False, 'message': 'Price cannot be negative.'})

    if count_value < 0:
        return JsonResponse({'success': False, 'message': 'Count cannot be negative.'})

    if expiry_date <= manufacture_date:
        return JsonResponse({'success': False, 'message': 'Expiry date must be after manufacture date.'})

    medicine.name = name
    medicine.category = category
    medicine.manufacture_date = manufacture_date
    medicine.expiry_date = expiry_date
    medicine.price = price_value
    medicine.count = count_value
    medicine.save()

    return JsonResponse({'success': True, 'message': 'Medicine updated successfully!'})


@require_POST
def delete_medicine(request, medicine_id):
    if not request.user.is_authenticated or not is_admin(request.user):
        return JsonResponse({'success': False, 'message': 'You are not authorized.'}, status=403)

    medicine = get_object_or_404(Medicine, id=medicine_id)
    medicine.delete()

    return JsonResponse({'success': True, 'message': 'Medicine deleted successfully.'})


# =========================================================
# CUSTOMER DASHBOARD
# =========================================================

def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if is_admin(request.user):
        return redirect('admin_dashboard')

    medicines = Medicine.objects.all().order_by('name')
    return render(
        request,
        'pharmacy/user_dashboard.html',
        {'medicines': medicines}
    )


@require_POST
def order_medicine(request, medicine_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login first.'
        }, status=401)

    if is_admin(request.user):
        return JsonResponse({
            'success': False,
            'message': 'Admin accounts cannot place customer orders.'
        }, status=403)

    medicine = get_object_or_404(Medicine, id=medicine_id)

    try:
        count = int(request.POST.get('count', '0'))
    except (TypeError, ValueError):
        return JsonResponse({
            'success': False,
            'message': 'Please enter a valid count.'
        })

    if count < 1:
        return JsonResponse({
            'success': False,
            'message': 'Please enter a valid count.'
        })

    with transaction.atomic():
        medicine = Medicine.objects.select_for_update().get(id=medicine_id)

        if count > medicine.count:
            return JsonResponse({
                'success': False,
                'message': 'Order count cannot be greater than available count.'
            })

        medicine.count -= count
        medicine.save(update_fields=['count'])

        order = Order.objects.create(
            medicine=medicine,
            user=request.user,
            count=count,
            status='Pending'
        )

    return JsonResponse({
        'success': True,
        'message': f'{medicine.name} order placed successfully.',
        'order_id': order.id
    })


# =========================================================
# USER MY ORDERS
# =========================================================

def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if is_admin(request.user):
        return redirect('admin_dashboard')

    orders = Order.objects.filter(
        user=request.user
    ).select_related(
        'medicine'
    ).order_by('-order_date')

    for order in orders:
        order.total_price = order.medicine.price * order.count

    return render(
        request,
        'pharmacy/my_orders.html',
        {'orders': orders}
    )


# =========================================================
# ADMIN ORDER MANAGEMENT
# =========================================================

def orders_management(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not is_admin(request.user):
        return redirect('user_dashboard')

    orders = Order.objects.select_related(
        'medicine',
        'user'
    ).order_by('-order_date')

    for order in orders:
        order.total_price = order.medicine.price * order.count

    return render(
        request,
        'pharmacy/orders_management.html',
        {'orders': orders}
    )


@require_POST
def update_order_status(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login first.'
        }, status=401)

    if not is_admin(request.user):
        return JsonResponse({
            'success': False,
            'message': 'You are not authorized to update orders.'
        }, status=403)

    order = get_object_or_404(
        Order.objects.select_related('medicine', 'user'),
        id=order_id
    )

    new_status = request.POST.get('status', '').strip()

    if new_status not in ['In Progress', 'Delivered', 'Rejected']:
        return JsonResponse({
            'success': False,
            'message': 'Invalid order status.'
        })

    with transaction.atomic():
        order = Order.objects.select_for_update().select_related('medicine').get(id=order_id)
        current_status = order.status

        # Pending -> In Progress
        if current_status == 'Pending' and new_status == 'In Progress':
            order.status = 'In Progress'
            order.save(update_fields=['status'])

            return JsonResponse({
                'success': True,
                'message': 'Order moved to In Progress.'
            })

        # In Progress -> Delivered
        if current_status == 'In Progress' and new_status == 'Delivered':
            order.status = 'Delivered'
            order.save(update_fields=['status'])

            return JsonResponse({
                'success': True,
                'message': 'Order marked as Delivered.'
            })

        # Pending -> Rejected and return medicine count to inventory.
        if current_status == 'Pending' and new_status == 'Rejected':
            order.medicine.count += order.count
            order.medicine.save(update_fields=['count'])

            order.status = 'Rejected'
            order.save(update_fields=['status'])

            return JsonResponse({
                'success': True,
                'message': 'Order rejected successfully.'
            })

    return JsonResponse({
        'success': False,
        'message': f'Order cannot be changed from {current_status} to {new_status}.'
    })
