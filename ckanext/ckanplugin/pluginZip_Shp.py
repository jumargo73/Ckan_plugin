# file: blueprints/ckan_proxy.py
from ckan.plugins import SingletonPlugin,implements,toolkit,IResourceController
from ckan.plugins.interfaces import  IConfigurer, IBlueprint
from flask import Blueprint, jsonify, redirect,request,Response,stream_with_context
import json, logging,os,  mimetypes, subprocess
import requests
from ckan.common import config
from configparser import ConfigParser
import time
import ckan.model as model
from ckanext.ckanplugin.services.zip_shp_to_geojson import Zip_Shp_JSONConverter
import ckan.lib.helpers as h
from flask import redirect
from ckan.types import Context 
from typing import Any
from ckanext.ckanplugin.services.geojson_converter import GeoJSONConverter



log = logging.getLogger(__name__)


class ApiZipShpToGeojsonView(SingletonPlugin):

    implements(IBlueprint)
    log.info("[pluginZip_Shp][ApiZipShpToGeojsonView] ejecutado")

    def get_ckan_config(self):

        log.info("[convert_job][get_ckan_config] ejecutado")
        
        
        # Ruta a tu production.ini
        config_path = "/usr/lib/ckan/default/src/ckan/ckan.ini"  # cámbiala según tu instalación
        storage_path = '/var/lib/ckan/default/'


        # 1. Cargar el archivo de configuración manualmente
        if not os.path.exists(config_path):
                raise Exception(f"No se encontró el archivo ini en: {config_path}")

        # 1. Carga la configuración en el objeto 'config' global
        config_ckan = ConfigParser()
        config_ckan.read(config_path)

        # CKAN guarda las variables en la sección [app:main]
        site_url = config_ckan.get("app:main", "ckan.site_url", fallback=None)
        api_key = config_ckan.get("app:main", "ckan.datapusher.api_token", fallback=None)
        ssl_cert = config_ckan.get("app:main", "ckan.devserver.ssl_cert", fallback=None)

        #api_key = os.environ.get("CKAN_API_KEY")  # mejor manejarlo como variable de entorno

        log.info("[get_ckan_config] site_url: %s", site_url)
        log.info("[get_ckan_config] api_key: %s", api_key)
        log.info("[get_ckan_config] storage_path: %s", storage_path)
        log.info("[get_ckan_config] ssl_cert: %s", ssl_cert)
        
        return site_url, api_key,storage_path,ssl_cert

    
    def get_blueprint(self):

        ckan_shp_geojson_bp = Blueprint("Shp_GeoJson", __name__)

        log.info("[ApiZipShpToGeojsonView][get_blueprint][Shp_GeoJson] ejecutado") 

        @ckan_shp_geojson_bp.route("/ckan/shp_to_geojson")
        def shp_to_geojson():

            organizations=Zip_Shp_JSONConverter.listar_organizaciones()
            datasets=Zip_Shp_JSONConverter.listar_dataset()

            log.info("[ApiZipShpToGeojsonView] shp_to_geojson ejecutado") 
            return toolkit.render('convertSHPToGeoJSOB.html',
                                    {
                                        'csrf_field': h.csrf_input(),
                                        'organizations':organizations,
                                        'datasets':datasets
                                    }
                                  )
           
          
        @ckan_shp_geojson_bp.route("/ckan/shp_to_geojson/convert",methods=['POST'])
        def convert_shp_geojson():

            log.info("[ApiZipShpToGeojsonView][convert_shp_geojson]  ejecutado") 
            
            archivo = toolkit.request.files.get('upload')  
            package_id=toolkit.request.form.get('dataset_org') 
            owner_org=toolkit.request.form.get('owner_org') 
            isEvent=toolkit.request.form.get('owner_org') or False

            log.info("[ApiZipShpToGeojsonView][convert_shp_geojson] archivo=%s",archivo) 
            log.info("[ApiZipShpToGeojsonView][convert_shp_geojson] package_id=%s",package_id) 
            log.info("[ApiZipShpToGeojsonView][convert_shp_geojson] owner_org=%s",owner_org) 
            site_url, api_key,storage_path,ssl_cert = self.get_ckan_config()

            # Guardar archivo en /tmp
            tmp_path = f"/tmp/{archivo.filename}"
            archivo.save(tmp_path)   # <-- aquí ya tienes un string path válido

            filename=archivo.filename

            log_file = "/var/log/ckan/convert_job.log"

            # Lanzar proceso en background
            with open(log_file, "a") as f:
                subprocess.Popen(
                    [
                        "/usr/lib/ckan/default/bin/python",
                        "/usr/lib/ckan/default/src/ckan/ckanext/ckanplugin/convert_job.py",
                        tmp_path,
                        package_id,
                        owner_org,
                        filename,
                        site_url, 
                        api_key,
                        storage_path,
                        ssl_cert,
                        isEvent
                    ],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    close_fds=True
                )

          
           

            return toolkit.h.redirect_to("Shp_GeoJson.shp_to_geojson")  # mensaje de "Procesando..."


        return ckan_shp_geojson_bp  


