import ckan.plugins.toolkit as tk
from flask import Blueprint
import ckanext.ckanplugin.helpers as helpers
import logging

log = logging.getLogger(__name__)

import logging
contador = Blueprint(
    'contador', 
    __name__,   
    url_prefix='/contador'
)

@contador.route('/dataset/<dataset>/resource/<resource_id>/download/<filename>')
def resource_download(package_id, resource_id, filename):

    log.info("[views][contador][resource_download] ejecutado")

    helpers.guardar_contador(package_id, resource_id, 'Download')

    return redirect(
        tk.url_for(
            'resource.download',
            dataset=dataset,
            resource_id=resource_id,
            filename=filename
        )
    )
