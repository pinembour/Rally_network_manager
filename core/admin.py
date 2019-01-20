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

from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

class CotisationAdminInline(admin.TabularInline):
    model = Cotisation
    extra = 0
    fields = ["client", "montant", "appartement"]

class PortAdminInline(admin.TabularInline):
    model = Port
    extra = 0
    fields = ["numero", "fonctionnel", "a_jour"]

class SwitchAdminInline(admin.TabularInline):
    model = Switch
    extra = 0

class AppartementAdminInline(admin.TabularInline):
    model = Appartement
    extra = 0
    fields = ["numero", "port"]

class AppartementAdminInline_2(admin.StackedInline):
    model = Appartement


class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    list_display = ('surnom', 'prenom', 'nom', 'email', 'admin')
    search_fields = ['surnom', 'prenom', 'nom', 'email']

class CotisationAdmin(admin.ModelAdmin):
    form = CotisationForm
    list_display = ('semestre', 'client', 'appartement', 'montant_view', 'cable_view', 'commentaire')
    list_filter = ['semestre', 'appartement']
    search_fields = ['client__prenom', 'client__nom', 'client__surnom']

    def cable_view(self, obj):
        return '%i e' % obj.cable
    cable_view.short_description = 'Cable'

    def montant_view(self, obj):
        return '%i e' % obj.montant
    montant_view.short_description = 'Montant'

class BatimentAdmin(admin.ModelAdmin):
    form = BatimentForm
    list_display = ('numero', 'commentaire')
    list_filter = []
    search_fields = ['numero']
    inlines = [SwitchAdminInline, AppartementAdminInline]

class AppartementAdmin(admin.ModelAdmin):
    form = AppartementForm
    list_display = ('numero', 'batiment', 'port', 'commentaire')
    list_filter = ['batiment']
    search_fields = ['numero', 'batiment__numero', 'commentaire']

class SemestreAdmin(admin.ModelAdmin):
    form = SemestreForm
    list_display = ('__str__', 'cotisants', 'somme')
    list_filter = []
    search_fields = ['nom', 'commentaire']
    inlines = [CotisationAdminInline]

class PortAdmin(admin.ModelAdmin):
    form = PortForm
    list_display = ('switch', 'numero', 'appartement', 'fonctionnel', 'a_jour')
    list_filter = ['fonctionnel', 'a_jour', 'switch']
    search_fields = ['numero', 'commentaire']

class SwitchAdmin(admin.ModelAdmin):
    form = SwitchForm
    list_display = ('nom', '__str__', 'desc', 'a_jour', 'mettre_a_jour', 'mettre_a_jour_force', 'decabler')
    list_filter = ['modele']
    search_fields = ['nom', 'commentaire']
    inlines = [PortAdminInline]

    def a_jour(self, obj):
        return bool(obj.a_jour())

    def mettre_a_jour(self, obj):
        return mark_safe('<a target="_blank" href="/core/updateSwitch/' + str(obj.id) + '/0"><input type="button" value="Mettre a jour"></input></a>')

    def mettre_a_jour_force(self, obj):
        return mark_safe('<a target="_blank" href="/core/updateSwitch/' + str(obj.id) + '/1"><input type="button" value="Forcer"></input></a>')

    def decabler(self, obj):
        return mark_safe('<a target="_blank" href="/core/decableSwitch/' + str(obj.id) + '"><input type="button" value="Decabler"></input></a>')

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

admin.site.site_header = 'Rivlink'
admin.site.site_title = 'Rivlink manager |'
admin.site.index_title = ''
