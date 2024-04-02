from django import forms

from .models import Transaction
from account.models import UserBankAccount


class DateInput(forms.DateInput):
	input_type = 'date'

class TimeInput(forms.TimeInput):
	input_type = 'time'

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'account','amount', 'beneficiary_name', 'beneficiary_account',
            'beneficiary_bank', 'iban_number', 'description',
            'transaction_type', 'transaction_date', 'transaction_time'
        ]

    def __init__(self, *args, **kwargs):
        # self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['transaction_date'].widget = DateInput()
        self.fields['transaction_time'].widget = TimeInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        # self.instance.account = self.account
        # self.instance.balance_after_transaction = self.account.balance
        return super().save()

    
    

class DepositForm(TransactionForm):
    

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        min_deposit_amount = 500

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You can not deposit less than {min_deposit_amount}{self.account.currency}'
            )

        return amount
    

class WithdrawForm(TransactionForm):

    def clean_amount(self):
        customer_account = self.cleaned_data.get('account')
        account = UserBankAccount.objects.get(account_no=customer_account.account_no)
        min_withdraw_amount = account.account_type.minimum_withdraw
        max_withdraw_amount = (
            account.account_type.maximum_withdraw
        )
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can not withdraw less than {account.currency}{min_withdraw_amount}'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can not withdraw more than {account.currency}{max_withdraw_amount}'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} {account.currency} in this account. '
                'You can not withdraw more than the account balance'
            )

        return amount
    

class CustomerTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'amount', 'beneficiary_name', 'beneficiary_account',
            'beneficiary_bank', 'iban_number', 'description',
            'transaction_type', 'transaction_date', 'transaction_time'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['transaction_date'].disabled = True
        self.fields['transaction_date'].widget = forms.HiddenInput()
        self.fields['transaction_time'].disabled = True
        self.fields['transaction_time'].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = account.account_type.minimum_withdraw
        max_withdraw_amount = (
            account.account_type.maximum_withdraw
        )
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can not transfer less than {account.currency}{min_withdraw_amount}'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can not transfer more than {account.currency}{max_withdraw_amount}'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} {account.currency} in your account. '
                'You can not transfer more than the account balance'
            )

        return amount