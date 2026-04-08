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
from ckanext.ckanplugin.services.geojson_converter import GeoJSONConverter
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

        
        log.warning("[CSVtoGeoJSONPlugin] after_resource_update ejecutado")
        
        # Procesar solo CSV
        if resource.get('format', '').lower() == 'csv':

            # Obtener dataset completo
            package =   get_action('package_show')(context, {'id': resource['package_id']})
            
            
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

        log.info("[CSVtoGeoJSONPlugin] after_dataset_update ejecutado")

        if context.get('skip_sello_excelencia'):
            return    

        
        # Leer el valor del checkbox desde el formulario
        val =  request.form.get('sello_excelencia') or pkg_dict.get('sello_excelencia')

        
        # Determinar si está marcado
        is_checked = bool(val and str(val).strip().lower() in TRUTHY)

        #log.info("[CSVtoGeoJSONPlugin] after_dataset_update tiene sello , %s",is_checked) 

        # Traer el dataset actual
        pkg_id = pkg_dict.get('id') or pkg_dict.get('name')
        if not pkg_id:
            return

        pkg =   get_action('package_show')({'user': context.get('user')}, {'id': pkg_id})
        extras = pkg.get('extras', [])

        # Quitar valor previo si existe
        extras = [e for e in extras if e.get('key') != 'sello_excelencia']

        # Guardar cambios
        if is_checked:
            extras.append({'key': 'sello_excelencia', 'value': 'true'})

        # ⚠️ Pasar bandera para que el evento no se dispare otra vez
        new_context = dict(context, skip_sello_excelencia=True)
        get_action('package_patch')(new_context, {'id': pkg_id, 'extras': extras})

        #log.info("[CSVtoGeoJSONPlugin] after_dataset_update Dataset Marcado con Exito")          
        

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
        log.info("[CSVtoGeoJSONPlugin][after_dataset_search] ejecutado")
        try:

            contadores=[]
            
            # 1️⃣ Obtener contadores desde tu acción
            #contador_action = toolkit get_action('contador_get')
            context = {
                'model': model,
                'session': model.Session,
                'user':  g.user or  config.get('ckan.site_id')
            }

            log.info(f"[CSVtoGeoJSONPlugin][after_dataset_search] context {context}")
            
            contadores = self.contador_get()
            
            
            log.info(f"[CSVtoGeoJSONPlugin][after_dataset_search] contadores {contadores}")

            # 2️⃣ Optimizar acceso mapeando por resource_id
            contador_map = {c['resource_id']: c for c in contadores}

            # 3️⃣ Iterar los datasets y agregar contador a cada recurso
            for dataset in search_results.get('results', []):

                package_id=dataset.get('id') if dataset else ''

                consolidado=self.get_consolidado_contador(package_id)

                dataset['consolidado']=consolidado if consolidado else {}

                log.info(f"[CSVtoGeoJSONPlugin] after_dataset_search package['id']= {package_id} consolidado {consolidado}")
               
                for resource in dataset.get('resources', []):
                    #log.info(f"[CSVtoGeoJSONPlugin] after_dataset_search resource['id']= {resource['id']}")
                    rid = resource.get('id')
                    filas_columnas_map=self.get_filas_columnas(rid,context)
                    data_extra=self.get_extras(rid)
                    resource['contador'] = contador_map.get(rid, None)
                    resource["estructura"] = filas_columnas_map
                    resource["data_extra"] =data_extra

        except Exception as e:
            log.error(
                f"[CSVtoGeoJSONPlugin] Error after_dataset_search: {str(e)}"
            )

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


    def get_extras(self,id):

        
        try:

            #log.info("[CSVtoGeoJSONPlugin] get_extras ejecutado")

            resource_model = Session.query(Resource).filter(
                Resource.format.ilike('PDF'),
                Resource.id == id
            ).first()

            if not resource_model:
                #log.warning("[DataJson] get_extras No se encontró recurso con ID: %s", id)
                return {
                    "resource_id":id,
                    "categoria":"",
                    "fecha_obtencion":"",
                    "fecha_vencimiento":"",
                    "dependiencia":"",
                    "nivel":"",
                }  

            extras = {}

            if resource_model.extras:
                if isinstance(resource_model.extras, str):
                    try:
                        extras = json.loads(resource_model.extras)
                    except Exception as e1:
                            log.error(f"[DataJson] Error id {id} {e1}")
                            return {
                                "resource_id":id,
                                "categoria":"",
                                "fecha_obtencion":"",
                                "fecha_vencimiento":"",
                                "dependiencia":"",
                                "nivel":"",
                                "error": str(e1)
                            }  
                elif isinstance(resource_model.extras, dict):
                    extras = resource_model.extras

            if extras.get('type')=="sello_excelencia":
                return {
                    "resource_id":id,
                    "categoria":extras.get('type'),
                    "fecha_obtencion":extras.get('fecha_obtencion'),
                    "fecha_vencimiento":extras.get('fecha_vencimiento'),
                    "dependiencia":extras.get('owner_org'),
                    "nivel":extras.get('nivel'),
                    "error": ""
                }        
            else:
                return {
                    "resource_id": id,
                    "categoria":"",
                    "fecha_obtencion":"",
                    "fecha_vencimiento":"",
                    "dependiencia":"",
                    "nivel":"",
                    "error": "No tiene Sello de Excelencia"
                }  
        
        except Exception as e:
            log.error(f"[DataJson] Error id {id} {e}")
            return [
                {
                    "resource_id":id,
                    "categoria":"",
                    "fecha_obtencion":"",
                    "fecha_vencimiento":"",
                    "dependiencia":"",
                    "nivel":"",
                    "error":str(e)
                }
            ]

    def get_filas_columnas(self,id,context):
        try:
            #log.info("[CSVtoGeoJSONPlugin] get_filas_columnas ejecutado")
            datastore_response =  get_action('datastore_search')(context,{'id': id})
            if datastore_response:
                columnas = len(datastore_response.get("fields", []))
                filas = datastore_response.get("total", 0)  
                #log.warning(f"[CSVtoGeoJSONPlugin] get_filas_columnas con id={id}: filas={filas}, columnas={columnas}")
                return{
                        "resource_id": id,
                        "filas": filas,
                        "columnas": columnas,
                        "error": ""
                    }
                
                
            else:
                #log.warning(f"[CSVtoGeoJSONPlugin] get_filas_columnas con id={id}: filas=0,columnas=0")
                return {
                        "resource_id": id,
                        "filas": 0,
                        "columnas": 0,
                        "error": str(datastore_response)
                    }
                
               

        except Exception as e:
            log.error(f"[CSVtoGeoJSONPlugin] get_filas_columnas con id {id} error={e}")
            return {
                    "resource_id": id,
                    "filas": 0,
                    "columnas": 0,
                    "error": str(e)
                }
            
           
    def get_consolidado_contador(selft,package_id): 
                
        """
            Devuelve el consolidado de las vistas y descargas de los recursos.
        """

        log.info("[CSVtoGeoJSONPlugin] get_consolidado_contador ejecutado")
    
        session = model.Session

        vistas=0
        descargas=0

        rows = Session.query(Contador).filter(
                Contador.package_Id == package_id
            ).all()

       
        for row in rows:
            vistas+=row.contVistas
            descargas+=row.contDownload
            log.info(f"[CSVtoGeoJSONPlugin][get_consolidado_contador] vistas {vistas} descargas {descargas}")

        
        log.info(f"[CSVtoGeoJSONPlugin][get_consolidado_contador] registro {rows}")

        return{
                "visualizaciones": vistas if vistas else 0,
                "descargas": descargas if descargas else 0,
                "package_id": package_id,
            }
          


              

    def contador_get(self):
        """
        Devuelve los contadores almacenados en la tabla personalizada.
        """

        #log.info("[CSVtoGeoJSONPlugin] contador_get ejecutado")
    
        session = model.Session

        rows = session.query(Contador).all()

        log.info(f"[CSVtoGeoJSONPlugin][contador_get] registro {rows}")

        return [
            {
                "resource_id": row.source_Id,
                "visualizaciones": row.contVistas,
                "descargas": row.contDownload,
                "package_id": row.package_Id,
            }
            for row in rows
        ]   
       
    
