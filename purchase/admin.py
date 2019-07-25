from django.contrib import admin
from django.db.models import Avg, Max, Min, Count,Sum

from .models import *
from jet.admin import CompactInline


# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')

class PaymentInline(CompactInline):
    model = Payment
    exclude =  ('createTime','updateTime','deletedTime','createdBy','updatedBy','isActive')
class ContractAdmin(BaseAdmin):
    inlines = [PaymentInline,]
    list_display = ('id','code','projectCode','contractAmount','get_payment_total','get_payment_left','contractContent', 'supplier','address','invoice',)
    raw_id_fields=('projectCode','supplier')

    # list_filter = ('supplier',)
    search_fields = ('supplier__name','projectCode__name','code',)

    def get_payment_total(self,contract):
        total = Payment.objects.filter(contract=contract).aggregate(total_pay=Sum('rpaymentMoney'))
        if total["total_pay"] != None:
            return total["total_pay"]
        else:
            return 0
    def get_payment_left(self,contract):
        if isinstance(contract.contractAmount,float):
            return contract.contractAmount - float(self.get_payment_total(contract))
        else:
            return 0
    get_payment_total.short_description = '已付款'
    get_payment_left.short_description = '剩余'

class PaymentAdmin(BaseAdmin):
    list_display = ('contract','rpaymentMoney','paymentDate',)
    search_fields = ('contract__code','contract__supplier__name',)
    list_filter = ('paymentDate',)
admin.site.register(Supplier,BaseAdmin)
admin.site.register(Contract,ContractAdmin)
admin.site.register(Payment,PaymentAdmin)

