PAYMENT_CONSTANTS = dict(
    status=[(0, "SUCCESSFUL"), (1, "FAILED"), (2, "IN_PROGRESS"), (3, "DECLINED")],
    values=dict(
        status=dict(SUCCESSFUL=0, FAILED=1, IN_PROGRESS=2, DECLINED=3),
    ),
)
APPLICATION_CONSTANTS = dict(transaction=PAYMENT_CONSTANTS)
