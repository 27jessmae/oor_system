from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm
from .models import Reservation, Order, Item, Payment, CustomUser, Table, TableReservation
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime, timedelta

def home(request):
    # Initialize forms for login and registration modals
    login_form = LoginForm()
    register_form = RegisterForm()
    
    return render(request, 'home.html', {
        'login_form': login_form,
        'register_form': register_form,
    })

def reservations(request):
    return render(request, 'reservations.html', {
        'reservations': Reservation.objects.all(),
        'login_form': AuthenticationForm(),
        'register_form': RegisterForm(),
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_date', '-order_time')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Only allow cancellation of pending orders
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} has been cancelled successfully.')
    else:
        messages.error(request, f'Order #{order.id} cannot be cancelled because it is already {order.get_status_display().lower()}.')
    
    return redirect('orders')

def items_view(request):
    items = Item.objects.all()
    current_date = timezone.now().date()
    current_time = timezone.now().time().strftime('%H:%M:%S')
    return render(request, 'items.html', {
        'items': items,
        'current_date': current_date,
        'current_time': current_time
    })

@login_required
def create_order(request):
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=request.POST['item_id'])
        quantity = int(request.POST['quantity'])
        Order.objects.create(
            item=item,
            customer=request.user,
            quantity=quantity,
            order_date=timezone.localdate(),
            order_time=timezone.localtime().time()
        )
        return redirect('orders')
    return redirect('items')

def payments(request):
    return render(request, 'payments.html', {
        'payments': Payment.objects.all(),
        'login_form': AuthenticationForm(),
        'register_form': RegisterForm(),
    })

