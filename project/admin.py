from django.contrib import admin
from django.db.models import Avg, Max, Min, Count,Sum
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from django.urls import path,include

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
    # date_hierarchy = 'signDate'
    list_display = ('id','code','name','contractAmount','get_cost','signDate',)
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
    @method_decorator(staff_member_required)
    def data_view(self, request):
        response_data = []
        supplier_list = Supplier.objects.all()
        for supplier in supplier_list:
            contract_list = Contract.objects.filter(supplier = supplier)
            pay_list = []
            contract_total = 0
            pay_total = 0
            for contract in contract_list:
                if isinstance(contract.contractAmount,float):
                    contract_total = contract_total + float(contract.contractAmount)
                # pay_list = Payment.objects.filter(contract = contrant)
                # for pay in pay_list:
                #     pay_total = pay_total + pay.rpaymentMoney
                total = Payment.objects.filter(contract=contract).aggregate(total_pay=Sum('rpaymentMoney'))
                if total["total_pay"] != None:
                    pay_total = pay_total + total["total_pay"]
            supplier_pay_dic = {
                    'supplier':supplier.name,
                    'contrant_total':str(contract_total),
                    'pay_total':str(pay_total),
                    'debt':str(contract_total - pay_total)
                }
            response_data.append(supplier_pay_dic)
            print(response_data)
        # print(request.GET)
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            data = response_data,
        )
        return TemplateResponse(request, "project/data.html",context)
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('data_view/', self.admin_site.admin_view(self.data_view)),
        ]
        return my_urls + urls
    get_cost.short_description = '采购成本'
admin.site.register(Custom,BaseAdmin)
admin.site.register(Project,ProjectAdmin)
