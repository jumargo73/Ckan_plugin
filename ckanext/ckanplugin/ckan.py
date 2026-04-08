import ckan.plugins as p
import ckan.plugins.toolkit as tk
from flask import Blueprint, request, jsonify,current_app,redirect
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



log = logging.getLogger(__name__)



class CkanPlugin(DefaultDatasetForm,p.SingletonPlugin):
   
    p.implements(p.IConfigurer, inherit=True)   
    p.implements(p.IActions) 
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers)   
    p.implements(p.IDatasetForm, inherit=True)
    p.implements(p.IBlueprint)


    def get_blueprint(self):
      
        # Blueprint 2
        download_bp = Blueprint(
            "download_tracker",
            __name__
        )

        analytics_bp = Blueprint("analytics_bp", __name__)

        @analytics_bp.after_app_request
        def registrar_analytics_after(response):            

            try:
                log.warning("[CkanPlugin][get_blueprint][registrar_analytics_after] ejecutado")
                path = request.path

                if "/dataset/" in path and "/download/" in path:

                    parts = path.split("/")

                    dataset_id = parts[2]
                    resource_id = parts[4]

                    user_agent = request.headers.get("User-Agent", "")

                    # evitar contar llamadas internas de datapusher
                    if "python-requests" not in user_agent:
                        helpers.contar_descargas(resource_id, dataset_id)

            except Exception as e:
                log.warning(f"Error registrando descarga: {e}")

            return response

        @analytics_bp.before_app_request
        def registrar_analytics_before():
            try:
                log.warning("[CkanPlugin][get_blueprint][registrar_analytics_before] ejecutado")
                #log.warning(f"Interceptando request.path {request.path}")

                path = request.path    
                
                if path.startswith("/datastore/dump/"):
                    log.warning("[CkanPlugin][get_blueprint][analytics_bp] path %s",path)
                    resource_id = request.path.split("/")[-1]

                    ip = request.remote_addr
                    user_agent = request.user_agent.string
                    formato = request.args.get("format")
                    bom = request.args.get("bom")

                    #log.warning(f"Dump datastore detectado {resource_id}")  

                    context = {'ignore_auth': True}

                    resource = tk.get_action('resource_show')(context, {
                        'id': resource_id
                    })

                    package_id = resource['package_id']

                    #log.warning(f"Dump datastore package_id {package_id}")  

                    helpers.contar_descargas(resource_id,package_id) 
            except Exception as e:
                log.warning(f"Error registrando descarga: {e}")    

        return [estadistica,noticias,analytics_bp, download_bp]
    

        
    def update_config(self, config):

        log.warning("[CkanPlugin][update_config] ejecutado")

        if not getattr(config, '_ckanplugin_loaded', False):
            tk.add_template_directory(config, 'templates')                          
            tk.add_public_directory(config, 'public')
            tk.add_resource('public','ckanext-ckanplugin')

            config._ckanplugin_loaded = True

        
    def package_types(self):
        log.warning("[CkanPlugin][package_types] ejecutado") 
        return ['dataset']

    def is_fallback(self):
        print("🔥 is_fallback ejecutado")
        return True    

    def create_package_schema(self):
        schema = super().create_package_schema()

        schema.update({
            'city': [
                tk.get_validator('ignore_empty'),
                tk.get_converter('convert_to_extras')
            ],
            'department': [
                tk.get_validator('ignore_empty'),
                tk.get_converter('convert_to_extras')
            ],
            'update_frequency': [
                tk.get_validator('ignore_empty'),
                tk.get_converter('convert_to_extras')
            ],
        })

        return schema


    def update_package_schema(self):
        schema = super().update_package_schema()

        schema.update({
            'city': [
                tk.get_validator('ignore_empty'),
                tk.get_converter('convert_to_extras')
            ],
            'department': [
                tk.get_validator('ignore_empty'),
                tk.get_converter('convert_to_extras')
            ],
            'update_frequency': [
                tk.get_validator('ignore_empty'),
                tk.get_converter('convert_to_extras')
            ],
        })

        return schema


    def show_package_schema(self):
        schema = super().show_package_schema()

        schema.update({
            'city': [
                tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')
            ],
            'department': [
                tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')
            ],
            'update_frequency': [
                tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')
            ],
        })

        return schema
   
    def get_actions(self):
        return {
            'resource_rating_set': rating_action.resource_rating_set,
            'resource_rating_get': rating_action.resource_rating_get,
            'guardar_contador':updateAction.guardar_contador  
        }    

    def get_auth_functions(self):
        return {
            'resource_rating_set': rating_auth.resource_rating_set,
            'resource_rating_get': rating_auth.resource_rating_get,
            'guardar_contador':updateAuth.guardar_contador  
        }

    def get_helpers(self):
        return {
            "obtener_contador_package": helpers.obtener_contador_package,
            "obtener_contador_resource": helpers.obtener_contador_resource,
            "guardar_contador": helpers.guardar_contador,
            "get_featured_noticia":helpers.get_featured_noticia,
            "get_featured_general":helpers.get_featured_general,
            "get_featured_estadistica":helpers.get_featured_estadistica,
            "get_featured_dataset":helpers.get_featured_dataset,
            "get_featured_groups_new":helpers.get_featured_groups_new,
            "contar_visualizacion":helpers.contar_visualizacion,
            "contar_descargas":helpers.contar_descargas,
        } 

     
        
    
    
    
