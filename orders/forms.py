from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ['name','email','phone','choice','date_needed','details']
        widgets = {
            'date_needed': forms.DateInput(attrs={'type':'date'}),
        }