class ApiZipShpToGeojson(SingletonPlugin):
                    
    implements(IResourceController)
    log.info("[pluginZip_Shp][ApiZipShpToGeojson] ejecutado")

    def before_resource_create(self,context: Context, resource: dict[str, Any]):
        pass

    def after_resource_create(self,context: Context, resource: dict[str, Any]):
        log.info("[pluginZip_Shp][ApiZipShpToGeojson][after_resource_create] ejecutado")
        isEvent=False
        # 1. Verificar si es ZIP
        format = resource.get('format', '').lower()
        if format == 'zip':
            isEvent=True
            # 2. Obtener el nombre original (limpiando posibles rutas)
            nombre_sucio = resource.get('name') or resource.get('url') or 'recurso_espacial.zip'

            # os.path.basename limpia rutas como '/tmp/subidas/datos.zip' y deja solo 'datos.zip'
            nombre_limpio = os.path.basename(nombre_sucio)

            # Si el nombre no tiene extensión (pasa a veces en CKAN), se la ponemos
            if not nombre_limpio.lower().endswith('.zip'):
                nombre_limpio = f"{nombre_limpio}.zip"

            # 3. Obtener la URL base de la configuración
            site_url = toolkit.config.get('ckan.site_url')

            # 4. Construir la URL completa al endpoint
            # Esto resultará en: http://localhost:5000/ckan/shp_to_geojson/convert
            endpoint_url = f"{site_url.rstrip('/')}/ckan/shp_to_geojson/convert"
            
            # 5. Obtener la ruta local del archivo en el storage de CKAN
            path_file = resource.get('url') # O la lógica de subida local

            # 6. Obtener la ruta base del storage desde el .ini
            storage_path = toolkit.config.get('ckan.storage_path')
            res_id = resource.get('id')
            package_id = resource.get('package_id')


            # Obtener la organización (owner_org) del dataset
            # Nota: A veces está en resource, si no, hay que traerla del package
            pkg = toolkit.get_action('package_show')(context, {'id': package_id})
            org_id = pkg.get('owner_org')

            # 7. Construir la ruta física real donde CKAN guardó el archivo
            # Estructura típica de CKAN: storage/resources/abc/def/ghi...      
            file_path = os.path.join(
                storage_path, 'resources', 
                res_id[0:3], res_id[3:6], res_id[6:]
            )
            
                # 5. Datos para el endpoint
            if os.path.exists(file_path):
                package_id = resource.get('package_id')

                payload = {
                'dataset_org': package_id,
                'owner_org': org_id,
                'isEvent':isEvent
                }
                
                files = {
                    'upload': (nombre_limpio, open(file_path, 'rb'), 'application/zip')
                }
            
                try:
                    # Abrir el archivo y enviarlo al endpoint
                    response = requests.post(endpoint_url, data=payload, files=files)
                    if response.status_code == 200:
                        print("[pluginZip_Shp][ApiZipShpToGeojson][after_resource_create] Conversión iniciada exitosamente")
                        toolkit.flash_success("Archivo ZIP detectado: Iniciando conversión a GeoJSON y CSV.")
                        toolkit.h.redirect_to(toolkit.url_for('dataset.read', id=package_id))
                except Exception as e:
                    print(f"[pluginZip_Shp][ApiZipShpToGeojson][after_resource_create] Error enviando al endpoint: {e}")


    def before_resource_update(self,context: Context, current: dict[str, Any], resource: dict[str, Any]):
        pass

    def after_resource_update(self, context, resource):
        log.warning("[CSVtoGeoJSONPlugin] after_resource_update ejecutado")
        
        # Procesar solo CSV
        if resource.get('format', '').lower() == 'csv':

            # Obtener dataset completo
            package =   toolkit.get_action('package_show')(context, {'id': resource['package_id']})
            
            
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


    def before_resource_delete(self,context: Context, resource: dict[str, Any], resources: list[dict[str, Any]]):
        pass

    def after_resource_delete(self,context: Context, resources: list[dict[str, Any]]):
        pass    


    def before_resource_show(self,resource_dict: dict[str, Any]):
        return resource_dict


    def before_resource_search(self,search_params: dict[str, Any]):
        return search_params 
    
    def after_resource_search(self,context: Context,data_dict: dict[str, Any], search_params: dict[str, Any]):
    
        return data_dict
    

class ShpPlugin(ApiZipShpToGeojson, ApiZipShpToGeojsonView):
    """Clase unificadora que no necesita código extra"""
    pass