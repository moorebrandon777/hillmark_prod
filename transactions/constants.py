DEBIT = 'DR'
CREDIT = 'CR'

TRANSACTION_TYPE_CHOICES = (
    (DEBIT, 'Debit'),
    (CREDIT, 'Credit'),
)


# PENDING = 'Pending'
SUCCESSFUL = 'Successful'
FAILED = 'Failed'

STATUS_CHOICES = (
    # (PENDING, 'Pending'),
    (SUCCESSFUL, 'Successful'),
    (FAILED, 'Failed')
)