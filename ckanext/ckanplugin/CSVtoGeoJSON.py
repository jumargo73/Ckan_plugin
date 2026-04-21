from ckan.plugins import SingletonPlugin, IDatasetForm, implements, IPackageController, IResourceController
from ckan.plugins.interfaces import IResourceView, IConfigurer, IBlueprint
import ckan.plugins.toolkit as tk
from flask import Blueprint,request
import json, logging,os,  mimetypes
from datetime import datetime, date
#import ckan.logic as logic
import ckan.model as model
from model import Session, Resource,Package,PackageExtra
from ckanext.ckanplugin.model.contador import Contador
import fitz  
from ckan.types import Context 
from ckan.common import config
from typing import Any
import pprint, re                    
from ckanext.ckanplugin.services.geojson_converter import GeoJSONConverter
#import ckan.lib.helpers as h
from ckan.common import request
from sqlalchemy.orm import joinedload
from dateutil.relativedelta import relativedelta
import os


log = logging.getLogger(__name__)

class CSVtoGeoJSONPlugin(SingletonPlugin):
    implements(IResourceController)
    implements(IPackageController)
   
    
    log.info("[CSVtoGeoJSONPlugin] CSVtoGeoJSONDatasetResourcePlugin Cargado con Exito")
    
    
    # --- resource_create ---        
    def before_resource_create(self,context: Context, resource: dict[str, Any]):
        pass

    def after_resource_create(self,context: Context, resource: dict[str, Any]):
        pass
        
    # --- dataset_create ---     
    def after_dataset_create(self,context: Context,  pkg_dict: dict[str, Any]):
        
        return pkg_dict
    
    # --- resource_update ---    

    def before_resource_update(self,context: Context, current: dict[str, Any], resource: dict[str, Any]):
        pass

    def after_resource_update(self, context, resource):
        
        log.warning("[CSVtoGeoJSONPlugin] after_resource_update ejecutado")
        
        # Procesar solo CSV
        if resource.get('format', '').lower() == 'csv':

            # Obtener dataset completo
            package = tk.get_action('package_show')(context, {'id': resource['package_id']})
            
            
            # Buscar recurso GeoJSON ya existente en el paquete
            geojson_resource = next(
                (r for r in package['resources'] if r.get('format', '').lower() == 'geojson'),
                None
            )

            if geojson_resource:
                log.warning("[CSVtoGeoJSONPlugin] GeoJSON ya existe, será actualizado (ID: %s)", geojson_resource['id'])
                GeoJSONConverter.convertir_csv_geojson(resource['id'], geojson_resource['id'])  # Pasar ID para update
            else:
                log.warning("[CSVtoGeoJSONPlugin] No hay GeoJSON, creando nuevo")
                GeoJSONConverter.convertir_csv_geojson(resource['id'])

    
    # --- dataset_update ---
    
    def after_dataset_update(self,context: Context, pkg_dict: dict[str, Any]):
        pass

    # --- resource_delete ---
        
    def before_resource_delete(self,context: Context, resource: dict[str, Any], resources: list[dict[str, Any]]):
        pass

    def after_resource_delete(self,context: Context, resources: list[dict[str, Any]]):
        pass

    # --- dataset_delete ---
    def after_dataset_delete(self,context: Context, pkg_dict: dict[str, Any]):
        pass
    
    # --- resource_show ---
    
    def before_resource_show(self,resource_dict: dict[str, Any]):
        return resource_dict

    def before_dataset_show(self,context: Context, pkg_dict: dict[str, Any]):
        return pkg_dict
    
    
    # --- dataset_show ---   
    def after_dataset_show(self,context: Context, pkg_dict: dict[str, Any]):
        return pkg_dict
        
    def before_dataset_view(self,pkg_dict: dict[str, Any]):
        return pkg_dict  
        
    # --- dataset_search ---    
    def before_dataset_search(self,search_params: dict[str, Any]):
        return search_params    
    
    def before_resource_search(self,search_params: dict[str, Any]):
        return search_params  

    def after_dataset_search(self,search_results: dict[str, Any], search_params: dict[str, Any]):
       return search_results
        
    
    def after_resource_search(self,context: Context,data_dict: dict[str, Any], search_params: dict[str, Any]):
        return data_dict
       
    
    # --- dataset_index ---   
    
    def before_dataset_index(self,pkg_dict: dict[str, Any]):
        return pkg_dict
    
    
    # --- create ---   
    def create(self,entity: model.Package):
        pass
    
    # --- delete ---  
    def delete(self,entity: model.Package):
        pass
    
    # --- create ---
    def edit(self,entity: model.Package):
        pass        
        
    # --- READ ---      
    def read(self,entity: model.Package):
        pass


    