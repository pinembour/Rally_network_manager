from django import forms

from .models import Client
from .models import Cotisation
from .models import Semestre
from .models import Appartement
from .models import Batiment
from .models import Switch
from .models import Port
from .models import Marque
from .models import Modele

class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ['admin', 'surnom', 'prenom', 'nom', 'email', 'commentaire']

class CotisationForm(forms.ModelForm):

    class Meta:
        model = Cotisation
        fields = ['semestre', 'client', 'appartement', 'montant', 'cable', 'commentaire']

class BatimentForm(forms.ModelForm):

    class Meta:
        model = Batiment
        fields = ['numero', 'commentaire']

class AppartementForm(forms.ModelForm):

    class Meta:
        model = Appartement
        fields = ['batiment', 'numero', 'port', 'commentaire']

    def __init__(self, *args, **kwargs):
        super(AppartementForm, self).__init__(*args, **kwargs)
        self.fields['port'].required = False

class SemestreForm(forms.ModelForm):

    class Meta:
        model = Semestre
        fields = ['nom', 'debut', 'commentaire']

class SwitchForm(forms.ModelForm):

    class Meta:
        model = Switch
        fields = ['nom', 'adresse', 'batiment', 'modele', 'commentaire']

class PortForm(forms.ModelForm):

    class Meta:
        model = Port
        fields = ['numero', 'fonctionnel', 'a_jour', 'switch', 'commentaire']

class MarqueForm(forms.ModelForm):

    class Meta:
        model = Marque
        fields = ['nom', 'driver']

class ModeleForm(forms.ModelForm):

    class Meta:
        model = Modele
        fields = ['nom', 'marque']
