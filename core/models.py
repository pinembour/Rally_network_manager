from django.db import models
from django.db.models import Sum

import unicodedata

class Client(models.Model):
    prenom = models.CharField(max_length=30, null=False)
    nom = models.CharField(max_length=30, null=False)
    surnom = models.CharField(max_length=30, null=True)
    admin = models.BooleanField(null=False, default=False)

    appartement = models.OneToOneField(
        "Appartement",
        null=True,
        related_name="client"
    )

    @staticmethod
    def search(pattern):
        return Client.objects.filter(Q(surnom=pattern) | Q(nom=pattern) | Q(prenom=pattern))

    def save(self, *args, **kwargs):
        if (self.appartement is not None) and (self.appartement.port is not None):
            print(self.appartement.port)
            self.appartement.port.a_jour = False
            self.appartement.port.save()
        super(Client, self).save(*args, **kwargs)

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

class Cotisation(models.Model):
    montant = models.FloatField(null=False, default=0)

    client = models.ForeignKey(
        "Client",
        on_delete=models.CASCADE,
        related_name="cotisations"
    )

    semestre = models.ForeignKey(
        "Semestre",
        on_delete=models.CASCADE,
        related_name="cotisations"
    )

    def save(self, *args, **kwargs):
        if (self.client.appartement is not None) and (self.client.appartement.port is not None):
            self.client.appartement.port.a_jour = False
            self.client.appartement.port.save()
        super(Cotisation, self).save(*args, **kwargs)

    def appartement(self):
        return str(self.client.appartement)

    def __str__(self):
        return str(self.semestre) + " : " + str(self.client)

class Semestre(models.Model):
    nom = models.CharField(max_length=30, null=False)

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
        related_name='appartement'
    )

    def save(self, *args, **kwargs):
        #if self.pk is not None:
        #    orig = Appartement.objects.get(pk=self.pk)
        #    if (orig.client is not None) and (orig.port is not None):
        #        orig.port.a_jour = False
        #        orig.port.save()
        #if (self.client is not None) and (self.port is not None):
        #    self.port.a_jour = False
        #    self.port.save()
        super(Appartement, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.batiment) + ", " + str(self.numero)

class Batiment(models.Model):
    numero = models.CharField(max_length=30, null=False)

    def cotisants(self):
        semestre = Semestre.objects.all().order_by('-id')[:1]
        if semestre.count == 0:
            return 0

        cotisations = Cotisation.objects.all().filter(semestre__exact=semestre[0])

        cotisants = 0
        for c in cotisations:
            client = c.client
            if client.appartement.batiment == self:
                cotisants += 1

        return cotisants

    def __str__(self):
        return "bat " + self.numero

class Switch(models.Model):
    adresse = models.CharField(max_length=40, null=False)

    batiment = models.ForeignKey(
        "Batiment"
    )

    modele = models.ForeignKey(
        "Modele",
        on_delete=models.CASCADE,
        related_name="switchs"
    )

    def a_jour(self):
        return self.ports.filter(a_jour=False).count() == 0

    def ports_a_mettre_a_jour(self):
        return self.ports.filter(fonctionnel=True).filter(a_jour=False)

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

    #def switchsCount(self):
    #    return self.switchs.modeles.all().count()
    #switchsCount.short_description = "Nombre de switchs"

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
