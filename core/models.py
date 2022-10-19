from django.db import models
from django.db.models import Sum

import unicodedata

class Engineer(models.Model):
    name = models.CharField(max_length=30, null=False)
    admin = models.BooleanField(null=False, default=False)
    comment = models.TextField(default="", null=True, blank=True)

    @staticmethod
    def search(pattern):
        return Engineer.objects.filter(Q(name=pattern))

    def getIdentifiant(self):
        identifiant = self.name

        identifiant = str(unicodedata.normalize('NFKD', identifiant).encode('ascii', 'ignore'))
        identifiant.replace(" ", "")
        identifiant.replace("-", "")
        identifiant.replace("_", "")
        identifiant.replace("@", "a")
        identifiant.replace(";", "")
        identifiant = identifiant.strip("b\'")

        return identifiant

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=30, null=False)

    start = models.DateField()

    comment = models.TextField(default="", null=True, blank=True)

    def engineers(self):
        return self.usedPorts.count()

    def __str__(self):
        return self.name

class TablePort(models.Model):
    number = models.CharField(max_length=30, null=False)

    infrastructure = models.ForeignKey(
        "Infra",
        on_delete=models.CASCADE,
        related_name="tablePorts"
    )

    port = models.OneToOneField(
        "Port",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tablePort'
    )
    
    comment = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.has_port():
            self.port.upToDate = False
            self.port.save()
        super(TablePort, self).save(*args, **kwargs)

    def has_port(self):
        has = False
        try:
            has = (self.port is not None)
        except Port.DoesNotExist:
            pass
        return has

    def __str__(self):
        return str(self.infrastructure) + ", " + str(self.number)

class UsedPort(models.Model):
    engineer = models.ForeignKey(
        "Engineer",
        on_delete=models.CASCADE,
        related_name="usedPorts"
    )

    tablePort = models.ForeignKey(
        "TablePort",
        on_delete=models.CASCADE,
        related_name="usedPorts"
    )

    event = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
        related_name="usedPorts"
    )
    
    comment = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.tablePort.port.upToDate = False
        self.tablePort.port.save()
        super(UsedPort, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.event) + " : " + str(self.engineer)

class Infra(models.Model):
    number = models.CharField(max_length=30, null=False)
    
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "infra " + self.number

class Switch(models.Model):

    name = models.CharField(max_length=40, null=False, default="tep")

    address = models.CharField(max_length=40, null=False)

    infrastructure = models.ForeignKey(
        "Infra",
        on_delete=models.CASCADE
    )

    model = models.ForeignKey(
        "Model",
        on_delete=models.CASCADE,
        related_name="switchs"
    )
    
    comment = models.TextField(null=True, blank=True)

    def dismount(self):
        for port in self.ports.all():
            port.tablePort = None
            port.save()
        return True

    def upToDate(self):
        return self.ports.filter(upToDate=False).count() == 0

    def ports_to_update(self, force):
        ports = self.ports.filter(working=True)
        if force == '0':
            ports = ports.filter(upToDate=False)
        return ports

    def portsFree(self):
        return self.ports.all().exclude(tablePort__isnull=False).exclude(working__exact=False).count()

    def stable(self):
        return self.portsFree() > 2
    stable.boolean = True
    stable.short_description = "Stable"

    def desc(self):
        return str(self) + " --> " + str(self.portsFree()) + " ports available"
    desc.short_description = "Description"

    def __str__(self):
        return str(self.infrastructure) + " : " + self.address

class Port(models.Model):
    number = models.CharField(max_length=10, null=False)
    working = models.BooleanField(null=False, default=True)
    upToDate = models.BooleanField(null=False, default=False)

    switch = models.ForeignKey(
        "Switch",
        on_delete=models.CASCADE,
        related_name='ports'
    )
    
    comment = models.TextField(null=True, blank=True)

    def has_tablePort(self):
        has = False
        try:
            has = (self.tablePort is not None)
        except TablePort.DoesNotExist:
            pass
        return has

    def is_connected(self):
        has_tablePort = False
        try:
            has_tablePort = (self.tablePort is not None)
        except TablePort.DoesNotExist:
            print("Error:" + str(self))
            pass
        return has_tablePort

    def __str__(self):
        return str(self.switch) + " : " + self.number + " : " + ("OK" if self.working else "NOT OK")

class Brand(models.Model):
    name = models.CharField(max_length=30, null=False)

    driver = models.CharField(max_length=40, null=False, default="ios")

    def __str__(self):
        return self.name

class Model(models.Model):
    name = models.CharField(max_length=30, null=False)

    brand = models.ForeignKey(
        "Brand",
        on_delete=models.CASCADE,
        related_name = "models"
    )

    def __str__(self):
        return str(self.brand) + " - " + self.name
