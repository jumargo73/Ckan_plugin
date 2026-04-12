from ckan.plugins import SingletonPlugin, implements
from ckan.plugins.interfaces import IConfigurer, IBlueprint
from ckan.plugins import toolkit
from ckan.common import config
import ckan.model as model
from ckan.model.resource import Resource  # ✅ Correcto import

from flask import Blueprint, jsonify, redirect, request, Response
from ckan.types import Context 

import logging, json, subprocess, os
from datetime import datetime


log = logging.getLogger(__name__)


class DataJson(SingletonPlugin):
    implements(IBlueprint)
    log.info("[DataJson] DataJson Cargado con Exito")

    def get_blueprint(self):

        bp = Blueprint('data_json', __name__)

        log.info("[DataJson][get_blueprint][data_json] ejecutado")

        @bp.route('/api/3/action/data.json', methods=['GET'])
        def dataJson():

            log.info("[data_json][dataJson] ejecutado")
            context = {
                'model': model,
                'session': model.Session,
                'ignore_auth': True,
                'user': None
            }

            data={}
            try:

                # 1️⃣ Primero obtengo la cantidad total
                count_result = toolkit.get_action('package_search')(context, {
                    'rows': 0
                })
                registros = count_result['count']

                # 2️⃣ Ahora hago otra llamada trayendo exactamente esa cantidad
                responses = toolkit.get_action('package_search')(context, {
                    'rows': registros
                })



                package_responses=responses['results']

                log.warning(f"[DataJson] get_blueprint dataJson responses: {package_responses}")


                data={
                        "@context": "https://project-open-data.cio.gov/v1.1/schema/catalog.jsonld",
                        "@type": "dcat:Catalog", 
                        "conformsTo": "https://project-open-data.cio.gov/v1.1/schema", 
                        "describedBy": "https://project-open-data.cio.gov/v1.1/schema/catalog.json",
                    }

                data['dataset']=[]

                url_site=config.get('ckan.site_url')


                count=0

                for package_response in package_responses:
                        

                    #log.warning(f"[DataJson] get_blueprint powerBI  {package_response['id']} posicion {count}') : {registros}")

                    if package_response.get('type', '').lower() != 'harvest':

                        grupos= package_response.get('groups')
                        organization=package_response.get('organization') 
                        tags=package_response.get('tags') 
                        resources=package_response.get('resources') 

                        if package_response.get('private')==True:
                            estado="Privado"
                        else:
                            estado="Público"

                        data_dataset={
                            "@type":"Dataset",
                            "identifier":package_response['id'], 
                            "landingPage":"{}".format(url_site+'/'+package_response.get('type')+'/'+package_response['id']),  
                            "title": package_response.get('title'),
                            "description": package_response.get('notes'),
                            "dependencia":organization.get('title') if organization else '',
                            "issued": package_response.get('metadata_created') or '',
                            "modified": package_response.get('metadata_modified') or '',
                            "ciudad": package_response.get('ciudad') or '' ,
                            "departamento":package_response.get('departamento') or '',
                            "accrualPeriodicity":package_response.get('frecuencia_actualizacion') or '',
                            "keywords":[tag["display_name"] for tag in tags],
                            "publisher":{
                                "@type": "org:Organization",
                                "name": "{}".format("org:"+ organization.get('title') if organization else ''),
                            },
                            "contactPoint":{
                                "@type": "vcard:Contact", 
                                "hasEmail": "mailto:datosabiertos@valledelcauca.gov.co", 
                                "fn":  "Valle Data"
                            },
                            "accessLevel":estado,
                            'license':{}                   
                        }


                        data_dataset['distribution']=[]
                        data_dataset['theme']=[]

                        if grupos:
                            data_dataset['theme'].append(grupos)

                        for resource in resources:
                            data_resource= {
                                "@type": "dcat:Distribution",
                                "description":resource.get('description') or '',
                                "downloadURL":resource.get('url') or '',  
                                "format":resource.get('format') or '',
                                "mediaType":resource.get('mediaType') or '',
                                "title":resource.get('title') or '',
                                "issued": resource.get('created') or '',
                                "modified": resource.get('last_modified') or ''
                            }

                            data_dataset['distribution'].append(data_resource)
                    data['dataset'].append(data_dataset)
                return  jsonify(data) 
                #return Response(json.dumps(data), mimetype="application/json")

            except Exception as e:
                log.error(f"[DataJson] Error procesando get_blueprint powerBI: {e}")    



        

        @bp.route('/api/3/action/powerBI.json', methods=['GET'])
        def powerBI():

            """
            EndPoint para Tableros
            """
            log.info("[data_json][powerBI] ejecutado")
            context = {
                'model': model,
                'session': model.Session,
                'ignore_auth': True,
                'user': None
            }

            

            data={}
            try:

                # 1️⃣ Primero obtengo la cantidad total
                count_result = toolkit.get_action('package_search')(context, {
                    'rows': 0,
                    'include_private': True,
                    'fq': '+state:active'
                })
                registros = count_result['count']

                # 2️⃣ Ahora hago otra llamada trayendo exactamente esa cantidad
                responses = toolkit.get_action('package_search')(context, {
                    'rows': registros,
                    'include_private': True,
                    'fq': '+state:active'
                })
                

                package_responses=responses['results']

                #log.warning(f"[DataJson] get_blueprint powerBI context: {context}")

                #log.warning(f"[PluginApi][powerBI] responses: {package_responses}")

                #
                # log.warning(f"[DataJson] get_blueprint powerBI registros: {registros}")

                if package_responses:
                    
                    data={
                        "@context": "https://project-open-data.cio.gov/v1.1/schema/catalog.jsonld",
                        "@type": "dcat:Catalog", 
                        "conformsTo": "https://project-open-data.cio.gov/v1.1/schema", 
                        "describedBy": "https://project-open-data.cio.gov/v1.1/schema/catalog.json",
                    }

                    data['conjuntoDatos']=[]
                    data['sellos']=[]

                    url_site=config.get('ckan.site_url')


                    count=0

                    
                    for package_response in package_responses:

                        #log.warning(f"[DataJson] get_blueprint powerBI  {package_response['id']} posicion {count}') : {registros}")

                        if package_response.get('type', '').lower() != 'harvest':

                            grupos= package_response.get('groups')
                            organization=package_response.get('organization') 
                            tags=package_response.get('tags') 
                            resources=package_response.get('resources') 

                            log.warning(f"[PluginApi][powerBI] resources: {resources}")

                            # Filtrar solo CSV con datastore activo
                            csv_resources = [
                                r for r in resources
                                if r.get("format", "").lower() == "csv"
                                and r.get("datastore_active")
                            ]

                            log.warning(f"[PluginApi][powerBI] csv_resources: {csv_resources}")

                            if not csv_resources:
                                continue


                            # Obtener el más reciente
                            latest_resource = max(
                                csv_resources,
                                key=lambda r: datetime.fromisoformat(r["created"])
                            )        
                            
                            log.warning(f"[PluginApi][powerBI] latest_resource: {latest_resource}")

                            estado=None    
                            if package_response.get('private')==True:
                                estado="Privado"
                            else:
                                estado="Público"

                            consolidado=package_response.get('consolidado')

                            #log.warning(f"[DataJson] get_blueprint powerBI organization: {organization}")

                            data_dataset={
                                "@type":"Dataset",
                                "identifier":package_response['id'], 
                                "landingPage":"{}".format(url_site+'/'+package_response.get('type')+'/'+package_response['id']),  
                                "title": package_response.get('title'),
                                "description": package_response.get('notes'),
                                "dependencia":organization.get('title') if organization else '',
                                "issued": package_response.get('metadata_created') or '',
                                "modified": package_response.get('metadata_modified') or '',
                                "ciudad": package_response.get('ciudad') or '' ,
                                "departamento":package_response.get('departamento') or '',
                                "frecuencia_actualizacion":package_response.get('frecuencia_actualizacion') or '',
                                "keywords":[tag["display_name"] for tag in tags],
                                "publisher":{
                                    "@type": "org:Organization",
                                    "name": "{}".format("org:"+ organization.get('title') if organization else ''),
                                },
                                "contactPoint":{
                                    "@type": "vcard:Contact", 
                                    "hasEmail": "mailto:datosabiertos@valledelcauca.gov.co", 
                                    "fn":  "Valle Data"
                                },
                                "accessLevel":estado,
                                'licencia':{},
                                "Visualizaciones":consolidado.get('visualizaciones') if consolidado else 0,
                                "descargar":consolidado.get('descargas') if consolidado else 0,                                   
                            }

                            data_dataset['distribucion']=[]
                            data_dataset['tema']=[]

                            contador=latest_resource.get('contador') 
                            #log.warning(f"[PliginApi][powerBI] contador: {contador}")
                            estructura=latest_resource.get('estructura') 
                            #log.warning(f"[PliginApi][powerBI] estructura: {estructura}")
                            data_extras=latest_resource.get('data_extra')    
                            #log.warning(f"[PliginApi][powerBI] data_extras: {data_extras}")

                            data_resource= {
                                "@type": "dcat:Distribution",
                                "description":latest_resource['description'] or '',
                                "downloadURL":latest_resource['url'] or '',  
                                "format":latest_resource['format'] or '',
                                "mediaType":latest_resource['mimetype'] or '',
                                #"title":latest_resource['title'] or '',
                                "issued": latest_resource['created'] or '',
                                "modified": latest_resource['last_modified'] or '',                              
                                "filas":estructura['filas'] if estructura else 0 ,
                                "columnas":estructura['columnas'] if estructura else 0 ,
                                "vistas":contador['visualizaciones'] if contador else 0,
                                'descargas':contador['descargas'] if contador else 0,
                            }


                            if grupos:
                                data_dataset['tema'].append(grupos)
                           
                           
                                        #nombre_resource=resource.get('name')
                            data_dataset['distribucion'].append(data_resource)

                               

                            #log.warning(f"[DataJson] get_blueprint powerBI resources_response: {resource}")

                        #log.warning(f"[DataJson] get_blueprint powerBI data_dataset: {data_dataset}")
                        data['conjuntoDatos'].append(data_dataset)

                        #log.warning(f"[DataJson] get_blueprint powerBI data_dataset: {data_dataset}")

                        count+=1
                            
                return  jsonify(data) 
                #return Response(json.dumps(data), mimetype="application/json")

            except Exception as e:
                log.error(f"[PluginApi][powerBI] Error procesando powerBI {e}")

            # Siempre devolver success para no interrumpir CKAN

            #return jsonify({"success": True})

       

        @bp.route('/api/3/action/dashboard_stats', methods=['GET'])
        
        def dashboard_stats():

            log.info("[data_json][dashboard_stats] ejecutado")
            

            # Usamos ignore_auth para que el dashboard sea público pero vea todo
            context = {
                'model': model,
                'session': model.Session,
                'ignore_auth': True,
                'user': 'opendata'
            }


            count_result = toolkit.get_action('package_search')(context, {
                    'rows': 0,
                    'include_private': True,
                    'fq': '+state:active'
                })
            registros = count_result['count']

            # 2️⃣ Ahora hago otra llamada trayendo exactamente esa cantidad
            privados = self.contar_privados(context,registros)       
                     
            
            # 2. Huérfanos (tu consulta favorita)
            huerfanos = self.obtener_huerfanos_totales(context,registros)  

            #formatos
            formatos_raw = self.formatos_raw(context,registros)           
          
            
            # ... (tus conteos de datasets, huérfanos y privados anteriores) ...

            # 4. Total de Organizaciones
            orgs = toolkit.get_action('organization_list')(context, {})
            total_orgs = len(orgs)

            # 5. Total de Grupos
            grupos = toolkit.get_action('group_list')(context, {})
            total_grupos = len(grupos)

            data=jsonify({
                'total_datasets': registros,
                'huerfanos': huerfanos,
                'privados': privados,
                'total_orgs': total_orgs,
                'total_grupos': total_grupos,
                'formatos_raw':formatos_raw
            })    
            log.warning(f"[DataJson[dashboard_stats][data]={data}")

            return data
            
        return bp 
    

    def obtener_huerfanos_totales(self,context:Context,registros):
        # 'ignore_auth': True es lo que permite ver los privados sin restricciones
        
        data_dict = {
            'q': '*:*',
            'fq': '-groups:[* TO *]', # Tu filtro de huérfanos
            'include_private': True,   # Obligatorio para Solr
            'rows': registros               # Ajusta según cuántos esperes encontrar
        }
        
        resultado = toolkit.get_action('package_search')(context, data_dict)
        return resultado['count']


    def contar_privados(self,context:Context,registros):
        # Es vital usar ignore_auth para que el conteo sea real (vea todo)
            
        data_dict = {
            'q': '*:*',
            'fq': 'capacity:private', # Filtramos solo por capacidad privada
            'rows': registros,                 # No queremos la lista, solo el total
            'include_private': True
        }
        
        resultado = toolkit.get_action('package_search')(context, data_dict)
        return resultado['count']
    

    def formatos_raw(self,context:Context,registros):
        # Es vital usar ignore_auth para que el conteo sea real (vea todo)
            
        search_params = {
        'q': '*:*',
        'rows': registros,
        'facet': True,
        'facet.field': ['res_format'], # Pedimos los formatos
        'include_private': True
        }
        resultado = toolkit.get_action('package_search')(context, search_params)

        # Extraemos los formatos: CKAN los devuelve en una lista plana
        # Ejemplo: ['CSV', 10, 'PDF', 5] -> Queremos convertirlo a algo fácil para Angular
        formatos_raw = resultado.get('search_facets', {}).get('res_format', {}).get('items', [])
        
        # Los transformamos en un diccionario limpio: {"csv": 10, "pdf": 5}
        formatos_limpios = {f['name']: f['count'] for f in formatos_raw}
       
        log.warning(f"[DataJson[dashboard_stats][formatos_raw][data]={formatos_limpios}")
        return formatos_limpios