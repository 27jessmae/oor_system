# SSCoffee System ERD

## CustomUser
- id: BigAutoField
- password: CharField
- last_login: DateTimeField
- is_superuser: BooleanField
- username: CharField
- first_name: CharField
- last_name: CharField
- email: CharField
- is_staff: BooleanField
- is_active: BooleanField
- date_joined: DateTimeField

## AdminProfile
- id: BigAutoField
- user: OneToOneField

## Customer
- id: BigAutoField
- user: OneToOneField

## Category
- id: BigAutoField
- name: CharField

## Item
- id: BigAutoField
- name: CharField
- description: TextField
- price: DecimalField
- image: FileField
- category: CharField

## Order
- id: BigAutoField
- item -> Item
- customer -> CustomUser
- quantity: PositiveIntegerField
- order_date: DateField
- order_time: TimeField
- status: CharField

## OrderItem
- id: BigAutoField
- order -> Order
- item -> Item
- quantity: PositiveIntegerField

## Reservation
- id: BigAutoField
- customer -> CustomUser
- item -> Item
- quantity: PositiveIntegerField
- reservation_date: DateField
- reservation_time: TimeField
- status: CharField

## Payment
- id: BigAutoField
- order -> Order
- amount: DecimalField
- payment_date: DateField

## Table
- id: BigAutoField
- table_number: PositiveIntegerField
- capacity: PositiveIntegerField
- is_available: BooleanField

## TableReservation
- id: BigAutoField
- customer -> CustomUser
- table -> Table
- number_of_guests: PositiveIntegerField
- reservation_date: DateField
- reservation_time: TimeField
- special_requests: TextField
- status: CharField
- created_at: DateTimeField

## Relationships

- Order.item -> Item
- Order.customer -> CustomUser
- OrderItem.order -> Order
- OrderItem.item -> Item
- Reservation.customer -> CustomUser
- Reservation.item -> Item
- Payment.order -> Order
- TableReservation.customer -> CustomUser
- TableReservation.table -> Table
