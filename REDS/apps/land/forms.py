from django import forms
from .models import Landlord, LandContract, ContractPaymentSchedule

class LandlordForm(forms.ModelForm):
    class Meta:
        model  = Landlord
        fields = [
            'name', 'name_urdu', 'cnic',
            'phone', 'address', 'city'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'name_urdu': forms.TextInput(attrs={
                'dir': 'rtl', 'class': 'urdu-input'
            }),
        }


class LandContractForm(forms.ModelForm):
    class Meta:
        model  = LandContract
        fields = [
            'landlord', 'title', 'location',
            'total_area', 'area_unit', 'total_amount',
            'contract_type', 'start_date', 'duration_years',
            'status', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'location':   forms.Textarea(attrs={'rows': 2}),
            'notes':      forms.Textarea(attrs={'rows': 2}),
        }


class PaymentScheduleForm(forms.ModelForm):
    class Meta:
        model  = ContractPaymentSchedule
        fields = [
            'paid_date', 'paid_amount', 'payment_mode',
            'bank_account', 'cheque_no', 'cheque_bank',
            'cheque_status', 'narration'
        ]
        widgets = {
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
            'narration': forms.Textarea(attrs={'rows': 2}),
        }