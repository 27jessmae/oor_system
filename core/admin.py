# core/admin.py
from django.contrib             import admin
from django.contrib.auth.admin  import UserAdmin as DjangoUserAdmin
from .models                    import (
    CustomUser, AdminProfile, Customer, Category,
    Item, Order, OrderItem, Reservation, Payment
)

@admin.register(CustomUser)
class CustomUserAdmin(DjangoUserAdmin):
    list_display  = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter   = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user')
    search_fields = ('user__username', 'user__email')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user')
    search_fields = ('user__username', 'user__email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name')
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display     = ('id', 'name', 'category', 'price')
    search_fields    = ('name', 'description')
    list_filter      = ('category',)
    def has_add_permission(self, request):    return request.user.is_staff or request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_staff or request.user.is_superuser
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = (
        'id', 'customer', 'item', 'quantity',
        'total_amount', 'order_date', 'order_time'
    )
    search_fields = ('customer__username', 'item__name')
    list_filter   = ('order_date',)

    def total_amount(self, obj):
        return obj.get_total
    total_amount.short_description    = 'Total Amount'
    total_amount.admin_order_field   = 'item__price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ('id', 'order', 'item', 'quantity')
    search_fields = ('order__id', 'item__name')
    list_filter   = ('item',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'customer', 'item', 'reservation_date', 'status')
    search_fields = ('customer__username', 'item__name')
    list_filter   = ('status', 'reservation_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'order', 'amount', 'payment_date')
    search_fields = ('order__id',)
    list_filter   = ('payment_date',)
