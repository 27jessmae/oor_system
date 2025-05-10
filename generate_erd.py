import os
import sys
import django
from django.apps import apps
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sscoffee.settings')
django.setup()

# Import models
from core.models import (
    CustomUser, AdminProfile, Customer, Category, Item, 
    Order, OrderItem, Reservation, Payment, Table, TableReservation
)

def generate_erd_text():
    """Generate a text-based ERD representation"""
    models = [
        CustomUser, AdminProfile, Customer, Category, Item, 
        Order, OrderItem, Reservation, Payment, Table, TableReservation
    ]
    
    erd_text = "# SSCoffee System ERD\n\n"
    
    for model in models:
        model_name = model.__name__
        erd_text += f"## {model_name}\n"
        
        # Get fields
        fields = []
        for field in model._meta.fields:
            field_type = field.get_internal_type()
            field_name = field.name
            
            # Check if it's a foreign key
            if field_type == 'ForeignKey':
                related_model = field.remote_field.model.__name__
                fields.append(f"- {field_name} -> {related_model}")
            else:
                fields.append(f"- {field_name}: {field_type}")
        
        erd_text += "\n".join(fields) + "\n\n"
    
    # Add relationships section
    erd_text += "## Relationships\n\n"
    
    for model in models:
        model_name = model.__name__
        
        for field in model._meta.fields:
            if field.get_internal_type() == 'ForeignKey':
                related_model = field.remote_field.model.__name__
                field_name = field.name
                erd_text += f"- {model_name}.{field_name} -> {related_model}\n"
    
    return erd_text

if __name__ == "__main__":
    erd_text = generate_erd_text()
    
    # Write to file
    with open('sscoffee_erd.md', 'w') as f:
        f.write(erd_text)
    
    print("ERD text generated and saved to sscoffee_erd.md")
    print("To generate a visual ERD, install django-extensions and run:")
    print("python manage.py graph_models -a -g -o sscoffee_erd.png")
