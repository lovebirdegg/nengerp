from django.db import models

from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class SoftDeletableQuerySet(models.query.QuerySet):
    def delete(self):
        self.update(deletedTime=timezone.now())

class SoftDeletableManager(models.Manager):
    """
    仅返回未被删除的实例
    """
    _queryset_class = SoftDeletableQuerySet

    def get_queryset(self):
        """
        在这里处理一下QuerySet, 然后返回没被标记位is_deleted的QuerySet
        """
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints

        return self._queryset_class(**kwargs).filter(deletedTime=None)

class BaseModel(models.Model):
    """
        基础模型
    """
    createTime = models.DateTimeField(verbose_name="创建时间",default=timezone.now,null=True)
    updateTime = models.DateTimeField(verbose_name="修改时间",default=timezone.now,null=True)
    deletedTime = models.DateTimeField("删除时间",null=True, blank=True,default=None)
    createdBy = models.IntegerField(verbose_name="创建人ID",default=0,null=True)
    updatedBy = models.IntegerField(verbose_name="修改人ID",default=0,null=True)
    isActive = models.BooleanField(default=True, verbose_name='是否正常')

    objects = SoftDeletableManager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        if soft:
            self.deletedTime = timezone.now()
            self.save()
        else:
            return super(SoftDeletableModel, self).delete(using=using, *args, **kwargs)
    class Meta:
        abstract = True
class Custom(BaseModel):
    name = models.CharField('客户名称', max_length=32, blank=True,unique=True)
    contact = models.CharField('联系人', max_length=32, blank=True,null=True)
    phone = models.CharField('联系方式', max_length=32, blank=True,null=True)
    class Meta:
        verbose_name = '客户信息'
        verbose_name_plural = '客户信息'

    def __str__(self):
        return self.name
class Project(BaseModel):
    code = models.CharField('项目编号',max_length=32, blank=True)
    name = models.TextField('项目名称',max_length=200, blank=True)
    custom = models.ForeignKey(Custom, verbose_name='甲方',on_delete=models.CASCADE,blank=True, null=True)
    signDate = models.DateField('签约日期', default=timezone.now, null=True)
    contractAmount = models.FloatField('合同金额',blank=True,default=0, null=True)
    contractNetAmount = models.FloatField('合同净额',blank=True,default=0, null=True)
    salePerson = models.CharField('销售负责人',max_length=32, blank=True,null=True)
    projectManager = models.CharField('项目负责人',max_length=32, blank=True,null=True)
    remark = models.CharField('备注',max_length=32, blank=True,null=True)
    class Meta:
        verbose_name = '项目合同'
        verbose_name_plural = '项目合同'

    def __str__(self):
        return self.name
class ReturnMoney(BaseModel):
    returnName = models.CharField('阶段',max_length=1000, blank=True,null=True)
    returnRate = models.FloatField('回款率',blank=True,default=0)
    returnAbleDate = models.DateField('应收日期', blank=True,null=True)
    returnDate = models.DateField('回款日期', blank=True,null=True)
    returnAbleMoney = models.FloatField('应回款额',blank=True,default=0)
    returnMoney = models.FloatField('回款额',blank=True,default=0)
    project = models.ForeignKey(to=Project, verbose_name="项目", blank=True,on_delete=models.DO_NOTHING,default=0)

    class Meta:
        verbose_name = '回款条件'
        verbose_name_plural = '回款条件'

    def __str__(self):
        return self.returnName