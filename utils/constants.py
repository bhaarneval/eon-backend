PAYMENT_CONSTANTS = dict(
    status=[(0, "SUCCESSFUL"), (1, "FAILED"), (2, "IN_PROGRESS"), (3, "DECLINED")],
    type=[(0, "CREDIT"), (1, "DEBIT")],
    values=dict(
        type=dict(CREDIT=0, DEBIT=1),
        status=dict(SUCCESSFUL=0, FAILED=1, IN_PROGRESS=2, DECLINED=3),
    ),
)
APPLICATION_CONSTANTS = dict(transaction=PAYMENT_CONSTANTS)
