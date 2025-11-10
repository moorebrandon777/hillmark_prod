from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

from .models import UserBankAccount, RequiredCode, UserCodes




class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Acc.-No. Or Email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-3'})


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-3'})


class UserBankAccountForm(forms.ModelForm):
    class Meta:
        model = UserBankAccount
        fields = ('account_type', 'currency', 'street_address', 'city', 'country', 'postal_code', 'picture', 'transfer_pin')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-3'})


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-3'})


class RequiredCodeForm(forms.ModelForm):
    class Meta:
        model = RequiredCode
        fields = ['code_name', 'code_number']
        # fields = ['code_name', 'code_number', 'is_active', 'user']

    def __init__(self, *args, **kwargs):
        super(RequiredCodeForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to each field
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'


class UserCodeForm(forms.ModelForm):
    class Meta:
        model = UserCodes
        fields = ['tax_code', 'imf_code', 'insurance_code']
        # fields = ['code_name', 'code_number', 'is_active', 'user']

    def __init__(self, *args, **kwargs):
        super(UserCodeForm, self).__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' class to each field
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'