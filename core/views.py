from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Switch
from .models import Appartement
from .models import Cotisation
from .models import Semestre

import napalm
import sys
import os

def index(request):

    return HttpResponse("Hello, world. You're at the core index.")

@login_required(login_url='/login/')
def decableSwitch(request, switch_id):

    switch = Switch.objects.get(id=switch_id)
    switch.decable()
    switch.save()

    return HttpResponse("Switch " + switch.adresse + " decable")


@login_required(login_url='/login/')
def updateSwitch(request, switch_id, force):

    """Load a config for the device."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/core/configs/"

    switch = Switch.objects.get(id=switch_id)

    conf_dir = switch.modele.marque.nom + "/" + switch.modele.nom + "/"

    admin_conf_file = base_dir + conf_dir + "admin_port.conf"
    client_conf_file = base_dir + conf_dir + "client_port.conf"
    registration_conf_file = base_dir + conf_dir + "registration_port.conf"
    pass_file = base_dir + "switch_password"

    if not (os.path.exists(admin_conf_file) and os.path.isfile(admin_conf_file)):
        msg = 'Missing or invalid admin port config file {0}'.format(admin_conf_file)
        return HttpResponse(msg)

    if not (os.path.exists(client_conf_file) and os.path.isfile(client_conf_file)):
        msg = 'Missing or invalid client port config file {0}'.format(client_conf_file)
        return HttpResponse(msg)

    if not (os.path.exists(registration_conf_file) and os.path.isfile(registration_conf_file)):
        msg = 'Missing or invalid registration port config file {0}'.format(registration_conf_file)
        return HttpResponse(msg)

    if not (os.path.exists(pass_file) and os.path.isfile(pass_file)):
        msg = 'Missing or invalid switch password file {0}'.format(pass_file)
        return HttpResponse(msg)

    admin_conf = open(admin_conf_file, 'r').read()
    client_conf = open(client_conf_file, 'r').read()
    registration_conf = open(registration_conf_file, 'r').read()
    root_password = open(pass_file, 'r').read().replace('\n', '')

    ports = switch.ports_a_mettre_a_jour(force)

    semestre = Semestre.objects.order_by("-debut")[0]
    print(semestre)

    final_config = ""

    for port in ports:

        config = ""
        if port.has_appartement():

            appartement = port.appartement
            cotisations = appartement.cotisations.filter(semestre=semestre).all()

            if len(cotisations) > 0:

                cotisation = cotisations[len(cotisations) - 1]
                client = cotisation.client

                if client.admin:
                    print("Port: " + port.numero + " admin")
                    config = admin_conf.replace('$INTERFACE', port.numero)
                    config = config.replace('$DESCRIPTION', "Appart " + appartement.numero + " - " + client.getIdentifiant() + " - ADMIN")
                else:
                    print("Port: " + port.numero + " cotisant")
                    config = client_conf.replace('$INTERFACE', port.numero)
                    config = config.replace('$DESCRIPTION', "Appart " + appartement.numero + " - " + client.getIdentifiant())
            else:
                print("Port: " + port.numero + " pas de cotisation")
                config = registration_conf.replace('$INTERFACE', port.numero)
                config = config.replace('$DESCRIPTION', "Appart " + appartement.numero)

        else:
            print("pas cable")
            config = registration_conf.replace('$INTERFACE', port.numero)
            config = config.replace('$DESCRIPTION', "Not connected")

        final_config += config

    final_config += '\nend\ncopy r s\n'

    ## Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver(switch.modele.marque.driver)

    # Connect:
    device = driver(hostname=switch.adresse, username='root', password=root_password)

    #print 'Opening ...'
    device.open()

    #print 'Loading replacement candidate ...'
    device.load_merge_candidate(config=final_config)

    ## Note that the changes have not been applied yet. Before applying
    ## the configuration you can check the changes:
    print('\nDiff:')
    print(device.compare_config())

    ## You can commit or discard the candidate changes.
    device.commit_config()

    # close the session with the device.
    device.close()

    for port in ports:
        port.a_jour = True
        port.save()

    print('Done.')

    return HttpResponse(final_config.replace('\n', '<br />'))

@login_required(login_url='/admin/login/')
def money(request):
        
        total = Cotisation.objects.filter(client__admin=False).aggregate(Sum('montant'))['montant__sum']
        
        message = "Total = " + str(total)
        
        return HttpResponse(message)
