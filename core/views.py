from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Switch
from .models import TablePort
from .models import UsedPort
from .models import Event

import napalm
import sys
import os

def index(request):

    return HttpResponse("Hello, world. You're at the core index.")

@login_required(login_url='/login/')
def dismountSwitch(request, switch_id):

    switch = Switch.objects.get(id=switch_id)
    switch.dismount()
    switch.save()

    return HttpResponse("Switch " + switch.address + " dismount")


@login_required(login_url='/login/')
def updateSwitch(request, switch_id, force):

    """Load a config for the device."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/core/configs/"

    switch = Switch.objects.get(id=switch_id)

    conf_dir = switch.model.brand.name + "/" + switch.model.name + "/"

    admin_conf_file = base_dir + conf_dir + "admin_port.conf"
    engineer_conf_file = base_dir + conf_dir + "engineer_port.conf"
    registration_conf_file = base_dir + conf_dir + "registration_port.conf"
    pass_file = base_dir + "switch_password"

    if not (os.path.exists(admin_conf_file) and os.path.isfile(admin_conf_file)):
        msg = 'Missing or invalid admin port config file {0}'.format(admin_conf_file)
        return HttpResponse(msg)

    if not (os.path.exists(engineer_conf_file) and os.path.isfile(engineer_conf_file)):
        msg = 'Missing or invalid engineer port config file {0}'.format(engineer_conf_file)
        return HttpResponse(msg)

    if not (os.path.exists(registration_conf_file) and os.path.isfile(registration_conf_file)):
        msg = 'Missing or invalid registration port config file {0}'.format(registration_conf_file)
        return HttpResponse(msg)

    if not (os.path.exists(pass_file) and os.path.isfile(pass_file)):
        msg = 'Missing or invalid switch password file {0}'.format(pass_file)
        return HttpResponse(msg)

    admin_conf = open(admin_conf_file, 'r').read()
    engineer_conf = open(engineer_conf_file, 'r').read()
    registration_conf = open(registration_conf_file, 'r').read()
    root_password = open(pass_file, 'r').read().replace('\n', '')

    ports = switch.ports_to_update(force)

    event = Event.objects.order_by("-start")[0]
    print(event)

    final_config = ""

    for port in ports:

        config = ""
        if port.has_tablePort():

            tablePort = port.tablePort
            usedPorts = tablePort.usedPorts.filter(event=event).all()

            if len(usedPorts) > 0:

                usedPort = usedPorts[len(usedPorts) - 1]
                engineer = usedPort.engineer

                if engineer.admin:
                    print("Port: " + port.number + " admin")
                    config = admin_conf.replace('$INTERFACE', port.number)
                    config = config.replace('$DESCRIPTION', "TablePort " + tablePort.number + " - " + engineer.getIdentifiant() + " - ADMIN")
                else:
                    print("Port: " + port.number + " cotisant")
                    config = engineer_conf.replace('$INTERFACE', port.number)
                    config = config.replace('$DESCRIPTION', "TablePort " + tablePort.number + " - " + engineer.getIdentifiant())
            else:
                print("Port: " + port.number + " pas de usedPort")
                config = registration_conf.replace('$INTERFACE', port.number)
                config = config.replace('$DESCRIPTION', "TablePort " + tablePort.number)

        else:
            print("pas cable")
            config = registration_conf.replace('$INTERFACE', port.number)
            config = config.replace('$DESCRIPTION', "Not connected")

        final_config += config

    final_config += '\nend\ncopy r s\n'

    ## Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver(switch.model.brand.driver)

    # Connect:
    device = driver(hostname=switch.address, username='hmsu0707', password=root_password)

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
        port.upToDate = True
        port.save()

    print('Done.')

    return HttpResponse(final_config.replace('\n', '<br />'))

