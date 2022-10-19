from django import forms

from .models import Engineer
from .models import UsedPort
from .models import Event
from .models import TablePort
from .models import Infra
from .models import Switch
from .models import Port
from .models import Brand
from .models import Model

class EngineerForm(forms.ModelForm):

    class Meta:
        model = Engineer
        fields = ['admin', 'name', 'comment']

class UsedPortForm(forms.ModelForm):

    class Meta:
        model = UsedPort
        fields = ['event', 'engineer', 'tablePort', 'comment']

class InfraForm(forms.ModelForm):

    class Meta:
        model = Infra
        fields = ['number', 'comment']

class TablePortForm(forms.ModelForm):

    class Meta:
        model = TablePort
        fields = ['infrastructure', 'number', 'port', 'comment']

    def __init__(self, *args, **kwargs):
        super(TablePortForm, self).__init__(*args, **kwargs)
        self.fields['port'].required = False

class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['name', 'start', 'comment']

class SwitchForm(forms.ModelForm):

    class Meta:
        model = Switch
        fields = ['name', 'address', 'infrastructure', 'model', 'comment']

class PortForm(forms.ModelForm):

    class Meta:
        model = Port
        fields = ['number', 'working', 'upToDate', 'switch', 'comment']

class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = ['name', 'driver']

class ModelForm(forms.ModelForm):

    class Meta:
        model = Model
        fields = ['name', 'brand']
