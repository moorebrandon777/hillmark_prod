from django.shortcuts import render,redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone


from django.views.generic import CreateView, ListView

from .models import Transaction
from account.models import UserBankAccount
from . import forms, constants
from . import emailsend


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context
    

class DepositMoneyView(TransactionCreateMixin):
    form_class = forms.DepositForm
    title = 'Fund Customer Account'
    success_url = reverse_lazy('transactions:deposit_money')

    def get_initial(self):
        initial = {'transaction_type': constants.CREDIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        customer_account = form.cleaned_data.get('account')
        if form.is_valid():
            account = UserBankAccount.objects.get(account_no=customer_account.account_no)
            transaction = form.save(commit=False)
            transaction.balance_after_transaction = account.balance + amount
            transaction.status = constants.SUCCESSFUL
            transaction.save()
            account.balance += amount
            account.save(
                update_fields=[
                    'balance',
                ]
            )

            messages.success(
                self.request,
                f'{amount}{account.currency} has been deposited successfully to this account'
            )

        return super().form_valid(form)
    

class WithdrawMoneyView(TransactionCreateMixin):
    form_class = forms.WithdrawForm
    title = 'Debit Customer Account'
    success_url = reverse_lazy('transactions:withdraw_money')

    def get_initial(self):
        initial = {'transaction_type': constants.DEBIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        customer_account = form.cleaned_data.get('account')
        if form.is_valid():
            account = UserBankAccount.objects.get(account_no=customer_account.account_no)
            transaction = form.save(commit=False)
            transaction.balance_after_transaction = account.balance - amount
            transaction.status = constants.SUCCESSFUL
            transaction.save()
            account.balance -= amount
            account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {amount}{account.currency} from this account'
        )

        return super().form_valid(form)


class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/all_transactions.html'
    context_object_name = 'transactions'


def delete_transaction(request, pk):
    transaction =  Transaction.objects.get(pk=pk)
    account = UserBankAccount.objects.get(account_no=transaction.account.account_no)
    if transaction.transaction_type == 'DR':
        if transaction.status == 'Failed':
            transaction.delete()
        else:
            account.balance += transaction.amount
            account.save()
            transaction.delete()
    else:
        if transaction.status == 'Failed':
            transaction.delete()
        else:  
            account.balance -= transaction.amount 
            account.save()
            transaction.delete()
        messages.success(request, 'Transaction was deleted successfully')
    return redirect('transactions:all_transactions')


class CustomerTransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/customer_transfer.html'
    model = Transaction
    # success_url = reverse_lazy('transactions:customer_transfer')

    # def get_success_url(self):
    #     customer_id =self.kwargs['pk']
    #     return reverse_lazy('account:admin_customer_detail', kwargs={'pk': customer_id})

    def get_success_url(self):
        if self.request.user.account.is_success:
            return reverse_lazy('transactions:transaction_successful')
        else:
            return reverse_lazy('transactions:transaction_failed')
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    

class CustomerWithdrawMoneyView(CustomerTransactionCreateMixin):
    form_class = forms.CustomerTransactionForm

    def get_initial(self):
        initial = {'transaction_type': constants.DEBIT, 'transaction_date':timezone.now().date(),
                   'transaction_time':timezone.now().time()}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        pin = form.cleaned_data.get('description')

        if form.is_valid():
            if int(pin) == self.request.user.account.transfer_pin:
                if self.request.user.account.is_success:
                    data = form.save(commit=False)
                    data.status = constants.SUCCESSFUL
                    data.save()
                    self.request.user.account.balance -= amount
                    self.request.user.account.save(update_fields=['balance'])
                    self.request.session['pk'] = data.pk

                    message = render_to_string('emails/transaction_successful_email.html',{
                                'name':self.request.user.get_full_name,
                                'date': data.transaction_date,
                                'account_number':data.beneficiary_account,
                                'amount':f'{data.amount} {data.account.currency}',
                                'balance':f'{data.balance_after_transaction} {data.account.currency}',
                            })
                    try:
                        emailsend.email_send('Transaction Successful', message, self.request.user.email)
                    except:
                        pass
                else:
                    data = form.save(commit=False)
                    data.status = constants.FAILED
                    data.save()
                    self.request.session['pk'] = data.pk
            else:
                messages.success(
                    self.request,
                    f'Your transfer pin is incorrect, please check and try again'
                )
                return self.render_to_response(self.get_context_data(form=form))
              

        return super().form_valid(form)
    

def transaction_failed(request):
    pk = request.session.get('pk')
    try:
        transaction = Transaction.objects.get(pk=pk)
    except:
        return redirect('account:customer_dashboard')

    context = {'transaction':transaction}
    request.session.modified = True
    return render(request, 'transactions/transaction_failed.html', context)


def transaction_successful(request):
    pk = request.session.get('pk')
    try:
        transaction = Transaction.objects.get(pk=pk)
    except:
        return redirect('account:customer_dashboard')

    context = {'transaction':transaction}
    request.session.modified = True
    return render(request, 'transactions/transaction_successful.html', context)