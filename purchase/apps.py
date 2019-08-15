from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    name = 'purchase'
    verbose_name='采购管理'
from suit.apps import DjangoSuitConfig
class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'