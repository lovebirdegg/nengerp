from django.contrib import admin
from .models import *
from purchase.models import *

# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')

class ReturnMoneyInline(admin.TabularInline):
    model = ReturnMoney
    fields = ['returnName','returnRate','returnAbleMoney','returnMoney','returnAbleDate','returnDate']
class PurchaseContractInline(admin.TabularInline):
    model = Contract
    fields = ['code','supplier','contractAmount','contractContent',]
    raw_id_fields=('supplier',)
class ProjectAdmin(BaseAdmin):
    # inlines = [ReturnMoneyInline,]
    inlines = [PurchaseContractInline,]
    list_display = ('id','code','name','signDate','custom','contractAmount','contractNetAmount','salePerson','projectManager',)
    search_fields = ('code','name','custom__name','salePerson')
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')
admin.site.register(Custom,BaseAdmin)
admin.site.register(Project,ProjectAdmin)
