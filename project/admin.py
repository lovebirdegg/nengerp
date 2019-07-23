from django.contrib import admin
from .models import *

# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')

class ReturnMoneyInline(admin.TabularInline):
    model = ReturnMoney
    fields = ['returnName','returnRate','returnAbleMoney','returnMoney','returnAbleDate','returnDate']
class ProjectAdmin(BaseAdmin):
    inlines = [ReturnMoneyInline,]
    exclude = ('createTime','updateTime','','deletedTime','createdBy','updatedBy','isActive')
admin.site.register(Custom,BaseAdmin)
admin.site.register(Project,ProjectAdmin)
