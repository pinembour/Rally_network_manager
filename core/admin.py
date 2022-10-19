from django.contrib import admin
from django.utils.html import mark_safe

from .models import Engineer
from .models import UsedPort
from .models import Event
from .models import TablePort
from .models import Infra
from .models import Switch
from .models import Port
from .models import Brand
from .models import Model

from .forms import EngineerForm
from .forms import UsedPortForm
from .forms import InfraForm
from .forms import TablePortForm
from .forms import EventForm
from .forms import SwitchForm
from .forms import PortForm
from .forms import BrandForm
from .forms import ModelForm

from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy

class UsedPortAdminInline(admin.TabularInline):
    model = UsedPort
    extra = 0
    fields = ["engineer", "tablePort"]

class PortAdminInline(admin.TabularInline):
    model = Port
    extra = 0
    fields = ["number", "working", "upToDate"]

class SwitchAdminInline(admin.TabularInline):
    model = Switch
    extra = 0

class TablePortAdminInline(admin.TabularInline):
    model = TablePort
    extra = 0
    fields = ["number", "port"]

class TablePortAdminInline_2(admin.StackedInline):
    model = TablePort


class EngineerAdmin(admin.ModelAdmin):
    form = EngineerForm
    list_display = ('name', 'admin')
    search_fields = ['name']

class UsedPortAdmin(admin.ModelAdmin):
    form = UsedPortForm
    list_display = ('event', 'engineer', 'tablePort', 'comment')
    list_filter = ['event', 'tablePort']
    search_fields = ['engineer__name']

class InfraAdmin(admin.ModelAdmin):
    form = InfraForm
    list_display = ('number', 'comment')
    list_filter = []
    search_fields = ['number']
    inlines = [SwitchAdminInline, TablePortAdminInline]

class TablePortAdmin(admin.ModelAdmin):
    form = TablePortForm
    list_display = ('number', 'infrastructure', 'port', 'comment')
    list_filter = ['infrastructure']
    search_fields = ['number', 'infrastructure__number', 'comment']

class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ('__str__', 'engineers')
    list_filter = []
    search_fields = ['name', 'comment']
    inlines = [UsedPortAdminInline]

class PortAdmin(admin.ModelAdmin):
    form = PortForm
    list_display = ('switch', 'number', 'tablePort', 'working', 'upToDate')
    list_filter = ['working', 'upToDate', 'switch']
    search_fields = ['number', 'comment']

class SwitchAdmin(admin.ModelAdmin):
    form = SwitchForm
    list_display = ('name', '__str__', 'desc', 'upToDate', 'update', 'update_force', 'dismount')
    list_filter = ['model']
    search_fields = ['name', 'comment']
    inlines = [PortAdminInline]

    def upToDate(self, obj):
        return bool(obj.upToDate())

    def update(self, obj):
        return mark_safe('<a target="_blank" href="/core/updateSwitch/' + str(obj.id) + '/0"><input type="button" value="Update"></input></a>')

    def update_force(self, obj):
        return mark_safe('<a target="_blank" href="/core/updateSwitch/' + str(obj.id) + '/1"><input type="button" value="Force"></input></a>')

    def dismount(self, obj):
        return mark_safe('<a target="_blank" href="/core/dismountSwitch/' + str(obj.id) + '"><input type="button" value="Dismount"></input></a>')

class BrandAdmin(admin.ModelAdmin):
    form = BrandForm
    list_display = ('__str__',)
    list_filter = []
    search_fields = ['name']

class ModelAdmin(admin.ModelAdmin):
    form = ModelForm
    list_display = ('__str__',)
    list_filter = []
    search_fields = ['name']

admin.site.register(Engineer, EngineerAdmin)
admin.site.register(UsedPort, UsedPortAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(TablePort, TablePortAdmin)
admin.site.register(Infra, InfraAdmin)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Model, ModelAdmin)

admin.site.site_header = 'Rally Network Manager'
admin.site.site_title = 'Rally Network Manager |'
admin.site.index_title = ''
