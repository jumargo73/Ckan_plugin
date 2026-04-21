from ckan.plugins import SingletonPlugin, IDatasetForm, implements, IPackageController, IResourceController
from ckan.plugins.interfaces import IResourceView, IConfigurer, IBlueprint
from ckan.plugins.toolkit import get_action,request,config,g,check_access, ValidationError,c
from flask import Blueprint,request
import json, logging,os,  mimetypes
from datetime import datetime, date
import ckan.logic as logic
import ckan.model as model
from model import Session, Resource,Package,PackageExtra
from ckanext.ckanplugin.model.contador import Contador
import fitz  
from ckan.types import Context 
from typing import Any
import pprint, re                    
import ckan.lib.helpers as h
from ckan.common import request
from sqlalchemy.orm import joinedload
from dateutil.relativedelta import relativedelta
import os

TRUTHY = {'true', 'on', '1', 'si', 'sí'}

log = logging.getLogger(__name__)

class CSVtoGeoJSONDatasetResourcePlugin(SingletonPlugin):
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
        pass        
    
    # --- dataset_update ---
    
    def after_dataset_update(self,context: Context, pkg_dict: dict[str, Any]):

        log.info("[CSVtoGeoJSONPlugin] after_dataset_update ejecutado")
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

        #log.info("[CSVtoGeoJSONPlugin] after_dataset_show ejecutado")
        ##log.info("[SelloExcelenciaView]  fter_dataset_show pkg_dict devuelto: %s", json.dumps(pkg_dict, indent=2, ensure_ascii=False))    
        return pkg_dict
        
    def before_dataset_view(self,pkg_dict: dict[str, Any]):
        return pkg_dict  
        
    # --- dataset_search ---    
    def before_dataset_search(self,search_params: dict[str, Any]):
        log.info("[CSVtoGeoJSONPlugin] before_dataset_search ejecutado")
        return search_params    
    
    def before_resource_search(self,search_params: dict[str, Any]):
        log.info("[CSVtoGeoJSONPlugin] before_resource_search ejecutado")
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


    