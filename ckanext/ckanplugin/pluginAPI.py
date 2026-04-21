from ckan.plugins import SingletonPlugin, implements,IPackageController, IResourceController
from ckan.plugins.interfaces import IConfigurer, IBlueprint
from ckan.plugins import toolkit
from ckan.common import config
import ckan.model as model
from ckan.model.resource import Resource  # ✅ Correcto import
from ckanext.ckanplugin.model.contador import Contador
from model import Session
from flask import Blueprint, jsonify, redirect, request, Response
from ckan.types import Context 
from typing import Any


import logging, json, subprocess, os
from datetime import datetime


log = logging.getLogger(__name__)


class DataJsonView(SingletonPlugin):
    implements(IBlueprint)
    log.info("[DataJson] DataJson Cargado con Exito")

    def get_blueprint(self):

        bp = Blueprint('data_json', __name__)

        log.info("[DataJson][get_blueprint][data_json] ejecutado")


        @bp.route('/ckan/dashboard', methods=['GET'])
        def ckan_dashboard_stats():
            return toolkit.render('estadistica/dashboard.html')
        

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

        @bp.route('/api/3/action/dataset_huerfanos', methods=['GET'])        
        def dataset_huerfanos():
            log.info("[data_json][dataset_huerfanos] ejecutado")
             
            context = {'model': model, 'session': model.Session, 'ignore_auth': True, 'user': 'opendata'}

            count_result = toolkit.get_action('package_search')(context, {
                    'rows': 0,
                    'include_private': True,
                    'fq': '+state:active'
                })
            registros = count_result['count']

            # 1. Obtener datasets sin grupo
            res_sin_grupo = toolkit.get_action('package_search')(context, {
                'q': '*:*',
                'fq': 'state:active AND -groups:[* TO *]',
                'rows': registros,
                'include_private': True
            })

            # 2. Obtener datasets sin organización
            res_sin_org = toolkit.get_action('package_search')(context, {
                'q': '*:*',
                'fq': 'state:active AND -owner_org:[* TO *]',
                'rows': registros,
                'include_private': True
            })

            # 3. Unir y eliminar duplicados usando el ID único
            # Usamos un diccionario para mantener el objeto completo pero evitar IDs repetidos
            unificados = {ds['id']: ds for ds in (res_sin_grupo['results'] + res_sin_org['results'])}

            # Retornamos la lista final
            return jsonify(list(unificados.values()))

       

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
            formatos_raw = self.get_stats_formatos(context,registros)   

            grupos_raw=self.get_stats_grupos(context,registros)        
          
            organizacion_raw=self.obtener_organizacion_facet(context,registros) 
            # ... (tus conteos de datasets, huérfanos y privados anteriores) ...

            stats_tematicas=self.get_stats_tematicas(context,registros) 

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
                'formatos_raw':formatos_raw,
                'grupos_raw' : grupos_raw,
                'organizacion_raw':organizacion_raw,
                'stats_tematicas':stats_tematicas
            })    
            log.warning(f"[DataJson[dashboard_stats][data]={data}")

            return data
            
        return bp 

    def obtener_organizacion_facet(self,context:Context,registros):
        # 'ignore_auth': True es lo que permite ver los privados sin restricciones
        
        data_dict = {
            'q': '*:*',
            'include_private': True,
            'rows': registros,
            'facet': True,
            'facet.field': ['organization']
        }
        
        resultado = toolkit.get_action('package_search')(context, data_dict)

        organizacion_raw = resultado.get('search_facets', {}).get('organization', {}).get('items', [])
        
        organizacion_limpios = {f['name']: f['count'] for f in organizacion_raw}

        organizacion_limpios['Total_Datasets']=resultado['count']

        log.warning(f"[DataJson[dashboard_stats][grupos_raw][data]={organizacion_limpios}")

        return organizacion_limpios    
    

    def get_stats_grupos(self,context:Context,registros):
        # 'ignore_auth': True es lo que permite ver los privados sin restricciones
        
        data_dict = {
            'q': '*:*',
            'include_private': True,
            'rows': registros,
            'facet': True,
            'facet.field': ['groups']
        }
        
        resultado = toolkit.get_action('package_search')(context, data_dict)

        grupos_raw = resultado.get('search_facets', {}).get('groups', {}).get('items', [])
        
        grupos_limpios = {f['name']: f['count'] for f in grupos_raw}

        grupos_limpios['Total_Datasets']=resultado['count']

        log.warning(f"[DataJson[dashboard_stats][grupos_raw][data]={grupos_limpios}")

        return grupos_limpios

    def obtener_huerfanos_totales(self,context:Context,registros):
        # 'ignore_auth': True es lo que permite ver los privados sin restricciones
        log.info("[data_json][obtener_huerfanos_totales] ejecutado")

        context = {'model': model, 'session': model.Session, 'ignore_auth': True, 'user': 'opendata'}

        count_result = toolkit.get_action('package_search')(context, {
                'rows': 0,
                'include_private': True,
                'fq': '+state:active'
            })
        registros = count_result['count']

        # 1. Obtener datasets sin grupo
        res_sin_grupo = toolkit.get_action('package_search')(context, {
            'q': '*:*',
            'fq': 'state:active AND -groups:[* TO *]',
            'rows': registros,
            'include_private': True
        })

        # 2. Obtener datasets sin organización
        res_sin_org = toolkit.get_action('package_search')(context, {
            'q': '*:*',
            'fq': 'state:active AND -owner_org:[* TO *]',
            'rows': registros,
            'include_private': True
        })

        # 3. Unir y eliminar duplicados usando el ID único
        # Usamos un diccionario para mantener el objeto completo pero evitar IDs repetidos
        unificados = {ds['id']: ds for ds in (res_sin_grupo['results'] + res_sin_org['results'])}

        # Retornamos la lista final
        data=list(unificados.values())
        
        return len(data)    

    
    def contar_privados(self,context:Context,registros):
        # Es vital usar ignore_auth para que el conteo sea real (vea todo)
            
        data_dict = {
            'q': '*:*',
            'fq': 'capacity:private', # Filtramos solo por capacidad privada
            'rows': registros,                 # No queremos la lista, solo el total
            'include_private': True,
            'facet.limit': -1,
            'facet.mincount': 1
        }
        
        resultado = toolkit.get_action('package_search')(context, data_dict)
        log.warning(f"[DataJson[dashboard_stats][contar_privados][resultado]={resultado}")
        return resultado['count']
    
    def get_stats_formatos(self,context:Context,registros):
        search_params = {
            'q': '*:*',
            'rows': 1000,
            'include_private': True,  # Trae públicos y privados
            'fq': 'state:active'      # Solo activos
        }
        
        results = toolkit.get_action('package_search')(context, search_params)
        stats_formatos = {}
        total_recursos=0

        for dataset in results.get('results', []):
            # Extraemos los recursos de cada dataset (sea público o privado)
            resources = dataset.get('resources', [])
            
            for res in resources:
                if res.get('state') == 'active':
                    # Normalizamos el formato (ej: 'csv', 'CSV', 'text/csv' -> 'CSV')
                    formato = res.get('format', 'Desconocido').upper().strip()
                    
                    if not formato:
                        formato = "S/F" # Sin Formato

                    if formato not in stats_formatos:
                        stats_formatos[formato] = 0
                    
                    stats_formatos[formato] += 1
                total_recursos+= 1
        # Convertimos a una lista de objetos para Angular
        formatos_json = [
            {'nombre': k, 'cantidad': v} 
            for k, v in stats_formatos.items()
        ]

        
        total_recursos={'nombre': 'total_recursos', 'cantidad': total_recursos}
        formatos_json.append(total_recursos)
        log.info(f"[DataJson][[dashboard_stats]][get_stats_formatos][total_recursos]={total_recursos}")
        
        # Ordenamos de mayor a menor
        formatos_json.sort(key=lambda x: x['cantidad'], reverse=True)
        
        return formatos_json

    def get_stats_tematicas(self,context:Context,registros):
        # 1. Obtenemos todos los datasets (ajusta 'rows' según tu volumen)
        search_params = {
            'q': '*:*',
            'rows': registros,
            'include_private': True,
            'fq': '+state:active'
        }
        results = toolkit.get_action('package_search')(context, search_params)
        log.info("[data_json][get_stats_tematicas][results]",results)
        
        stats = {}

        stats = {}

        for dataset in results.get('results', []):
            groups = dataset.get('groups', [])
            
            # --- AQUÍ ESTÁ EL TRUCO ---
            # Si la lista de grupos está vacía, saltamos al siguiente dataset inmediatamente
            if not groups:
                log.info("Saliendo de este dataset: No tiene temáticas asignadas.")
                continue 

            # 2. CONTEO MANUAL (La verdad absoluta)
            # En lugar de usar dataset.get('num_resources'), contamos los recursos activos
            recursos_activos = [
                res for res in dataset.get('resources', []) 
                if res.get('state') == 'active'
            ]
            conteo_real = len(recursos_activos)

            log.info(f"Dataset: {dataset.get('name')} | Estado: {dataset.get('capacity')} | Recursos Activos: {conteo_real}")

            for group in groups:
                group_name = group.get('name')
                if group_name not in stats:
                    stats[group_name] = {
                        'titulo': group.get('title') or group.get('display_name'),
                        'total_datasets': 0,
                        'total_recursos': 0,
                        'url_ver_mas': f'/group/{group_name}'
                    }
                
                # Solo sumará si el dataset pasó el 'if not groups'
                stats[group_name]['total_datasets'] += 1
                stats[group_name]['total_recursos'] += conteo_real

        # Convertimos el diccionario a una lista para que el JSON sea más fácil de recorrer en Angular
        return list(stats.values())
        

