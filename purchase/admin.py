from django.contrib import admin
from django.db.models import Avg, Max, Min, Count,Sum
from django.http import StreamingHttpResponse
from django.shortcuts import render,HttpResponse,redirect
import xlwt
import django_excel as excel

from .models import *
from jet.admin import CompactInline
from django_object_actions import DjangoObjectActions
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from django.urls import path,include

import xlwt
from io import BytesIO





# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')
    def export_excel_all(self, request):
        pass
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_excel_all/', self.admin_site.admin_view(self.export_excel_all)),
        ]
        return my_urls + urls

class PaymentInline(CompactInline):
    model = Payment
    exclude =  ('createTime','updateTime','deletedTime','createdBy','updatedBy','isActive')
class ContractAdmin(BaseAdmin):
    change_list_template = "purchase/change_list.html"

    inlines = [PaymentInline,]
    list_display = ('id','code','projectCode','contractAmount','get_payment_total','get_payment_left','contractContent', 'supplier','address','invoice',)
    raw_id_fields=('projectCode','supplier')
    actions = ["export_excel",]
    list_filter = ('signDate',)

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
    def export_excel(self,request,queryset):
        # data_excel =Contract.objects.all()
        column_names = ["code",]
        return excel.make_response_from_query_sets(queryset,column_names, "xlsx",status = 200 ,sheet_name='测试',file_name='测试文件')

    get_payment_total.short_description = '已付款'
    get_payment_left.short_description = '剩余'
    export_excel.short_description = "导出Excel文件"

    def export_excel_all(self, request):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=data.xls' #导出文件名
        wb = xlwt.Workbook(encoding='utf8')
        sheet = wb.add_sheet('order-sheet')
        # 设置文件头的样式,可以根据自己的需求进行更改
        style_heading = xlwt.easyxf("""
        font:
            name Arial,
            colour_index white,
            bold on,
            height 0xA0;
        align:
            wrap off,
            vert center,
            horiz center;
        pattern:
            pattern solid,
            fore-colour 0x19;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        """)
        # 写入文件标题（行，列，内容，样式）
        sheet.write(0, 0, '合同编号', style_heading)
        sheet.write(0, 1, '合同金额', style_heading)
        sheet.write(0, 2, '已付款', style_heading)
        sheet.write(0, 3, '剩余', style_heading)
        sheet.write(0, 4, '合同内容', style_heading)
        sheet.write(0, 5, '供应商', style_heading)
        sheet.write(0, 6, '用货地点', style_heading)
        sheet.write(0, 7, '项目名称', style_heading)


        data_row = 1
        contract_all =Contract.objects.all()
        payment_amount = 0
        payment_left = 0
        contract_amount = 0
        for contract in contract_all:
            sheet.write(data_row, 0, contract.code)
            sheet.write(data_row, 1, contract.contractAmount)
            sheet.write(data_row, 2, self.get_payment_total(contract))
            sheet.write(data_row, 3, self.get_payment_left(contract))
            sheet.write(data_row, 4, contract.contractContent)
            sheet.write(data_row, 5, contract.supplier.name)
            sheet.write(data_row, 6, contract.address)
            if contract.projectCode !=None:
                sheet.write(data_row, 7, contract.projectCode.name)
            payment_amount = payment_amount + self.get_payment_total(contract)
            payment_left = payment_left + self.get_payment_left(contract)
            if isinstance(contract.contractAmount,float):
                contract_amount = contract_amount + contract.contractAmount
            data_row = data_row + 1
        sheet.write(data_row, 0, '合计', style_heading)
        sheet.write(data_row, 1, contract_amount, style_heading)
        sheet.write(data_row, 2, payment_amount, style_heading)
        sheet.write(data_row, 3, payment_left, style_heading)

        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

class PaymentAdmin(BaseAdmin):
    list_display = ('contract','rpaymentMoney','paymentDate',)
    search_fields = ('contract__code','contract__supplier__name',)
    # date_hierarchy = 'paymentDate'
    # list_filter = ()
    list_filter = (('paymentDate',DateRangeFilter),)
class SupplierAdmin(BaseAdmin):
    change_list_template = "purchase/change_list_s.html"
    search_fields = ('name',)

    list_display = ('id','name','get_contract_total','get_pay_total','get_debt')
    # contract_total = 0
    # pay_total = 0
    def get_contract_total(self,supplier):
        contract_list = Contract.objects.filter(supplier = supplier)
        contract_total = 0
        for contract in contract_list:
            if isinstance(contract.contractAmount,float):
                contract_total = contract_total + float(contract.contractAmount)
        return contract_total
    def get_pay_total(self,supplier):
        contract_list = Contract.objects.filter(supplier = supplier)
        pay_total = 0
        for contract in contract_list:
            total = Payment.objects.filter(contract=contract).aggregate(total_pay=Sum('rpaymentMoney'))
            if total["total_pay"] != None:
                pay_total = pay_total + total["total_pay"]
        return pay_total
    def get_debt(self,supplier):
        return self.get_contract_total(supplier)-self.get_pay_total(supplier)
    get_contract_total.short_description = '合同总额'
    get_pay_total.short_description = '付款总额'
    get_debt.short_description = '欠款'

    def export_excel_all(self, request):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=data.xls' #导出文件名
        wb = xlwt.Workbook(encoding='utf8')
        sheet = wb.add_sheet('order-sheet')
        # 设置文件头的样式,可以根据自己的需求进行更改
        style_heading = xlwt.easyxf("""
        font:
            name Arial,
            colour_index white,
            bold on,
            height 0xA0;
        align:
            wrap off,
            vert center,
            horiz center;
        pattern:
            pattern solid,
            fore-colour 0x19;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        """)
        # 写入文件标题（行，列，内容，样式）
        sheet.write(0, 0, '名称', style_heading)
        sheet.write(0, 1, '合同金额', style_heading)
        sheet.write(0, 2, '已付款', style_heading)
        sheet.write(0, 3, '剩余', style_heading)


        data_row = 1
        supplier_all =Supplier.objects.all()
        payment_amount = 0
        payment_left = 0
        contract_amount = 0
        for supplier in supplier_all:
            sheet.write(data_row, 0, supplier.name)
            sheet.write(data_row, 1, self.get_contract_total(supplier))
            sheet.write(data_row, 2, self.get_pay_total(supplier))
            sheet.write(data_row, 3, self.get_debt(supplier))
            payment_amount = payment_amount + self.get_pay_total(supplier)
            payment_left = payment_left + self.get_debt(supplier)
            contract_amount = contract_amount + self.get_contract_total(supplier)
            data_row = data_row + 1
        sheet.write(data_row, 0, '合计', style_heading)
        sheet.write(data_row, 1, contract_amount, style_heading)
        sheet.write(data_row, 2, payment_amount, style_heading)
        sheet.write(data_row, 3, payment_left, style_heading)

        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

admin.site.register(Supplier,SupplierAdmin)
admin.site.register(Contract,ContractAdmin)
admin.site.register(Payment,PaymentAdmin)

