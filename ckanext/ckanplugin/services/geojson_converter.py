import os, json, tempfile, shutil, mimetypes
from datetime import datetime
from shapely.geometry import Point, mapping
import logging
from ckan.common import config
import ckan.model as model
import os
from ckan.plugins.toolkit import get_action,request,config,g,check_access, ValidationError,c


log = logging.getLogger(__name__)





class GeoJSONConverter:

    @staticmethod
    def normalizar_coordenada_universal(valor):
        s = str(valor).strip()
        
        # Si tiene más de un punto, aplicamos la lógica de limpieza
        if s.count('.') > 1:
            # Buscamos la posición del PRIMER punto original
            posicion_primer_punto = s.find('.')
            
            # Quitamos todos los puntos
            solo_numeros = s.replace('.', '')
            
            # Si el número era negativo, la posición del punto se corre un lugar
            # Ejemplo: -76.16... -> el punto estaba en el índice 3
            nuevo_valor = solo_numeros[:posicion_primer_punto] + "." + solo_numeros[posicion_primer_punto:]
            return float(nuevo_valor)
        
        # Si ya es un float válido (un solo punto), lo devuelve tal cual
        try:
            return float(s)
        except ValueError:
            return None

        
    @staticmethod
    def detectar_columnas_coord(columnas):
        
        log.info("[GeoJSONConverter] detectar_columnas_coord ejecutado")
        
        lat_variants = ['lat', 'latitude', 'latitud','Latitud']
        lon_variants = ['lon', 'lng', 'longitud', 'longitude','Longitud']
        lat_col = next((c for c in columnas if c.lower() in lat_variants), None)
        lon_col = next((c for c in columnas if c.lower() in lon_variants), None)
        return lat_col, lon_col

    @staticmethod
    def convertir_a_geojson(self,records, lat_col, lon_col):
        
        log.info("[GeoJSONConverter][convertir_a_geojson] ejecutado")
        log.info(f"[GeoJSONConverter][convertir_a_geojson][lat_col] ={lat_col}")
        log.info(f"[GeoJSONConverter][convertir_a_geojson][lon_col]={lon_col}")
        features = []
        for row in records:
            try:
                #lat = float(row[lat_col])
                lat=self.normalizar_coordenada_universal(row[lat_col])
                #lon = float(row[lon_col])
                lon=self.normalizar_coordenada_universal(row[lon_col])
                features.append({
                    "type": "Feature",
                    "geometry": mapping(Point(lon, lat)),
                    "properties": row
                })
                #log.warning("[GeoJSONConverter] convertir_a_geojson features detectar_columnas_coord %s",features)
            except (ValueError, TypeError):
                log.error("[GeoJSONConverter] convertir_a_geojson ValueError detectar_columnas_coord %s",ValueError)
                log.error("[GeoJSONConverter] convertir_a_geojson TypeError detectar_columnas_coord %s",TypeError)
                continue

        return json.dumps({
            "type": "FeatureCollection",
            "features": features
        }, ensure_ascii=False)
    
    @classmethod
    def convertir_csv_geojson(cls, resource_id, geojson_id=None):
        """
        Convierte un recurso CSV del DataStore en GeoJSON.
        Si geojson_id está presente, actualiza el recurso existente;
        si no, crea uno nuevo.
        """
        try:
            log.info("[GeoJSONConverter][convertir_csv_geojson] ejecutado")
            #log.info("[CSVtoGeoJSONPlugin] convertir_csv_geojson ejecutado para recurso CSV %s", resource_id)

            context = {'ignore_auth': True}

            storage_path = config.get("ckan.storage_path")
            
            
            # 1. Obtener información del recurso CSV
            resource = get_action('resource_show')(context, {'id': resource_id})
            #log.info("[CSVtoGeoJSONPlugin] convertir_csv_geojson Recurso Encontrado: %s", json.dumps(resource, indent=2, ensure_ascii=False))
            package_id = resource['package_id']
            nombre_origen = resource['name']

            # 2. Obtener datos del DataStore
            data = get_action('datastore_search')(context, {'resource_id': resource_id})
            #log.info("[CSVtoGeoJSONPlugin] convertir_csv_geojson data Encontrado: %s", data)
            records = data.get('records', [])
            if not records:
                log.error("[CSVtoGeoJSONPlugin] convertir_csv_geojson Sin datos en DataStore para %s", resource_id)
                return

            # 3. Detectar columnas lat/lon
            columnas = list(records[0].keys())
            lat_col, lon_col = cls.detectar_columnas_coord(columnas)
            if not lat_col or not lon_col:
                log.warning("[GeoJSONConverter][convertir_csv_geojson] No se detectaron columnas lat/lon en %s", resource_id)
                return
                
            # 4. Convertir a GeoJSON
            geojson = cls.convertir_a_geojson(cls,records, lat_col, lon_col)
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] geojson = %s", geojson)

            # 5. Crear archivo temporal
            tmp_dir = tempfile.mkdtemp()
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] tmp_dir = %s", tmp_dir)
            base_name = os.path.splitext(nombre_origen)[0]      # ZonaWifi.csv -> ZonaWifi 
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] base_name = %s", base_name)   
            safe_name = base_name.replace(" ", "_") + ".geojson"    # ZonaWifi.geojson
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] safe_name = %s",safe_name) 
            tmp_path = os.path.join(tmp_dir, safe_name)
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] tmp_path = %s", tmp_path) 
            
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(geojson)
                
            size = os.path.getsize(tmp_path)
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] size = %s", size) 
            mime = mimetypes.guess_type(tmp_path)[0] or 'application/geo+json'
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] mime = %s", mime)   
            

            # 6. Crear o actualizar recurso GeoJSON
            if geojson_id:
                # Actualizar recurso existente
                #log.info("[CSVtoGeoJSONPlugin] convertir_csv_geojson Actualizando recurso GeoJSON existente ID=%s", geojson_id)
                update_data = {
                    'id': geojson_id,
                    'format': 'GeoJSON',
                    'url_type': 'upload',
                    'size': size,
                    'mimetype': mime,
                    'last_modified': datetime.utcnow().isoformat(),
                    'url': safe_name
                }
                #log.warning("[GeoJSONConverter][convertir_csv_geojson] update_data = %s", update_data)   
                response =  get_action('resource_update')(context, update_data)
                #log.warning("[GeoJSONConverter][convertir_csv_geojson] response  = %s", response )   
                
            else:
                # Crear recurso nuevo
                #log.info("[CSVtoGeoJSONPlugin] convertir_csv_geojson Creando nuevo recurso GeoJSON para paquete %s", package_id)
                create_data = {
                    'package_id': package_id,
                    'name': f"{base_name} (GeoJSON)",
                    'format': 'GeoJSON',
                    'description': 'Recurso generado automáticamente desde CSV',
                    'url_type': 'upload',
                    'size': size,
                    'mimetype': mime,
                    'last_modified': datetime.utcnow().isoformat(),
                }
                with open(tmp_path, 'rb') as f:
                    create_data['upload'] = f
                    #log.warning("[GeoJSONConverter][convertir_csv_geojson] create_data  = %s", create_data )  
                    response =  get_action('resource_create')(context, create_data)
                    #log.warning("[GeoJSONConverter][convertir_csv_geojson] response  = %s", response )  
                    #log.info("[CSVtoGeoJSONPlugin] convertir_csv_geojson crear_recurso_geojson Recurso creado: %s", json.dumps(response, indent=2, ensure_ascii=False))
                    
            
            # Parchar el campo `url` para que tenga el nombre correcto del archivo
            response=get_action('resource_patch')(context, {
                'id': response['id'],
                'url': safe_name
            })

            #log.warning("[GeoJSONConverter][convertir_csv_geojson] response  = %s", response )  

            # 7. Copiar archivo manualmente al storage_path
            
            geojson_res_id = response.get('id')
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] geojson_res_id  = %s", geojson_res_id )  

            resource_path = os.path.join(storage_path, "resources")    
            # CKAN divide el UUID en carpetas de 3 caracteres
            subdir = os.path.join(geojson_res_id[0:3], geojson_res_id[3:6])
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] subdir  = %s", subdir )  
            dest_dir = os.path.join(resource_path, subdir)
            #log.warning("[GeoJSONConverter][convertir_csv_geojson] dest_dir  = %s", dest_dir )  
            os.makedirs(dest_dir, exist_ok=True)

            shutil.copy(tmp_path, os.path.join(dest_dir, geojson_res_id[6:]))

            #log.info("[CSVtoGeoJSONPlugin][convertir_csv_geojson] GeoJSON copiado manualmente a %s", os.path.join(dest_dir, geojson_res_id[6:]))
                
            # 8. Limpiar archivo temporal
            shutil.rmtree(tmp_dir)

            get_action("resource_view_create")(context, {
                "resource_id": geojson_res_id,
                "title": "GeoJson",
                "view_type": "geojson_view"
            })

            
            #log.info("[CSVtoGeoJSONPlugin][convertir_csv_geojson] conversión a GeoJSON completada para %s", resource_id)

        except Exception as e:
                log.error(f"[GeoJSONConverter][convertir_csv_geojson] Error Creando el recurso: {e}")
    # Métodos auxiliares
    
   
    