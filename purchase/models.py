from django.db import models
from django.utils import timezone

from project.models import BaseModel,Project
# Create your models here.

class Supplier(BaseModel):
    name = models.CharField('供应商名称', max_length=32, blank=True)
    contact = models.CharField('联系人', max_length=32, blank=True,null=True)
    phone = models.CharField('联系方式', max_length=32, blank=True,null=True)
    class Meta:
        verbose_name = '供应商信息'
        verbose_name_plural = '供应商信息'

    def __str__(self):
        return self.name
class Contract(BaseModel):
    code = models.CharField('合同编号',max_length=32, blank=True,null=True)
    payCode = models.CharField('采购申请单',max_length=32, blank=True,null=True)
    projectCode = models.ForeignKey(Project,verbose_name='项目名称',on_delete=models.CASCADE,blank=True,null=True)
    signDate = models.DateField('签约日期', default=timezone.now,blank=True,null=True)
    contractAmount = models.FloatField('合同金额',blank=True,default=0,null=True)
    contractContent = models.TextField('合同内容',blank=True,null=True)
    numstr = models.CharField('数量',max_length=32, blank=True,null=True)
    supplier = models.ForeignKey(Supplier,verbose_name='供应商',blank=True,null=True,on_delete=models.CASCADE)
    address = models.CharField('用货地点',max_length=32, blank=True,null=True)
    invoice = models.CharField('发票',max_length=32, blank=True,null=True) 
    remark = models.CharField('备注',max_length=32, blank=True,null=True)
    class Meta:
        verbose_name = '采购合同'
        verbose_name_plural = '采购合同'

    def __str__(self):
        return self.code+'--'+self.supplier.name
class Payment(BaseModel):
    PAY_TYPE = (
        (1, "第一次付款"),
        (2, "第二次付款"),
        (3, "第三次付款"),
        (4, "第四次付款"),
    )
    contract = models.ForeignKey(Contract,verbose_name='合同',on_delete=models.CASCADE,blank=True)
    paymentName = models.IntegerField(choices=PAY_TYPE, verbose_name="付款阶段", help_text="付款阶段")
    paymentDate = models.DateField('付款日期', blank=True,null=True)
    rpaymentMoney = models.FloatField('付款金额',blank=True,default=0)
    paymentNo = models.CharField('号数',max_length=32, blank=True,null=True)
    remark = models.CharField('备注',max_length=32, blank=True,null=True)

    class Meta:
        verbose_name = '付款记录'
        verbose_name_plural = '付款记录'

    def __str__(self):
        return self.contract.code+'---'+str(self.paymentName)+'---'+ str(self.rpaymentMoney)
