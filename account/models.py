import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomAccountManager
from django.db.models.signals import post_save




class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    account_number = models.CharField(_('account_number'),max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_activated = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['account_number']
    
    class Meta:
       ordering = ['-date_created']
    

    def __str__(self):
        return self.first_name +' '+self.email
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'  


def user_account_number_post_save(sender, instance, created,*args, **kwargs):
	if created:
		nums = range(111111, 999999)
		f_nums = random.choices(nums, k=1)
		r = f_nums[0]
		r_new = int(r) + instance.id
		instance.account_number = str(r_new)[5:15]
		instance.save()

post_save.connect(user_account_number_post_save, sender=CustomUser)


class BankAccountType(models.Model):
	name = models.CharField(max_length=128)
	maximum_withdraw = models.DecimalField(decimal_places=2, max_digits=12)
	minimum_withdraw = models.DecimalField(decimal_places=2, max_digits=12)

	def __str__(self):
		return self.name
	

class UserBankAccount(models.Model):
	CURRENCY_CHOICE = (
        ("$", "USD"),
        ("£", "Pounds"),
        ("€", "Euro"),
    )
	
	user = models.OneToOneField(CustomUser, related_name='account', on_delete=models.CASCADE)
	account_no = models.CharField(max_length=30, null=True, blank=True)
	account_type = models.ForeignKey(BankAccountType,related_name='accounts', on_delete=models.CASCADE)
	currency = models.CharField(max_length=4, choices=CURRENCY_CHOICE)
	balance = models.DecimalField(default=0, decimal_places=2, max_digits=12)
	street_address = models.CharField(max_length=512)
	city = models.CharField(max_length=256)
	postal_code = models.CharField(max_length=30, null=True, blank=True)
	country = models.CharField(max_length=100)
	is_success = models.BooleanField(default=False)
	transfer_pin = models.IntegerField()
	picture = models.FileField(upload_to='profile_pictures', default='default-img.jpg')

	def __str__(self):
		return str(self.user.first_name)

