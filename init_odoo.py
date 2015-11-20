"""Utilities to run and setup Odoo using Docker."""
import subprocess
import time

import erppeek


def odoo_start():
    try:
        erppeek.Client(server='http://localhost:8069')
    except:
        cmd = 'docker-compose up -d'
        subprocess.call(cmd, shell=True)
    else:
        print "Odoo server is running."
        return

    # Wait for Odoo to be loaded.
    print "Waiting for Odoo server to be available..."
    time.sleep(1)
    limit = time.time() + 30
    proofs_of_service = [
        'openerp.service.server: HTTP service (werkzeug) '  # ...
        'running on 0.0.0.0:8069',
        'openerp.addons.bus.bus: Bus.loop listen imbus on db postgres',
    ]
    while time.time() < limit:
        cmd = 'docker logs {docker_instance}'.format(
            docker_instance='odooselenium_odoo_1')
        output = subprocess.check_output(cmd, shell=True)
        if all([proof in output for proof in proofs_of_service]):
            break
        else:
            time.sleep(1)
    print "... Odoo server up and running!"


def odoo_stop():
    cmd = 'docker-compose stop'
    subprocess.call(cmd, shell=True)


def odoo_setup():
    odoo = erppeek.Client(
        server='http://localhost:8069',
    )
    dbname = u'test'
    if dbname not in odoo.db.list():
        print "Creating database {0}...".format(dbname)
        odoo.create_database('admin', dbname)
        print "... Database '{0}' created.".format(dbname)
    else:
        print "Database '{0}' already exists.".format(dbname)
    # Log in database.
    odoo = erppeek.Client(
        server='http://localhost:8069',
        db='test',
        user='admin',
        password='admin',
    )
    if 'web_selenium' not in odoo.modules()['installed']:
        assert 'web_selenium' in odoo.modules()['uninstalled'], \
            'web_selenium addon is not available. Check extra addons path.'
        print "Installing addon 'web_selenium'..."
        odoo.install('web_selenium')
        print "... web_selenium installed."
    else:
        print "Addon 'web_selenium' already installed."
