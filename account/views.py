import math
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

from .models import CustomUser, UserBankAccount, RequiredCode
from .forms import UserUpdateForm, UserBankAccountForm, UserCodeForm
from transactions.models import Transaction
from .models import UserCodes

# Optional helper: only admins or staff can access
def is_admin(user):
    return user.is_staff or user.is_superuser

# admin part
class AdminDashboardView(ListView):
    model = CustomUser
    template_name = 'account/admin/admin_dashboard.html'
    context_object_name = 'customers'
    paginate_by = 9  

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponse("Error handler content", status=400)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = super(AdminDashboardView, self).get_queryset()
        return qs.filter(is_staff=False).order_by('-date_created') 
    

class CustomerDetailsAdminView(DetailView):
    model = CustomUser
    template_name = 'account/admin/admin_customer_details.html'
    context_object_name = 'customer'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponse("Error handler content", status=400)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(CustomerDetailsAdminView, self).get_context_data(**kwargs)
        context['account'] = UserBankAccount.objects.get(user=self.object)
        context['transactions'] = Transaction.objects.filter(account=self.object.account)
        return context


@login_required
def activate_and_deactivate_customer_account(request, pk):
    customer = CustomUser.objects.get(pk=pk)
    if not customer.is_activated:
        customer.is_activated = True
        customer.save()
        messages.success(request, "Account is Activated")
    else:
        customer.is_activated = False
        customer.save()
        messages.success(request, "Account is Deactivated")
    return redirect('account:admin_customer_detail', pk=pk)


@login_required
def admin_transaction_success_or_fail(request, pk):
    customer = CustomUser.objects.get(pk=pk)
    account = UserBankAccount.objects.get(user=customer)
    if not account.is_success:
        account.is_success = True
        account.save()
        messages.success(request, "Transactions for this customer will be successfull")
    else:
        account.is_success = False
        account.save()
        messages.success(request, "Transactions for this customer will fail")
    return redirect('account:admin_customer_detail', pk=pk)


class UpdateCustomerView(UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    second_form_class = UserBankAccountForm
    template_name = 'account/admin/admin_customer_update.html'

    def get_success_url(self):
        customer_id =self.kwargs['pk']
        return reverse_lazy('account:admin_customer_detail', kwargs={'pk': customer_id})

    def get_context_data(self, **kwargs): 
        kwargs['active_client'] = True

        if 'form' not in kwargs:
            kwargs['form'] = self.form_class(instance=self.get_object())
        if 'form2' not in kwargs:
            kwargs['form2'] =  self.second_form_class(instance=self.get_object().account)
        return super(UpdateCustomerView, self).get_context_data(**kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.get_object())
        form2 = self.second_form_class(request.POST, request.FILES, instance=self.get_object().account)

        if form.is_valid() and form2.is_valid():
            form.save()
            form2.save()
            messages.success(self.request, 'Account was updated successfully')
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
              self.get_context_data(form=form, form2=form2))
        

@login_required
@user_passes_test(is_admin)
def admin_change_customer_password(request, pk):
    if request.method == 'POST':
        customer = CustomUser.objects.get(pk=pk)
        password_one = request.POST.get('password1')
        password_two = request.POST.get('password1')
        
        if password_one != password_two:
            messages.error(request, 'The two password does not match, check it and try again')
        else:
            customer.set_password(password_one)
            customer.save()
            messages.error(request, "Customer's password was changed successfully")
        return redirect('account:admin_customer_detail', pk=pk)


@login_required
@user_passes_test(is_admin)
def admin_delete_customer(request, pk):
    customer = CustomUser.objects.get(pk=pk)
    customer.delete()
    messages.success(request, 'customer was deleted successfully')
    return redirect('account:admin_dashboard')


@login_required
@user_passes_test(is_admin)
def activate_customer_is_progressed(request, pk):
    customer = CustomUser.objects.get(pk=pk)
    if not customer.is_progressed:
        customer.is_progressed = True
        customer.save()
        messages.success(request, "Customer activated for progress bar")
    else:
        customer.is_progressed = False
        customer.save()
        messages.success(request, "Customer deactivated for progress bar")
    return redirect('account:admin_customer_detail', pk=pk)


@login_required
@user_passes_test(is_admin)
def create_required_code(request, pk):
    customer = CustomUser.objects.get(pk=pk)
    
    # Try to get existing user codes (if they exist)
    try:
        user_codes = customer.transfer_codes
        has_codes = True
    except UserCodes.DoesNotExist:
        user_codes = None
        has_codes = False

    if request.method == 'POST':
        # If the user already has codes, prevent creating another
        if has_codes:
            messages.warning(request, "This user already has required codes. You can only update them.")
            return redirect('account:create_required_code', pk=pk)

        form = UserCodeForm(request.POST)
        if form.is_valid():
            required_code = form.save(commit=False)
            required_code.user = customer
            required_code.save()
            messages.success(request, 'Required codes created successfully.')
            return redirect('account:create_required_code', pk=pk)
    else:
        form = UserCodeForm()

    return render(
        request,
        'account/admin/add_use_code.html',
        {
            'form': form,
            'customer': customer,
            'user_codes': user_codes,
            'has_codes': has_codes,
        }
    )


