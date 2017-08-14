from django.contrib import admin
from django.utils.html import mark_safe

from .models import Client
from .models import Cotisation
from .models import Semestre
from .models import Appartement
from .models import Batiment
from .models import Switch
from .models import Port
from .models import Marque
from .models import Modele

from .forms import ClientForm
from .forms import CotisationForm
from .forms import BatimentForm
from .forms import AppartementForm
from .forms import SemestreForm
from .forms import SwitchForm
from .forms import PortForm
from .forms import MarqueForm
from .forms import ModeleForm

class CotisationAdminInline(admin.TabularInline):
    model = Cotisation
    extra = 0
    fields = ["client", "montant"]

class PortAdminInline(admin.TabularInline):
    model = Port
    extra = 0

class SwitchAdminInline(admin.TabularInline):
    model = Switch
    extra = 0

class AppartementAdminInline(admin.TabularInline):
    model = Appartement
    extra = 0

class AppartementPortAdminInline(admin.TabularInline):
    model = Appartement
    extra = 0
    max_num = 1




class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    list_display = ('__str__', 'appartement')
    list_filter = ['appartement']
    search_fields = ['surnom', 'prenom', 'nom']

class CotisationAdmin(admin.ModelAdmin):
    form = CotisationForm
    list_display = ('__str__', 'client', 'appartement', 'montant')
    list_filter = ['semestre']
    search_fields = ['client']

class BatimentAdmin(admin.ModelAdmin):
    form = BatimentForm
    list_display = ('__str__', 'cotisants')
    list_filter = []
    search_fields = ['numero']
    inlines = [SwitchAdminInline, AppartementAdminInline]

class AppartementAdmin(admin.ModelAdmin):
    form = AppartementForm
    list_display = ('__str__', 'batiment')
    list_filter = ['batiment']
    search_fields = ['numero', 'batiment']

class SemestreAdmin(admin.ModelAdmin):
    form = SemestreForm
    list_display = ('__str__', 'cotisants', 'somme')
    list_filter = []
    search_fields = ['nom']
    inlines = [CotisationAdminInline]

class PortAdmin(admin.ModelAdmin):
    form = PortForm
    list_display = ('__str__', 'fonctionnel', 'a_jour')
    list_filter = ['fonctionnel', 'a_jour', 'switch']
    search_fields = ['numero']
    inlines = [AppartementPortAdminInline]

class SwitchAdmin(admin.ModelAdmin):
    form = SwitchForm
    list_display = ('__str__', 'modele', 'desc', 'stable', 'a_jour', 'mettre_a_jour')
    list_filter = ['modele']
    search_fields = ['adresse']
    inlines = [PortAdminInline]

    def a_jour(self, obj):
        return bool(obj.a_jour())

    def mettre_a_jour(self, obj):
        return mark_safe('<a href="/core/updateSwitchs/' + str(obj.id) + '"><input type="button" value="Mettre à jour"></input></a>')

class MarqueAdmin(admin.ModelAdmin):
    form = MarqueForm
    list_display = ('__str__',)
    list_filter = []
    search_fields = ['nom']

class ModeleAdmin(admin.ModelAdmin):
    form = ModeleForm
    list_display = ('__str__',)
    list_filter = []
    search_fields = ['nom']

admin.site.register(Client, ClientAdmin)
admin.site.register(Cotisation, CotisationAdmin)
admin.site.register(Semestre, SemestreAdmin)
admin.site.register(Appartement, AppartementAdmin)
admin.site.register(Batiment, BatimentAdmin)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(Marque, MarqueAdmin)
admin.site.register(Modele, ModeleAdmin)

