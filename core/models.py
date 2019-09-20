from django.db import models
from django.db.models import Sum

import unicodedata

class Client(models.Model):
    prenom = models.CharField(max_length=30, null=False)
    nom = models.CharField(max_length=30, null=False)
    surnom = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    admin = models.BooleanField(null=False, default=False)

    commentaire = models.TextField(default="", null=True, blank=True)

    @staticmethod
    def search(pattern):
        return Client.objects.filter(Q(surnom=pattern) | Q(nom=pattern) | Q(prenom=pattern))

    def getIdentifiant(self):
        identifiant = self.surnom if self.surnom else (self.prenom + self.nom)

        identifiant = str(unicodedata.normalize('NFKD', identifiant).encode('ascii', 'ignore'))
        identifiant.replace(" ", "")
        identifiant.replace("-", "")
        identifiant.replace("_", "")
        identifiant.replace("@", "a")
        identifiant.replace(";", "")
        identifiant = identifiant.strip("b\'")

        return identifiant

    def __str__(self):
        return (self.surnom + " : " + self.prenom + " " + self.nom) if self.surnom else (self.prenom + " " + self.nom)

class Semestre(models.Model):
    nom = models.CharField(max_length=30, null=False)

    debut = models.DateField()

    commentaire = models.TextField(default="", null=True, blank=True)

    def cotisants(self):
        return self.cotisations.count()

    def somme(self):
        return self.cotisations.all().aggregate(Sum('montant'))['montant__sum']

    def __str__(self):
        return self.nom

class Appartement(models.Model):
    numero = models.CharField(max_length=30, null=False)

    batiment = models.ForeignKey(
        "Batiment",
        on_delete=models.CASCADE,
        related_name="appartements"
    )

    port = models.OneToOneField(
        "Port",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='appartement'
    )
    
    commentaire = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.has_port():
            self.port.a_jour = False
            self.port.save()
        super(Appartement, self).save(*args, **kwargs)

    def has_port(self):
        has = False
        try:
            has = (self.port is not None)
        except Port.DoesNotExist:
            pass
        return has

    def __str__(self):
        return str(self.batiment) + ", " + str(self.numero)

class Cotisation(models.Model):
    montant = models.FloatField(null=False, default=5)
    cable = models.IntegerField(default=0, null=False)

    client = models.ForeignKey(
        "Client",
        on_delete=models.CASCADE,
        related_name="cotisations"
    )

    appartement = models.ForeignKey(
        "Appartement",
        on_delete=models.CASCADE,
        related_name="cotisations"
    )

    semestre = models.ForeignKey(
        "Semestre",
        on_delete=models.CASCADE,
        related_name="cotisations"
    )
    
    commentaire = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.appartement.port.a_jour = False
        self.appartement.port.save()
        super(Cotisation, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.semestre) + " : " + str(self.client)

class Batiment(models.Model):
    numero = models.CharField(max_length=30, null=False)
    
    commentaire = models.TextField(null=True, blank=True)

    def __str__(self):
        return "bat " + self.numero

class Switch(models.Model):

    nom = models.CharField(max_length=40, null=False, default="tep")

    adresse = models.CharField(max_length=40, null=False)

    batiment = models.ForeignKey(
        "Batiment",
        on_delete=models.CASCADE
    )

    modele = models.ForeignKey(
        "Modele",
        on_delete=models.CASCADE,
        related_name="switchs"
    )
    
    commentaire = models.TextField(null=True, blank=True)

    def decable(self):
        for port in self.ports.all():
            port.appartement = None
            port.save()
        return True

    def a_jour(self):
        return self.ports.filter(a_jour=False).count() == 0

    def ports_a_mettre_a_jour(self, force):
        ports = self.ports.filter(fonctionnel=True)
        if force == '0':
            ports = ports.filter(a_jour=False)
        return ports

    def portsLibres(self):
        return self.ports.all().exclude(appartement__isnull=False).exclude(fonctionnel__exact=False).count()

    def stable(self):
        return self.portsLibres() > 2
    stable.boolean = True
    stable.short_description = "Stable"

    def desc(self):
        return str(self) + " --> " + str(self.portsLibres()) + " ports disponibles"
    desc.short_description = "Description"

    def __str__(self):
        return str(self.batiment) + " : " + self.adresse

class Port(models.Model):
    numero = models.CharField(max_length=10, null=False)
    fonctionnel = models.BooleanField(null=False, default=True)
    a_jour = models.BooleanField(null=False, default=False)

    switch = models.ForeignKey(
        "Switch",
        on_delete=models.CASCADE,
        related_name='ports'
    )
    
    commentaire = models.TextField(null=True, blank=True)

    def has_appartement(self):
        has = False
        try:
            has = (self.appartement is not None)
        except Appartement.DoesNotExist:
            pass
        return has

    def is_connected(self):
        has_appartement = False
        try:
            has_appartement = (self.appartement is not None)
        except Appartement.DoesNotExist:
            print("Error:" + str(self))
            pass
        return has_appartement

    def __str__(self):
        return str(self.switch) + " : " + self.numero + " : " + ("OK" if self.fonctionnel else "NOT OK")

class Marque(models.Model):
    nom = models.CharField(max_length=30, null=False)

    driver = models.CharField(max_length=40, null=False, default="ios")

    def __str__(self):
        return self.nom

class Modele(models.Model):
    nom = models.CharField(max_length=30, null=False)

    marque = models.ForeignKey(
        "Marque",
        on_delete=models.CASCADE,
        related_name = "modeles"
    )

    def __str__(self):
        return str(self.marque) + " - " + self.nom
