from django import forms
from .models import Coupon, Product
from django.utils import timezone
import random
import string

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'active', 'usage_limit']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BulkDiscountForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        label="Nombre de la Oferta", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Oferta Verano 2025'})
    )
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Seleccionar Productos"
    )
    discount_percentage = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        label="Porcentaje de Descuento",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    action = forms.ChoiceField(
        choices=[('apply', 'Aplicar Descuento'), ('remove', 'Quitar Descuento')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Acción"
    )

class CouponGenerationForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100, label="Cantidad de Cupones", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    discount_percentage = forms.IntegerField(min_value=1, max_value=100, label="Porcentaje de Descuento", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valid_days = forms.IntegerField(min_value=1, label="Días de Validez", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    usage_limit = forms.IntegerField(min_value=0, initial=1, label="Límite de Uso (0 = ilimitado)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    prefix = forms.CharField(max_length=10, required=False, label="Prefijo (Opcional)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    batch_name = forms.CharField(max_length=100, required=False, label="Nombre del Lote", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cupones Navidad'}))

    def generate_coupons(self):
        quantity = self.cleaned_data['quantity']
        discount = self.cleaned_data['discount_percentage']
        days = self.cleaned_data['valid_days']
        limit = self.cleaned_data['usage_limit']
        prefix = self.cleaned_data['prefix'] or "GEN"
        
        created_coupons = []
        now = timezone.now()
        valid_to = now + timezone.timedelta(days=days)
        
        for _ in range(quantity):
            # Generate random code
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            code = f"{prefix}-{random_str}"
            
            # Ensure uniqueness (simple check)
            while Coupon.objects.filter(code=code).exists():
                random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                code = f"{prefix}-{random_str}"
            
            coupon = Coupon.objects.create(
                code=code,
                discount_percentage=discount,
                valid_from=now,
                valid_to=valid_to,
                usage_limit=limit,
                active=True
            )
            created_coupons.append(coupon)
            
        return created_coupons
