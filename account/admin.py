from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm



from .models import CustomUser, BankAccountType, UserBankAccount


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'account_number', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'account_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'last_login','is_activated', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('first_name', 'last_name',  'account_number', 'email', 'password1', 'password2')}),
    )
    search_fields = ('email', 'first_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['email'].disabled = True
        return form

admin.site.register(CustomUser, UserAdmin)
admin.site.register(BankAccountType)
admin.site.register(UserBankAccount)