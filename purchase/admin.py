from django.contrib import admin
from .models import *

# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')

class PaymentInline(admin.TabularInline):
    model = Payment
    exclude =  ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')
class ContractAdmin(BaseAdmin):
    inlines = [PaymentInline,]
admin.site.register(Supplier,BaseAdmin)
admin.site.register(Contract,ContractAdmin)
admin.site.register(Payment,BaseAdmin)

