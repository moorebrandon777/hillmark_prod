import random
from django.db import models
from django.db.models.signals import post_save

from account.models import UserBankAccount
from . import constants


class Transaction(models.Model):
	account = models.ForeignKey(UserBankAccount, related_name='transactions', on_delete=models.CASCADE)
	beneficiary_name = models.CharField(max_length=200)
	beneficiary_account = models.CharField(max_length=50, null=True, blank=True)
	beneficiary_bank = models.CharField(max_length=200, blank=True)
	iban_number = models.CharField(max_length=100, blank=True)
	ref_code = models.CharField(max_length=20, null=True, blank=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
	description = models.CharField(max_length=200, blank=True)
	transaction_type = models.CharField(max_length=20, choices=constants.TRANSACTION_TYPE_CHOICES)
	status = models.CharField(max_length=20, choices=constants.STATUS_CHOICES)
	transaction_date = models.DateField(null=True)
	transaction_time = models.TimeField(null=True)

	class Meta:
		ordering = ['-transaction_date', '-transaction_time']

	def __str__(self):
		return self.beneficiary_name
	

def route_code_post_save(sender, instance, created,*args, **kwargs):
	if created:
		nums = range(1111111, 9999999)
		f_nums = random.choices(nums, k=1)
		r = f_nums[0]
		new_ref = str(int(r) + instance.id)[3:11]
		instance.ref_code = f'REF-HMOB{new_ref}X3Y'
		instance.save()

post_save.connect(route_code_post_save, sender=Transaction)
