from django.contrib import admin
from django.db.models import Avg, Max, Min, Count,Sum
from django.http import StreamingHttpResponse
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.admin.views.main import ChangeList
from django.db.models import Q

import xlwt
import django_excel as excel
import datetime

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
    list_per_page = 50
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

class ContractChangeList(ChangeList):

    def get_results(self, *args, **kwargs):
        super(ContractChangeList, self).get_results(*args, **kwargs)
        # q = self.queryset.aggregate(tomato_sum=Sum('contractAmount'))
        payment_amount = 0
        payment_left = 0
        contract_amount = 0
        for contract in self.queryset:
            payment_amount = payment_amount + self.model_admin.get_payment_total(contract)
            payment_left = payment_left + self.model_admin.get_payment_left(contract)
            if isinstance(contract.contractAmount,float):
                contract_amount = contract_amount + contract.contractAmount
        self.total = contract_amount
        self.payment_total = payment_amount
        self.left_total = payment_left
class ContractAdmin(BaseAdmin):
    change_list_template = "purchase/change_list.html"

    inlines = [PaymentInline,]
    list_display = ('id','code', 'supplier','projectCode','contractAmount','get_payment_total','get_payment_left','contractContent','address','invoice',)
    raw_id_fields=('projectCode','supplier')
    actions = ["export_excel",]
    # list_filter = (('signDate',DateRangeFilter),('createTime',DateRangeFilter),'contract_payment__createTime')
    list_filter = (('signDate',DateRangeFilter),('contract_payment__paymentDate',DateRangeFilter))

    # contractAmount.short_description = 'hahah'

    search_fields = ('supplier__name','projectCode__name','projectCode__code','code',)
    def get_queryset(self, request):
        qs = super(ContractAdmin, self).get_queryset(request)
        self.request = request
        return qs

    def get_payment_total(self,contract):
        # paymentDate__range__gte = self.request.GET.get('contract_payment__paymentDate__range__gte')
        paymentDate__range__lte = self.request.GET.get('contract_payment__paymentDate__range__lte')
        con = Q()#总条件
        contractQ = Q()
        rangeDateQ= Q()#付款时间
        paymentDate_gte = '1970-01-01'
        paymentDate_lte = '9999-01-01'
        contractQ.children.append(('contract',contract))
        # if paymentDate__range__gte != None and paymentDate__range__gte != '':
        #     paymentDate_gte = datetime.datetime.strptime(paymentDate__range__gte, "%Y/%m/%d")
        if paymentDate__range__lte != None and paymentDate__range__lte != '':
            paymentDate_lte = datetime.datetime.strptime(paymentDate__range__lte, "%Y/%m/%d")
        rangeDateQ.children.append(('paymentDate__range',(paymentDate_gte, paymentDate_lte)))
        con.add(contractQ, 'AND')
        con.add(rangeDateQ, 'AND')

        total = Payment.objects.filter(con).aggregate(total_pay=Sum('rpaymentMoney'))
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
        # print(request.GET['q'])
        # print(queryset)
        qs = self.get_changelist_instance(request).get_queryset(request)
        column_names = ["code",]
        return excel.make_response_from_query_sets(qs,column_names, "xlsx",status = 200 ,sheet_name='测试',file_name='测试文件')

    get_payment_total.short_description = '已付款'
    get_payment_left.short_description = '剩余'
    export_excel.short_description = "导出Excel文件"

    def export_excel_all(self, request):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=dataw.xls' #导出文件名
        wb = xlwt.Workbook(encoding='utf8')
        sheet = wb.add_sheet('order-sheet')
        sheet.col(0).width = 256*20
        sheet.col(1).width = 256*20
        sheet.col(2).width = 256*20
        sheet.col(3).width = 256*20
        sheet.col(4).width = 256*20
        sheet.col(5).width = 256*20
        sheet.col(6).width = 256*20
        sheet.col(7).width = 256*20
        sheet.col(8).width = 256*20
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
        changelist = self.get_changelist_instance(request)
        contract_all =changelist.get_queryset(request)
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
    def get_changelist(self, request):
        return ContractChangeList

    # def changelist_view(self, request, extra_context=None):
    #     q=Contract.objects.filter(request.GET['q']).aggregate(contract_sum=Sum('contractAmount'))
    #     total = q['contract_sum']
    #     my_context = {
    #         'total': total,
    #     }
    #     return super(ContractAdmin, self).changelist_view(request,
    #         extra_context=my_context)
class PaymentChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super(PaymentChangeList, self).get_results(*args, **kwargs)
        q = self.queryset.aggregate(total_pay=Sum('rpaymentMoney'))
        if q["total_pay"] != None:
            self.payment_total = q["total_pay"]
class PaymentAdmin(BaseAdmin):
    change_list_template = "purchase/change_list_s.html"

    list_display = ('contract','rpaymentMoney','paymentDate',)
    search_fields = ('contract__code','contract__supplier__name',)
    # date_hierarchy = 'paymentDate'
    # list_filter = ()
    list_filter = (('paymentDate',DateRangeFilter),('createTime',DateRangeFilter))
    def get_changelist(self, request):
        return PaymentChangeList
class SupplierChangeList(ChangeList):

    def get_results(self, *args, **kwargs):
        super(SupplierChangeList, self).get_results(*args, **kwargs)
        # q = self.queryset.aggregate(tomato_sum=Sum('contractAmount'))
        payment_amount = 0
        payment_left = 0
        contract_amount = 0
        for supplier in self.queryset:
            payment_amount = payment_amount + self.model_admin.get_pay_total(supplier)
            payment_left = payment_left + self.model_admin.get_debt(supplier)
            contract_amount = contract_amount + self.model_admin.get_contract_total(supplier)
        self.total = contract_amount
        self.payment_total = payment_amount
        self.left_total = payment_left
class SupplierAdmin(BaseAdmin):
    change_list_template = "purchase/change_list_s.html"
    search_fields = ('name',)

    list_display = ('id','name','get_contract_total','get_pay_total','get_debt')
    list_filter = (('contract_supplier__contract_payment__paymentDate',DateRangeFilter),)

    # contract_total = 0
    # pay_total = 0
    def get_queryset(self, request):
        qs = super(SupplierAdmin, self).get_queryset(request)
        self.request = request
        return qs
    def get_contract_total(self,supplier):
        contract_list = Contract.objects.filter(supplier = supplier)
        contract_total = 0
        for contract in contract_list:
            if isinstance(contract.contractAmount,float):
                contract_total = contract_total + float(contract.contractAmount)
        return contract_total
    def get_pay_total(self,supplier):
        paymentDate_gte = '1970-01-01'
        paymentDate_lte = '9999-01-01'
        # paymentDate__range__gte = self.request.GET.get('contract_supplier__contract_payment__paymentDate__range__gte')
        paymentDate__range__lte = self.request.GET.get('contract_supplier__contract_payment__paymentDate__range__lte')
        # if paymentDate__range__gte != None and paymentDate__range__gte != '':
        #     paymentDate_gte = datetime.datetime.strptime(paymentDate__range__gte, "%Y/%m/%d")
        if paymentDate__range__lte != None and paymentDate__range__lte != '':
            paymentDate_lte = datetime.datetime.strptime(paymentDate__range__lte, "%Y/%m/%d")
        contract_list = Contract.objects.filter(supplier = supplier)
        pay_total = 0
        for contract in contract_list:
            ###缺少付款时间条件
            con = Q()#总条件
            contractQ = Q()
            rangeDateQ= Q()#付款时间
            contractQ.children.append(('contract',contract))
            rangeDateQ.children.append(('paymentDate__range',(paymentDate_gte, paymentDate_lte)))
            con.add(contractQ, 'AND')
            con.add(rangeDateQ, 'AND')
            total = Payment.objects.filter(con).aggregate(total_pay=Sum('rpaymentMoney'))
            if total["total_pay"] != None:
                pay_total = pay_total + total["total_pay"]
        return pay_total
    def get_debt(self,supplier):
        return self.get_contract_total(supplier)-self.get_pay_total(supplier)
    get_contract_total.short_description = '合同总额'
    get_pay_total.short_description = '付款总额'
    get_debt.short_description = '欠款'
    def get_changelist(self, request):
        return SupplierChangeList
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
        # supplier_all =Supplier.objects.all()
        changelist = self.get_changelist_instance(request)
        supplier_all =changelist.get_queryset(request)
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

