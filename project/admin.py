from django.contrib import admin
from django.db.models import Avg, Max, Min, Count,Sum

from .models import *
from purchase.models import *
import xlwt
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
    list_display = ('id','code','name','signDate','custom','contractAmount','contractNetAmount','get_cost',)
    search_fields = ('code','name','custom__name','salePerson')
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')
    # actions = ["export_excel",]
    # export_excel.short_description = "导出Excel文件"
    def get_cost(self,project):
        purchase_contract_list = Contract.objects.filter(projectCode=project)
        cost = 0
        for contract in purchase_contract_list:
            total = Payment.objects.filter(contract=contract).aggregate(total_pay=Sum('rpaymentMoney'))
            if total["total_pay"] != None:
                cost = cost + total["total_pay"]
        return cost
    get_cost.short_description = '采购成本'
admin.site.register(Custom,BaseAdmin)
admin.site.register(Project,ProjectAdmin)
