from django.db import models


class Status(models.TextChoices):
    NEW = '1', 'New'
    PROCESSING = '2', 'Processing'
    APPROVAL_AWAIT = '3', 'Processing (await for approval of the board)'
    PAYMENT_AWAIT = '4', 'Await for the payment date'
    REJECTED = '5', 'Rejected'
    FINISHED = '6', 'Finished'


class Priority(models.TextChoices):
    LOW = '1', 'Low'
    MIDDLE = '2', 'Middle'
    HIGH = '3', 'High'


class Stage(models.TextChoices):
    PLAN = '1', 'In planning'
    LOG = '2', 'Is logistic'
    TRANS = '3', 'In transport'
    DONE = '4', 'Process is done'
    COMPL = '5','In complaint'


class Origin(models.TextChoices):
    CITY = '1', 'City'
    COUNTRY = '2', 'Country'
    ABROAD = '3', 'Abroad'


class Event(models.TextChoices):
    CREATED = '1', 'Created'
    STARTED = '2', 'Started'
    PAYMENT_REQUESTED = '3', 'Requested for set payment date'
    PAYMENT_DATE_WAS_SET = '4', 'Payment date was set'
    APPROVAL_REQUESTED = '5', 'Requested for approval of the board'
    ACCEPTED_BY_BOARD = '6', 'Accepted by the board'
    FINISHED = '7', 'Finished'
    REJECTED = '8', 'Rejected'
    SET_PLAN_END_DATE = '9', 'Planning end date was set'
    SET_LOG_END_DATE = '10', 'Logistic end date was set'
    SET_TRANS_END_DATE = '11', 'Transport end date was set'
    SET_DONE_END_DATE = '12', 'Process end date was set'
    SET_COMPLAINT_END_DATE = '13', 'Complaint end date was set'