def login_modal(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # Redirect admin users to admin dashboard
            if is_admin(user):
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            # If form has errors, render the home page with the form errors
            register_form = RegisterForm()
            return render(request, 'home.html', {
                'login_form': form,
                'register_form': register_form,
                'login_error': 'Invalid username or password',
                'show_login_modal': True  # Flag to show the login modal
            })
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def register_modal(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save the user and create a Customer profile
            user = form.save()
            
            # Create a Customer profile for the user
            from .models import Customer
            Customer.objects.create(user=user)
            
            messages.success(request, "Registration successful! Please log in.")
            return redirect('home')
        else:
            # If form has errors, render the home page with the form errors
            login_form = LoginForm()
            return render(request, 'home.html', {
                'login_form': login_form,
                'register_form': form,
                'show_register_modal': True  # Flag to show the register modal
            })
    return redirect('home')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def item_list(request):
    items = Item.objects.all()
    return render(request, 'items.html', {
        'items': items,
        'current_date': now().date(),
        'current_time': now().time(),
    })

@login_required
def create_reservation(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        customer = request.user
        quantity = int(request.POST.get("quantity", 1))
        reservation_date = request.POST.get("reservation_date")
        reservation_time = request.POST.get("reservation_time")

        item = Item.objects.get(id=item_id)

        Reservation.objects.create(
            customer=customer,
            item=item,
            quantity=quantity,
            reservation_date=reservation_date,
            reservation_time=reservation_time
        )
        return redirect('reservations')

@login_required
def reservations_view(request):
    reservations = Reservation.objects.filter(customer=request.user).order_by('-reservation_date', '-reservation_time')
    table_reservations = TableReservation.objects.filter(customer=request.user).order_by('-reservation_date', '-reservation_time')
    return render(request, 'reservations.html', {
        'reservations': reservations,
        'table_reservations': table_reservations
    })

@login_required
def table_reservation_form(request):
    """Display and process the table reservation form"""
    tables = Table.objects.filter(is_available=True).order_by('table_number')
    
    # Initialize forms for login and registration modals
    login_form = LoginForm()
    register_form = RegisterForm()
    
    if request.method == 'POST':
        table_id = request.POST.get('table')
        number_of_guests = request.POST.get('number_of_guests')
        reservation_date = request.POST.get('reservation_date')
        reservation_time = request.POST.get('reservation_time')
        special_requests = request.POST.get('special_requests', '')
        
        # Basic validation
        if not all([table_id, number_of_guests, reservation_date, reservation_time]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('table_reservation_form')
        
        try:
            # Convert to appropriate types
            table = Table.objects.get(id=table_id)
            number_of_guests = int(number_of_guests)
            reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
            reservation_time = datetime.strptime(reservation_time, '%H:%M').time()
            
            # Check if the table is available at the requested time
            conflicting_reservations = TableReservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                status__in=['pending', 'confirmed'],
            )
            
            # Check for time conflicts (assuming reservations last 2 hours)
            for existing_res in conflicting_reservations:
                existing_time = datetime.combine(reservation_date, existing_res.reservation_time)
                requested_time = datetime.combine(reservation_date, reservation_time)
                
                # If the requested time is within 2 hours of an existing reservation
                if abs((existing_time - requested_time).total_seconds()) < 7200:  # 2 hours in seconds
                    messages.error(request, f'Table #{table.table_number} is already reserved at or near that time.')
                    return redirect('table_reservation_form')
            
            # Check if number of guests exceeds table capacity
            if number_of_guests > table.capacity:
                messages.error(request, f'Table #{table.table_number} only has capacity for {table.capacity} guests.')
                return redirect('table_reservation_form')
            
            # Create the reservation
            TableReservation.objects.create(
                customer=request.user,
                table=table,
                number_of_guests=number_of_guests,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                special_requests=special_requests
            )
            
            messages.success(request, 'Your table reservation has been submitted and is pending confirmation.')
            return redirect('reservations')
            
        except (ValueError, Table.DoesNotExist) as e:
            messages.error(request, f'Error processing your reservation: {str(e)}')
            return redirect('table_reservation_form')
    
    # For GET requests
    min_date = now().date()
    max_date = min_date + timedelta(days=30)  # Allow reservations up to 30 days in advance
    
    return render(request, 'table_reservation_form.html', {
        'tables': tables,
        'min_date': min_date.strftime('%Y-%m-%d'),
        'max_date': max_date.strftime('%Y-%m-%d'),
        'login_form': login_form,
        'register_form': register_form,
    })

@login_required
def cancel_table_reservation(request, reservation_id):
    """Cancel a table reservation"""
    reservation = get_object_or_404(TableReservation, id=reservation_id, customer=request.user)
    
    # Only allow cancellation of pending or confirmed reservations
    if reservation.status in ['pending', 'confirmed']:
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, f'Table reservation for {reservation.reservation_date} has been cancelled.')
    else:
        messages.error(request, f'This reservation cannot be cancelled because it is already {reservation.get_status_display().lower()}.')
    
    return redirect('reservations')

# Admin dashboard views
def is_admin(user):
    """Check if user is an admin or staff member"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard view"""
    # Get statistics for dashboard
    order_count = Order.objects.count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    pending_reservations = Reservation.objects.filter(status='pending').count()
    
    # Get recent orders and reservations
    recent_orders = Order.objects.all().order_by('-order_date', '-order_time')[:5]
    recent_reservations = Reservation.objects.all().order_by('-reservation_date', '-reservation_time')[:5]
    
    return render(request, 'admin/dashboard.html', {
        'order_count': order_count,
        'total_revenue': total_revenue,
        'pending_reservations': pending_reservations,
        'recent_orders': recent_orders,
        'recent_reservations': recent_reservations,
    })

@user_passes_test(is_admin)
def admin_orders(request):
    """Admin orders management view"""
    status = request.GET.get('status', '')
    
    if status:
        orders = Order.objects.filter(status=status).order_by('-order_date', '-order_time')
    else:
        orders = Order.objects.all().order_by('-order_date', '-order_time')
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    return render(request, 'admin/orders.html', {'orders': orders, 'status': status})

@user_passes_test(is_admin)
def admin_update_order_status(request, order_id, status):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)
    
    if status in [s[0] for s in Order.STATUS_CHOICES]:
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {status}")
    else:
        messages.error(request, "Invalid status")
    
    return redirect('admin_orders')

@user_passes_test(is_admin)
def admin_reservations(request):
    """Admin reservations management view"""
    status = request.GET.get('status', '')
    reservation_type = request.GET.get('type', 'all')
    
    # Item reservations
    if status:
        item_reservations = Reservation.objects.filter(status=status).order_by('-reservation_date', '-reservation_time')
    else:
        item_reservations = Reservation.objects.all().order_by('-reservation_date', '-reservation_time')
    
    # Table reservations
    if status:
        table_reservations = TableReservation.objects.filter(status=status).order_by('-reservation_date', '-reservation_time')
    else:
        table_reservations = TableReservation.objects.all().order_by('-reservation_date', '-reservation_time')
    
    # Pagination based on type
    if reservation_type == 'table':
        paginator = Paginator(table_reservations, 10)
        page = request.GET.get('page', 1)
        table_reservations = paginator.get_page(page)
        item_reservations = []
    elif reservation_type == 'item':
        paginator = Paginator(item_reservations, 10)
        page = request.GET.get('page', 1)
        item_reservations = paginator.get_page(page)
        table_reservations = []
    else:  # 'all'
        item_paginator = Paginator(item_reservations, 5)
        table_paginator = Paginator(table_reservations, 5)
        page = request.GET.get('page', 1)
        item_reservations = item_paginator.get_page(page)
        table_reservations = table_paginator.get_page(page)
    
    return render(request, 'admin/reservations.html', {
        'item_reservations': item_reservations,
        'table_reservations': table_reservations,
        'status': status,
        'reservation_type': reservation_type
    })

@user_passes_test(is_admin)
def admin_update_reservation_status(request, reservation_id, status):
    """Update reservation status"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if status in [s[0] for s in Reservation.STATUS_CHOICES]:
        reservation.status = status
        reservation.save()
        messages.success(request, f"Reservation #{reservation.id} status updated to {status}")
    else:
        messages.error(request, f"Invalid status: {status}")
    
    return redirect('admin_reservations')

@user_passes_test(is_admin)
def admin_update_table_reservation_status(request, reservation_id, status):
    """Update table reservation status"""
    reservation = get_object_or_404(TableReservation, id=reservation_id)
    
    if status in [s[0] for s in TableReservation.STATUS_CHOICES]:
        reservation.status = status
        reservation.save()
        messages.success(request, f"Table reservation #{reservation.id} status updated to {status}")
    else:
        messages.error(request, f"Invalid status: {status}")
    
    return redirect('admin_reservations')

@user_passes_test(is_admin)
def admin_items(request):
    """Admin items management view"""
    items = Item.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(items, 10)  # Show 10 items per page
    page = request.GET.get('page', 1)
    items = paginator.get_page(page)
    
    return render(request, 'admin/items.html', {'items': items})

@user_passes_test(is_admin)
def admin_add_item(request):
    """Add new item view"""
    if request.method == 'POST':
        # Process form submission
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        
        item = Item.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            image=image
        )
        
        messages.success(request, f"Item '{item.name}' added successfully")
        return redirect('admin_items')
    
    return render(request, 'admin/add_item.html')

@user_passes_test(is_admin)
def admin_edit_item(request, item_id):
    """Edit item view"""
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        # Process form submission
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.category = request.POST.get('category')
        
        if 'image' in request.FILES:
            item.image = request.FILES.get('image')
        
        item.save()
        
        messages.success(request, f"Item '{item.name}' updated successfully")
        return redirect('admin_items')
    
    return render(request, 'admin/edit_item.html', {'item': item})

@user_passes_test(is_admin)
def admin_delete_item(request, item_id):
    """Delete item"""
    item = get_object_or_404(Item, id=item_id)
    name = item.name
    item.delete()
    
    messages.success(request, f"Item '{name}' deleted successfully")
    return redirect('admin_items')

@user_passes_test(is_admin)
def admin_customers(request):
    """Admin customers management view"""
    search = request.GET.get('search', '')
    
    if search:
        customers = CustomUser.objects.filter(
            Q(username__icontains=search) | 
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        ).order_by('username')
    else:
        customers = CustomUser.objects.all().order_by('username')
    
    # Pagination
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page = request.GET.get('page', 1)
    customers = paginator.get_page(page)
    
    return render(request, 'admin/customers.html', {'customers': customers, 'search': search})

@user_passes_test(is_admin)
def admin_customer_detail(request, customer_id):
    """View customer details"""
    customer = get_object_or_404(CustomUser, id=customer_id)
    orders = Order.objects.filter(customer=customer).order_by('-order_date', '-order_time')
    reservations = Reservation.objects.filter(customer=customer).order_by('-reservation_date', '-reservation_time')
    
    context = {
        'customer': customer,
        'orders': orders,
        'reservations': reservations,
    }
    
    return render(request, 'admin/customer_detail.html', context)

@user_passes_test(is_admin)
def admin_payments(request):
    """Admin payments management view"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    payments = Payment.objects.all().order_by('-payment_date')
    
    # Filter by date range if provided
    if start_date and end_date:
        payments = payments.filter(payment_date__range=[start_date, end_date])
    
    # Calculate total amount
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Pagination
    paginator = Paginator(payments, 10)  # Show 10 payments per page
    page = request.GET.get('page', 1)
    payments = paginator.get_page(page)
    
    context = {
        'payments': payments,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount,
    }
    
    return render(request, 'admin/payments.html', context)

@user_passes_test(is_admin)
def admin_payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    return render(request, 'admin/payment_detail.html', {'payment': payment})
