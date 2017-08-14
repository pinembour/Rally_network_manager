from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Switch
from .models import Appartement

import napalm
import sys
import os

def index(request):

    return HttpResponse("Hello, world. You're at the core index.")

@login_required(login_url='/login/')
def updateSwitchs(request, switch_id):

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

    ports = switch.ports_a_mettre_a_jour()

    final_config = ""

    for port in ports:

        config = ""
        if port.is_connected():
            appartement = port.appartement
            client = appartement.client

            if appartement:
                if appartement.client.admin:
                    config = admin_conf.replace('$INTERFACE', port.numero)
                    config = config.replace('$DESCRIPTION', appartement.client.getIdentifiant() + " - ADMIN")
                elif appartement.client.cotisations.count() > 0:
                    config = client_conf.replace('$INTERFACE', port.numero)
                    config = config.replace('$DESCRIPTION', appartement.client.getIdentifiant())
                else:
                    config = registration_conf.replace('$INTERFACE', port.numero)
                    config = config.replace('$DESCRIPTION', "Appart " + appartement.numero)

            final_config += config
        else:
            config = registration_conf.replace('$INTERFACE', port.numero)
            config = config.replace('$DESCRIPTION', "Not connected")
            final_config += config

    final_config += '\nend'
    #return HttpResponse(final_config.replace('\n', '<br />'))

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
    #choice = raw_input("\nWould you like to commit these changes? [yN]: ")
    #if choice == 'y':
    #  print('Committing ...')
    device.commit_config()
    #else:
    #  print('Discarding ...')
    #  device.discard_config()

    # close the session with the device.
    device.close()

    for port in ports:
        port.a_jour = True
        port.save()

    print('Done.')

    return HttpResponse("Yo.")
