import geopandas as gpd
import json, logging,os,  mimetypes,zipfile,tempfile,sys,shutil
from datetime import datetime
from ckanapi import RemoteCKAN
#from ckan.plugins import toolkit
from ckanapi.errors import NotFound
import time
import certifi, requests

logging.basicConfig(
    filename="/var/log/ckan/convert_job.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)



def shp_to_geojson(shp_path, output_path=None):
    try:
        log.info(f"[ApiZipShpToGeojsonView][convert_job][shp_to_geojson] Iniciando conversión SHP a GeoJSON para Archivo {shp_path}")
        
        # 1. Leer SHP
        gdf = gpd.read_file(shp_path)

        # 2. REPROYECCIÓN (Clave para que el mapa no salga en blanco)
        # Convertimos de Origen Nacional (o lo que traiga) a WGS84 (GPS)
        if gdf.crs is not None:
            log.info("[ApiZipShpToGeojsonView][convert_job] Reproyectando a EPSG:4326...")
            gdf = gdf.to_crs(epsg=4326)

        # 3. SIMPLIFICACIÓN (Opcional pero recomendada para archivos de 245MB)
        # Esto reduce el peso del archivo sin perder la forma de los predios
        # gdf['geometry'] = gdf['geometry'].simplify(0.00001, preserve_topology=True)

        # 4. Definir salida como .geojson
        if not output_path:
            output_path = os.path.splitext(shp_path)[0] + ".geojson"

        # 5. Guardar como GeoJSON real
        gdf.to_file(output_path, driver='GeoJSON')
        
        log.info("[ApiZipShpToGeojsonView][convert_job][shp_to_geojson] GeoJSON generado con éxito en: %s", output_path)
        return output_path

    except Exception as e:
        log.error("[ApiZipShpToGeojsonView][convert_job][shp_to_geojson] Error en conversión: %s", e)
        return None


def shp_to_csv(shp_path, output_path=None, drop_geometry=False):
    
    try:
            
        """
        Convierte un SHP en CSV.
        - shp_path: ruta del archivo .shp
        - output_path: ruta donde guardar el CSV
        - drop_geometry: si True elimina geometría
        """
        log.info(f"[ApiZipShpToGeojsonView][convert_job][shp_to_csv] Iniciando conversión SHP a CVS para Archivo {shp_path}") 
        # Leer SHP
        gdf = gpd.read_file(shp_path)

        # Definir salida
        if not output_path:
            output_path = os.path.splitext(shp_path)[0] + ".csv"

        if drop_geometry:
            # Sin geometría → solo atributos
            df = gdf.drop(columns="geometry")
            df.to_csv(output_path, index=False)
        else:
            # Mantener geometría como WKT
            gdf.to_csv(output_path, index=False)
        log.info("[ApiZipShpToGeojsonView][convert_job][convert_job][shp_to_csv] CSV generado con éxito en: %s", output_path)
        return output_path
    except Exception as e:
            log.info("[convert_job] Error: %s",e)   


def shp_to_csv_points(shp_path, output_path=None):

    log.info("[ApiZipShpToGeojsonView][convert_job][shp_to_csv_points] ejecutado")
    gdf = gpd.read_file(shp_path)

    # Extraer lat/lon si es de puntos
    if gdf.geom_type.isin(["Point"]).all():
        gdf["lon"] = gdf.geometry.x
        gdf["lat"] = gdf.geometry.y
        gdf = gdf.drop(columns="geometry")

    if not output_path:
        output_path = os.path.splitext(shp_path)[0] + ".csv"

    gdf.to_csv(output_path, index=False)
    return output_path

def ensure_resource_exists(ckan, resource_id, retries=5, wait=3):
    """
    Verifica si el recurso existe en CKAN, reintenta si aún no está disponible.
    """
    for intento in range(retries):
        try:
            resource = ckan.action.resource_show(id=resource_id)
            log.info("[ApiZipShpToGeojsonView][convert_job][ensure_resource_exists] Recurso encontrado: %s", resource["id"])
            return resource
        except NotFound:
            log.warning("[ApiZipShpToGeojsonView][convert_job][ensure_resource_exists] Recurso %s no encontrado. Reintento %s/%s",
                        resource_id, intento + 1, retries)
            time.sleep(wait)
        except Exception as e:
            log.error("[ApiZipShpToGeojsonView][convert_job][ensure_resource_exists] Error inesperado: %s", e, exc_info=True)
            raise

    raise Exception(f"Recurso {resource_id} no disponible tras {retries} intentos")


def update_resource_exists(ckan, resource_id, size, last_modified,mimetype,output_path,dataset_name,formato,retries=5, wait=3):
    """
    Actualiza el recurso en CKAN, reintenta si aún no está disponible.
    """
    for i in range(retries):
        try:
            resource = ckan.action.resource_update(
                id=resource_id,
                name=os.path.basename(output_path),
                mimetype= mimetype,
                format=formato,
                url=os.path.splitext(dataset_name)[0] + ".csv",   
                size=size,
                last_modified=last_modified.isoformat()
            )
            log.info("[ApiZipShpToGeojsonView][convert_job][update_resource_exists] Recurso Actualizado: %s", resource_id)
            return resource
        except Exception as e:
            print(f"[WARN] Intento {i+1}/{retries} falló: {e}")
            time.sleep(wait)

    raise Exception(f"Recurso {resource_id} no actualizado tras {retries} intentos")


def upload_file(package_id,output_path,dataset_name,storage_path,ckan,tmpdir,formato):

    
    try:

        log.info(f"[ApiZipShpToGeojsonView][convert_job][upload_file] Creando Recurso para Archivo {output_path}")

        resource = ckan.action.resource_create(
            package_id=package_id,
            name=os.path.basename(output_path),
            format=formato,
            url=os.path.splitext(dataset_name)[0] + "."+formato,         # marcador interno que dice “es un recurso subido”
            url_type="upload"     # explícitamente indica que es un recurso local
        
        )

        log.info(f"[ApiZipShpToGeojsonView][convert_job][upload_file] Resource Creado en BD : {resource['id']}")


        #log.info("[convert_job] zip_shp_to_geojson resource create: %s", json.dumps(resource, indent=2, ensure_ascii=False))

        #Guardar el Recurso    
        resource_id = resource['id']
        
        #log.info("[convert_job] zip_shp_to_geojson resource_id=%s",resource_id)

        
        nuevo_nombre = resource_id[6:] 

        #log.info("[convert_job] zip_shp_to_geojson nuevo_nombre=%s",nuevo_nombre)

                
        

        # 2 Calcular ruta destino CKAN
        geojson_res_id = resource_id # UUID del recurso

        subdir = os.path.join('resources',geojson_res_id[0:3], geojson_res_id[3:6]) # Creacion Arbol donde va a qUUID del recurso
        dest_dir = os.path.join(storage_path,subdir)
        os.makedirs(dest_dir, exist_ok=True)
        

        # 3 Guardar Archivo
        nuevo_nombre = resource_id[6:] 
        dest_path = os.path.join(dest_dir, nuevo_nombre)
        
        if dataset_name is not None:
            shutil.move(output_path, dest_path)
            
        #log.info("[convert_job] zip_shp_to_geojson dest_path=%s",dest_path)

        # 4 Obtener size, last_modified y mimetype
        size = os.path.getsize(dest_path)
        last_modified = datetime.fromtimestamp(os.path.getmtime(dest_path))
        mimetype, encoding = mimetypes.guess_type(output_path, strict=True)
        
        resource_existe = ensure_resource_exists(ckan, resource_id)

        if format.lower()=="csv":              
            # Crear vista geoespacial si aplica
            view = ckan.action.resource_view_create(
                resource_id=resource_existe["id"],
                view_type="Table",
                title="Datatable_View"
            )
        elif format.lower()=="geojson":
            view = ckan.action.resource_view_create(
                resource_id=resource_existe["id"],
                view_type="GeoJson",
                title="GeoJSON_View"
            )   

        log.info(f"[ApiZipShpToGeojsonView][convert_job][upload_file] Vista creada: {view['id']} para recurso {resource['id']}")

        resource=update_resource_exists(ckan, resource_existe["id"],size, last_modified,mimetype,output_path,dataset_name,formato)
        
        log.info(f"[ApiZipShpToGeojsonView][convert_job][upload_file] Resource Actualizado: {resource['id']}")

        # Limpieza del temporal
        if format=="CSV":
            shutil.rmtree(tmpdir)

        log.info(f"[ApiZipShpToGeojsonView][convert_job][upload_file] Proceso para Recurso {resource['id']} finalizado con exito")

        return resource['id']

    except Exception as e:
        return None
        log.info("[convert_job][upload_file] Error: %s",e)  

def main():
    
    try:
        
        # sys.argv[0] = convert_job.py
        if len(sys.argv) < 5:
            log.error("Parámetros insuficientes. Esperados: zip_path, None, package_id, owner_org,filename")
            sys.exit(1)

        zip_path = sys.argv[1]      # Ruta al archivo zip o shp    
        package_id = sys.argv[2]   # ID del dataset
        owner_org = sys.argv[3]    # Organización
        dataset_name=sys.argv[4]   # nombre archivo
        site_url=sys.argv[5]
        api_key=sys.argv[6]
        storage_path=sys.argv[7]
        ssl_cert=sys.argv[8]
        isEvent=sys.argv[9]
        output_path = None       # Ese 'None' que mandas

        log.info("=== Iniciando job de conversión SHP → GeoJSON ===")
        #log.info("[main] Archivo: %s", zip_path)
        #log.info("[main] Package ID: %s", package_id)
        #log.info("[main] Owner Org: %s", owner_org)
        #log.info("[main] dataset_name: %s", dataset_name)
        
        
        log.info("[ApiZipShpToGeojsonView][convert_job][main] site_url: %s", site_url)
        log.info("[ApiZipShpToGeojsonView][convert_job][main] api_key: %s", api_key)
        log.info("[ApiZipShpToGeojsonView][convert_job][main] storage_path: %s", storage_path)
        log.info("[ApiZipShpToGeojsonView][convert_job][main] ssl_cert: %s", ssl_cert)

        session = requests.Session()
        session.verify = False 
        session.headers.update({'User-Agent': 'opendata'})

        ckan = RemoteCKAN(site_url, apikey=api_key,session=session)
        #ckan1 = RemoteCKAN(site_url, apikey=api_key,verify=ssl_cert)

        # Crear carpeta temporal
        with tempfile.TemporaryDirectory() as tmpdir:

            #zip_path = os.path.join(tmpdir, filename)

            #log.info("[convert_job] zip_shp_to_geojson zip_path=%s",zip_path)

            # Guardar el ZIP subido en el directorio temporal
            #archivo.save(zip_path)
            
            # Extraer el ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            # Buscar el .shp dentro del ZIP
            shp_file = None
            for root, _, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".shp"):
                        shp_file = os.path.join(root, f)
                        break

            if not shp_file:
                log.info("[ApiZipShpToGeojsonView][convert_job][main] No se encontró ningún .shp dentro del ZIP")
                #flash_error("Error: No se encontró ningún .shp dentro del ZIP")
            
            if not isEvent:
                formato="Zip"
                resource_id=upload_file(package_id,output_path,dataset_name,storage_path,ckan,tmpdir,formato)            
                log.info(f"[ApiZipShpToGeojsonView][convert_job][main] Recursos {resource_id} formato {formato} asociado a {package_id}-{dataset_name} path {output_path}")
            
            
            
            formato="CSV"
            output_path=shp_to_csv(shp_file, None, False)
            resource_id=upload_file(package_id,output_path,dataset_name,storage_path,ckan,tmpdir,formato)            
            log.info(f"[ApiZipShpToGeojsonView][convert_job][main] Recursos {resource_id} formato {formato} asociado a {package_id}-{dataset_name} path {output_path}")

            
            formato="GeoJSON"
            output_path=shp_to_geojson(shp_file, None)
            resource_id=upload_file(package_id,output_path,dataset_name,storage_path,ckan,tmpdir,formato)
            log.info(f"[ApiZipShpToGeojsonView][convert_job][main] Recursos {resource_id} formato {formato} asociado a {package_id}-{dataset_name} path {output_path}")

                        
            log.info("[ApiZipShpToGeojsonView][convert_job][main] Proceso de Conversion finalizado")

    except Exception as e:
            log.info("[ApiZipShpToGeojsonView][convert_job][main]Error: %s",e)     
    
if __name__ == "__main__":
    main()
