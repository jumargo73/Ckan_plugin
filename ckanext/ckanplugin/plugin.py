import ckan.plugins as p
import ckan.plugins.toolkit as tk
from flask import Blueprint, request, jsonify,current_app
from ckanext.ckanplugin.middleware import registrar_analytics
import logging
from ckan.model import Package
from sqlalchemy import Column, Unicode
import os
import ckanext.ckanplugin.logic.action.resourceRating as rating_action
import ckanext.ckanplugin.logic.action.get as getAction
import ckanext.ckanplugin.logic.action.update as updateAction
import ckanext.ckanplugin.logic.auth.resourceRating as rating_auth
import ckanext.ckanplugin.logic.auth.get as getAuth
import ckanext.ckanplugin.logic.auth.update as updateAuth
import ckanext.ckanplugin.model.package_ext as package_ext
import ckanext.ckanplugin.model as model
import ckanext.ckanplugin.helpers as helpers
from typing import Any
from ckan.types import Context 
from ckan.model import Session
from ckan.plugins.toolkit import DefaultDatasetForm
from ckan.logic.schema import default_create_package_schema
from ckan.logic.schema import default_update_package_schema
from ckan.logic.schema import default_show_package_schema
from ckanext.ckanplugin.services.geojson_converter import GeoJSONConverter  
from ckanext.ckanplugin.views.estadistica import estadistica
from ckanext.ckanplugin.views.noticias import noticias
from ckanext.ckanplugin.views.contador import contador
from flask import current_app



log = logging.getLogger(__name__)
class CSVtoGeoJSON(p.SingletonPlugin):
    pass


class CSVtoGeoJSONApiPlugin(p.SingletonPlugin):
    
    p.implements(p.IBlueprint)
    #log.info("[CSVtoGeoJSONPlugin] CSVtoGeoJSONApi Cargado con Exito")
    def get_blueprint(self):
        """
        Crea un Blueprint con endpoint manual para convertir CSV a GeoJSON.
        """
        log.info("[CSVtoGeoJSONApiPlugin][get_blueprint][ckanplugin_manual]  ejecutado")

        bp = Blueprint('ckanplugin_manual', __name__)

        @bp.route('/api/3/action/convert_csv_to_geojson', methods=['POST'])
        def convert_csv_to_geojson_endpoint():
            """
            Endpoint manual: recibe resource_id y genera/actualiza GeoJSON.
            """
            try:
                log.info("[CSVtoGeoJSONApiPlugin][ckanplugin_manual][convert_csv_to_geojson_endpoint]  ejecutado")
                payload = request.get_json(force=True) or {}
                log.info(f"[CSVtoGeoJSONPlugin] Payload recibido en endpoint manual: {payload}")

                resource_id = payload.get('resource_id')
                if not resource_id:
                    raise ValidationError({'resource_id': ['Este campo es obligatorio']})
                    
                    
                # Crear context manual
                context = {
                    'model': model,
                    'session': model.Session,
                    'user': c.user or c.author,
                    'ignore_auth': False
                }    
                
                #buscar Paquete asociado
                resource = get_action('resource_show')(context, {'id': resource_id})
                
                # Obtener dataset completo
                package = get_action('package_show')(context, {'id': resource['package_id']})
               
                
                log.info(f"[CSVtoGeoJSONPlugin] package_id encontrado con {resource['id']} : {package['id']}")    

                # Buscar recurso GeoJSON ya existente en el paquete
                geojson_resource = next(
                    (r for r in package['resources'] if r.get('format', '').lower() == 'geojson'),
                    None
                )

                if geojson_resource:
                    #log.info("[CSVtoGeoJSONPlugin] GeoJSON ya existe, será actualizado (ID: %s)", geojson_resource['id'])
                    GeoJSONConverter.convertir_csv_geojson(resource['id'], geojson_resource['id'])  # Pasar ID para update
                else:
                    #log.info("[CSVtoGeoJSONPlugin] No hay GeoJSON, creando nuevo")
                    GeoJSONConverter.self.convertir_csv_geojson(resource['id'])  

                return jsonify({"success": True, "message": f"GeoJSON generado para recurso {resource_id}"})

            except ValidationError as ve:
                log.error(f"[CSVtoGeoJSONPlugin] Error de validación: {ve}")
                return jsonify({"success": False, "error": str(ve)}), 400

            except Exception as e:
                log.error(f"[CSVtoGeoJSONPlugin] Error en conversión manual: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

            # CKAN requiere lista de blueprints
        return [bp]

    

    