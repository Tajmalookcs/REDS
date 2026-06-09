from django import forms
from .models import BusinessProfile, BankAccount


class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            'company_name',
            'company_name_urdu',
            'logo',
            'address',
            'address_urdu',
            'city',
            'phone',
            'email',
            'ntn_number',
            'strn_number',
        ]


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = [
            'title',
            'bank_name',
            'account_no',
            'branch',
            'opening_balance',
            'is_active',
        ]
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
