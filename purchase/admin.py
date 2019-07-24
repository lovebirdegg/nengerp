from django.contrib import admin
from .models import *

# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')

class PaymentInline(admin.TabularInline):
    model = Payment
    exclude =  ('createTime','updateTime','deletedTime','createdBy','updatedBy','isActive')
class ContractAdmin(BaseAdmin):
    inlines = [PaymentInline,]
    list_display = ('id','code','projectCode','contractAmount','contractContent', 'supplier','address','invoice',)
    raw_id_fields=('projectCode',)
    # list_filter = ('supplier',)
    search_fields = ('supplier__name','projectCode__name','code',)
class PaymentAdmin(BaseAdmin):
    list_display = ('contract','rpaymentMoney','paymentDate',)
    search_fields = ('contract__code','contract__supplier__name',)
    list_filter = ('paymentDate',)
admin.site.register(Supplier,BaseAdmin)
admin.site.register(Contract,ContractAdmin)
admin.site.register(Payment,PaymentAdmin)