# @login_required
# @user_passes_test(is_admin)
# def activate_code(request, pk):
#     code = get_object_or_404(RequiredCode, pk=pk)

#     RequiredCode.objects.filter(user=code.user).exclude(pk=pk).update(is_active=False)

#     code.is_active = True
#     code.save()

#     messages.success(request, f"Activated code '{code.code_name}' for customer {code.user.get_full_name()}.")
#     return redirect('account:create_required_code', pk=code.user.pk)


# @login_required
# @user_passes_test(is_admin)
# def deactivate_code(request, pk):
#     code = get_object_or_404(RequiredCode, pk=pk)

#     code.is_active = False
#     code.save()

#     messages.info(request, f"Deactivated code '{code.code_name}' for customer {code.user.get_full_name()}.")
#     return redirect('account:create_required_code', pk=code.user.pk)


@login_required
@user_passes_test(is_admin)
def delete_code(request, pk):
    code = get_object_or_404(UserCodes, pk=pk)
    # code_name = code.code_name
    username = code.user.get_full_name()

    code.delete()

    messages.warning(request, f"Code for customer {username} has been deleted.")
    return redirect('account:create_required_code', pk=code.user.pk)

# customer part
class CustomerDashboardView(TemplateView):
    template_name = 'account/customer/customer_dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CustomerDashboardView, self).get_context_data(*args, **kwargs)
        context['account'] = UserBankAccount.objects.get(user=self.request.user)
        context['ledger_balance'] = context['account'].balance - 2500
        customer_transactions = Transaction.objects.filter(account=self.request.user.account)
        context['transactions'] = customer_transactions[:7]
        
        # getting transactions by transaction type
        deposits = customer_transactions.filter(transaction_type='CR')
        withdraws = customer_transactions.filter(transaction_type='DR')

        # summing transaction types amount filter and all transactions amount
        context['deposit_sum'] = sum(transaction.amount for transaction in deposits)
        context['withdraw_sum'] = sum(transaction.amount for transaction in withdraws)
        sum_all_transactions = sum(transaction.amount for transaction in customer_transactions)

        # getting depbit and credit percents
        context['deposit_percent'] = math.floor((context['deposit_sum'] * 100) / sum_all_transactions) if context['deposit_sum']  !=0 and sum_all_transactions !=0 else 0

        context['withdraw_percent'] = math.ceil((context['withdraw_sum'] * 100) / sum_all_transactions) if context['withdraw_sum']  !=0 and sum_all_transactions !=0 else 0
        return context


class CustomerCareView(TemplateView):
    template_name = 'account/customer/customer_care.html'

    def post(self, request, *args, **kwargs):
        name = self.request.POST.get('name')
        email = self.request.POST.get('email')
        subject = self.request.POST.get('subject')
        message = self.request.POST.get('message')
        final_message = render_to_string('emails/customer_care_email.html', 
        {
            'name': name,
            'email': email,
            'message': message,
            'subject': subject
        })
        try:
            send_mail(
                'Email From '+name,
                final_message,
                settings.EMAIL_HOST_USER,
                ['contact@hillmarkonline.com'],
                fail_silently=False,
            )
            messages.success(self.request, 'Email sent successfully, we will get back to you as soon as possible')
        except:
            messages.error(self.request, 'There was an error while trying to send your email, please try again')

        finally:
            return HttpResponseRedirect(reverse_lazy('account:customer_care'))
        

class CustomerEwalleteView(TemplateView):
    template_name = 'account/customer/customer_ewallet.html'


class CustomerSettingsView(TemplateView):
    template_name = 'account/customer/customer_settings.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CustomerSettingsView, self).get_context_data(*args, **kwargs)
        context['account'] = UserBankAccount.objects.get(user=self.request.user)
        return context
    

class CustomerAllTransactionsView(ListView):
    model = Transaction
    template_name = 'account/customer/customer_all_transactions.html'
    context_object_name = 'transactions'
    paginate_by = 12  

    def get_queryset(self):
        return super().get_queryset().filter(account=self.request.user.account).order_by('-transaction_date')
    

@login_required
def check_code(request):
    if request.method == "POST":
        code_type = request.POST.get("code_type")
        entered_code = request.POST.get("code")

        try:
            user_codes = UserCodes.objects.get(user=request.user)
        except UserCodes.DoesNotExist:
            return JsonResponse({"valid": False, "message": "No codes found for user."})

        # Get the right code field
        actual_code = getattr(user_codes, f"{code_type}_code", None)

        if actual_code and entered_code == actual_code:
            return JsonResponse({"valid": True})
        else:
            return JsonResponse({"valid": False, "message": "Invalid code."})
    
    return JsonResponse({"error": "Invalid request method."})

        