class DataJsonAPI(SingletonPlugin):
    implements(IPackageController)
    implements(IResourceController)

    #Eventos Resource

    def before_resource_create(self,context: Context, resource: dict[str, Any]):
        pass

    def after_resource_create(self,context: Context, resource: dict[str, Any]):
        pass

    def before_resource_update(self,context: Context, current: dict[str, Any], resource: dict[str, Any]):
        pass

    def after_resource_update(self, context, resource):
        pass        
   
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


    #Eventos Dataset

    def after_dataset_create(self,context: Context,  pkg_dict: dict[str, Any]):        
        return pkg_dict  

    def after_dataset_delete(self,context: Context, pkg_dict: dict[str, Any]):
        pass

    def before_dataset_show(self,context: Context, pkg_dict: dict[str, Any]):
        return pkg_dict

    def after_dataset_show(self,context: Context, pkg_dict: dict[str, Any]):    
        return pkg_dict
        
    def before_dataset_view(self,pkg_dict: dict[str, Any]):
        return pkg_dict  
        
    # --- dataset_search ---    
    def before_dataset_search(self,search_params: dict[str, Any]):
        return search_params           
    

    def after_dataset_search(self,search_results: dict[str, Any], search_params: dict[str, Any]):
        try:

            contadores=[]            
            
            # 1️⃣ Obtener contadores desde tu acción
            #contador_action = toolkit get_action('contador_get')
            context = {
                'model': model,
                'session': model.Session,
                'user':  toolkit.g.user or  toolkit.config.get('ckan.site_id')
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
        return search_results    

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
    
    def get_consolidado_contador(self,package_id): 
                
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
            datastore_response =  toolkit.get_action('datastore_search')(context,{'id': id})
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
    
class DataJsonPlugin(DataJsonView,DataJsonAPI):
    pass    