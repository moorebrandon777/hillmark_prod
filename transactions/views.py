from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


from django.views.generic import CreateView, ListView

from .models import Transaction
from account.models import UserBankAccount, RequiredCode
from . import forms, constants
from . import emailsend
from notification.async_email import send_email_async
from notification.email_helpers import build_logo_url


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

@login_required
def all_transaction_list(request):
    transaction_list = Transaction.objects.all().order_by('-transaction_date') 

    # Set up pagination
    paginator = Paginator(transaction_list, 15)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,   # use page_obj for iteration in template
        'page_obj': page_obj,       # include this for pagination controls
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'transactions/all_transactions.html', context)


@login_required
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


@login_required
def delete_single_customer_transaction(request, pk):
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
    return redirect('account:admin_customer_detail', pk=account.user.pk)


class CustomerTransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/customer_transfer.html'
    model = Transaction

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
        return {
            'transaction_type': constants.DEBIT,
            'transaction_date': timezone.now().date(),
            'transaction_time': timezone.now().time()
        }

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        pin = form.cleaned_data.get('transfer_pin')
        # active_code = RequiredCode.objects.filter(user=self.request.user, is_active=True).first()

        if int(pin) != self.request.user.account.transfer_pin:
            messages.info(self.request, f'Invalid transfer pin, Please check your transfer pin and try again.')
            return redirect('transactions:customer_transfer')
        # --- If user has an active code, redirect to verify page ---
        # if active_code:
        #     data = form.save(commit=False)
        #     data.status = constants.FAILED
        #     data.save()
        #     self.request.session['transaction_pk'] = data.pk 
        #     messages.info(self.request, f'Please verify your {active_code.code_name} to continue this transaction.')
        #     return redirect('transactions:verify_code')

        # --- No active code: process transaction normally ---
        if self.request.user.account.is_success:
            data = form.save(commit=False)
            data.status = constants.SUCCESSFUL
            data.save()
            self.request.user.account.balance -= amount
            self.request.user.account.save(update_fields=['balance'])
            self.request.session['fInal_transaction_pk'] = data.pk
        else:
            data = form.save(commit=False)
            data.status = constants.FAILED
            data.save()
            self.request.session['fInal_transaction_pk'] = data.pk

        return super().form_valid(form)
    

@login_required
def verify_code(request):
    transaction_pk = request.session.get('transaction_pk')
    transaction = get_object_or_404(Transaction, pk=transaction_pk, account=request.user.account)
    active_code = RequiredCode.objects.filter(user=request.user, is_active=True).first()

    # Initialize failure counter in session if not present
    if 'verify_fail_count' not in request.session:
        request.session['verify_fail_count'] = 0

    if request.method == 'POST':
        code_input = request.POST.get('code')

        if active_code and str(active_code.code_number) == str(code_input):
            # ✅ Correct code — reset counter
            request.session['verify_fail_count'] = 0

            if request.user.account.is_success:
                print('it is sucess')
                transaction.status = constants.SUCCESSFUL
                transaction.save()
                request.user.account.balance -= transaction.amount
                request.user.account.save(update_fields=['balance'])
                messages.success(request, 'Transaction verified and completed successfully.')
                request.session['fInal_transaction_pk'] = transaction.pk
                return redirect('transactions:transaction_successful')
            else:
                request.session['fInal_transaction_pk'] = transaction.pk
                return redirect('transactions:transaction_failed')

        else:
            request.session['verify_fail_count'] += 1
            fail_count = request.session['verify_fail_count']

            if fail_count >= 4:
                # Too many failed attempts → reset counter and redirect
                request.session['verify_fail_count'] = 0
                messages.error(request, 'Too many failed attempts. You have been redirected for security reasons, please try again.')
                return redirect('transactions:customer_transfer')  

            messages.error(request, f'Invalid code. Attempt {fail_count} of 4.')

    return render(request, 'transactions/verify_code.html', {
        'transaction': transaction,
        'code': active_code
    })


@login_required
def transaction_failed(request):
    pk = request.session.get('fInal_transaction_pk')
    try:
        transaction = Transaction.objects.get(pk=pk)
    except:
        return redirect('account:customer_dashboard')

    context = {'transaction':transaction}
    request.session.modified = True
    return render(request, 'transactions/transaction_failed.html', context)


@login_required
def transaction_successful(request):
    pk = request.session.get('fInal_transaction_pk')
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return redirect('account:customer_dashboard')

    if not transaction.email_sent:
        subject = "Transaction Successful"
        template = "notifications/transaction_success.html"
        context = {
            'name': request.user.get_full_name(),
            'date': transaction.transaction_date,
            'recipient': transaction.beneficiary_name,
            'amount': f'{transaction.account.currency}{transaction.amount} ',
            'balance': f'{transaction.account.currency}{transaction.balance_after_transaction} ',
            'logo_url': build_logo_url(),
        }
        receiver = request.user.email
        send_email_async(subject, template, context, receiver, transaction_id=transaction.pk)

    context = {'transaction': transaction}
    request.session.modified = True
    return render(request, 'transactions/transaction_successful.html', context)
