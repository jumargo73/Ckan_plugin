from ckanext.ckanplugin.model.contador import Contador
import ckan.model as model
from typing import (
    Any, Callable, Match, NoReturn, cast, Dict,
    Iterable, Optional, TypeVar, Union)
import ckan.plugins as p   
import logging
import ckan.logic as logic
from ckan.model import Session

log = logging.getLogger(__name__)

def obtener_contador_package(package_id):

    try:

        data={}
        datasetList=[]

        contVistas=0
        contDownload=0

        log.warning("[helplers][obtener_contador_package] ejecutado")

        
        #log.warning("[helplers][obtener_contador_package] package_id %s",package_id)

        registros = Session.query(Contador).filter(
            Contador.package_Id==package_id
        ).all()

        #log.warning("[helplers][obtener_contador_package] registros %s",registros)

        if not registros:
            
            data['package_id']=package_id
            data['contVistas']=0
            data['contDownload']=0

            datasetList.append(data)

            #log.warning("[helplers][obtener_contador_package] datasetList %s",datasetList)

            return datasetList
        
        for row in registros:
            contVistas+=row.contVistas
            contDownload+=row.contDownload

        data['package_id']=package_id
        data['contVistas']=contVistas
        data['contDownload']=contDownload
        datasetList.append(data)

        #log.warning("[helplers][obtener_contador_package] datasetList %s",datasetList)
        
        return datasetList

    except Exception as e:
        log.error(
            f"[Helplers][obtener_contador_package] Error en obtener el contador: {str(e)}"
        ) 

        return {}

def obtener_contador_resource(package_id, resource_id):

    try:
        
        data={}
        datasetList=[]

        contVistas=0
        contDownload=0
        registro = Session.query(Contador).filter(
            Contador.package_Id==package_id,
            Contador.source_Id==resource_id
        ).first()

        if not registro:
            data['package_id']=package_id
            data['resource_id']=resource_id
            data['contVistas']=0
            data['contDownload']=0

            datasetList.append(data)

            return datasetList
        else:

            data['package_id']=registro.package_Id
            data['resource_id']=registro.source_Id
            data['contVistas']=registro.contVistas
            data['contDownload']=registro.contDownload

            datasetList.append(data)
            return datasetList

    except Exception as e:
        log.error(
            f"[Helplers][obtener_contador_package] Error en obtener el contador: {str(e)}"
        ) 

        return {}


def guardar_contador(package_id, resource_id, tipo):

    try:
        log.warning("[helplers][guardar_contador] ejecutado")
        #log.warning("[helplers][guardar_contador] package_id %s",package_id)
        #log.warning("[helplers][guardar_contador] resource_id %s",resource_id)
        
        registro = Session.query(Contador).filter(           
            Contador.package_Id == package_id,
            Contador.source_Id == resource_id            
        ).first()

        #log.warning("[helplers][guardar_contador] registro %s",registro)
        #log.warning("[helplers][guardar_contador] tipo %s",tipo)   

        if not registro:
           
            if tipo == "Visualizacion":
                contVistas=1
                contDownload = 0
            elif tipo == "DownLoad":
                contVistas=0
                contDownload = 1
            
            registro = Contador(
                package_id=package_id,
                resource_id=resource_id,
                contVistas=contVistas,
                contDownload=contDownload
            )
            Session.add(registro)
        else:
            if tipo == "Visualizacion":
                registro.contVistas += 1                
            elif tipo == "DownLoad":
                registro.contDownload += 1
                
        
        #log.warning("[helplers][guardar_contador] registro despues de contar package_Id %s",registro.package_Id) 
        #log.warning("[helplers][guardar_contador] registro despues de contar source_Id %s",registro.source_Id)   
        #log.warning("[helplers][guardar_contador] registro despues de contar contVistas %s",registro.contVistas)   
        #log.warning("[helplers][guardar_contador] registro despues de contar contDownload %s",registro.contDownload)      
        
        Session.commit()  
    except Exception as e:
        log.error(
            f"[Helplers][obtener_contador_package] Error en obtener el contador: {str(e)}"
        ) 

        return False


def dataset_ciudad(pkg):
    return getattr(pkg, 'city', '')

def dataset_departamento(pkg):
    return getattr(pkg, 'department', '')

def dataset_frecuencia(pkg):
    return getattr(pkg, 'update_frequency', '')

def get_featured_dataset():
    """
    Procedimiento que consulta los grupos creadas en la BD y la muestra en una pagina HTML

    devuelve una Dict
    """ 
    data={}
    datasetList=[]

    
    datasets=ultimos_datasets()
    log.warning("[helplers][get_featured_dataset] dataset=%s",datasets)
    noPaquetes=2
    
    
    if datasets:
        noPaquetes=len(datasets)
        
        for i in range(noPaquetes):     
            fecha_data=datasets[i]["metadata_modified"][:10].split('-')
            año=fecha_data[0] 
            mes=fecha_data[1]
            dia=fecha_data[2]
            fecha=mes+'-'+dia+'-'+año
            data={"name":datasets[i]["name"],"type":datasets[i]["type"],"display_name":datasets[i]["name"],"title":datasets[i]["title"],"description":datasets[i]["notes"],"metadata_modified":fecha,"packageId":datasets[i]["id"],"sourceId":None}
            datasetList.append(data)
          
    return datasetList  


def ultimos_datasets():
    context = {"ignore_auth": True}
    data_dict = {
        "sort": "metadata_created desc",
        "rows": 3
    }

    result = p.toolkit.get_action("package_search")(context, data_dict)
    return result["results"]


def get_featured_estadistica():
    """
    Procedimiento que consulta los grupos creadas en la BD y la muestra en una pagina HTML

    devuelve una Dict
    """ 
    listNews=[]
    data={
        'name':'Formulario',
        'image_display_url':"/base/images/google-form.png",
        'type':'estadistica.form',
        'display_name':'Formulario',
        'description':'Para la Gobernación del Valle del Cauca es importante conocer su percepción de satisfacción frente al servicio recibido. Esta calificación nos permitirá mejorar el servicio que brindamos. Le sugerimos diligenciar la siguiente encuesta.'
    }
    listNews.append(data)
    data={
        'name':'Estadistica',
        'image_display_url':"/base/images/power-bi.png",
        'type':'estadistica.powerbi',
        'display_name':'Estadistica',
        'description':'La Gobernación en cifras. Vacunas. Salud DENGUE Casos Notificados: 71.386. Mortalidad: 20. Recuperados. Valle INN Emprendimientos: 7.884. Empleos react: 18.822'
    }
    listNews.append(data) 
    data={
        'name':'Estadistica',
        'image_display_url':"/base/images/power-bi.png",
        'type':'estadistica.powerbi_1',
        'display_name':'Formulario',
        'description':'Para la Gobernación del Valle del Cauca es importante conocer su percepción de satisfacción frente al servicio recibido. Esta calificación nos permitirá mejorar el servicio que brindamos. Le sugerimos diligenciar la siguiente encuesta.'
    }
    listNews.append(data)
   

    return listNews    


def get_featured_general():
    """
    Procedimiento que consulta los grupos creadas en la BD y la muestra en una pagina HTML

    devuelve una Dict
    """ 
    listNews=[]
    data={
        'name':'Disponibilidad de datos',
        'image_display_url':"/base/images/disponibilidad.PNG",
        'type':'https://datos.gob.es/es/informa-sobre/peticion-datos',
        'display_name':'Disponibilidad de datos',
        'description':'Si no encuentras los datos públicos que necesitas, puedes utilizar este formulario para que te facilitemos la búsqueda o para proponer la publicación de nuevos conjuntos de datos reutilizables.Tu propuesta será enviada al Organismo gestor y además será publicada en la sección “Disponibilidad de datos” desde donde podrás realizar un seguimiento de la misma.'
    }
    listNews.append(data)
    data={
        'name':'Iniciativas',
        'image_display_url':"/base/images/iniciativas.PNG",
        'type':"https://datos.gob.es/es/informa-sobre/iniciativas",
        'display_name':'Iniciativas',
        'description':'Si conoces alguna iniciativa de datos abiertos que no aparece en el "Mapa de iniciativas", utiliza este formulario para darla de alta y que así se muestre junto al resto.'
    }
    listNews.append(data)
    data={
        'name':'Empresas reutilizadoras',
        'image_display_url':"/base/images/Empresas_Reutilizadoras.PNG",
        'type':'https://datos.gob.es/es/informa-sobre/aplicaciones',
        'display_name':'Empresas reutilizadoras',
        'description':' Utiliza este formulario para informar sobre empresas que utilicen como materia prima datos abiertos del sector público. La empresa será incluida en la sección IMPACTO una vez haya sido revisado por el equipo de datos.gob.es.'
        }
    listNews.append(data)
   
    return listNews  


def get_featured_noticia():
    """
    Procedimiento que consulta los grupos creadas en la BD y la muestra en una pagina HTML

    devuelve una Dict
    """ 
    listNews=[]
    data={
        'name':'Pico y Placa',
        'image_display_url':"/base/images/new1.png",
        'type':'noticias.new',
        'display_name':'Pico y Placa',
        'description':"El 'pico y placa' para el segundo semestre de 2024 inicia el 2 de julio (teniendo en cuenta que el 1 es festivo) y se extiende hasta el 31 de diciembre. La gran novedad, en comparación con el primer semestre del calendario, es que se reduce una hora de la medida, que irá de 6:00 a.m. a 7:00 p.m., tomando como referencia el último dígito de la placa."
    }
    listNews.append(data)
    data={
        'name':'Mundial Sub20 Fem',
        'image_display_url':"/base/images/new2.png",
        'type':'noticias.new_1',
        'display_name':'Muerto en la Azotea',
        'description':'¿Hay boletas para ver a Colombia por los cuartos de final del Mundial Femenino sub 20? La situación del Pascual Guerrero de Cali?'
    }
    listNews.append(data)
    data={
        'name':'Mundial Sub20 Fem',
        'image_display_url':"/base/images/new3.png",
        'type':'noticias.new_2',
        'display_name':'Pico y Placa',
        'description':'En la tarde de este domingo 15 de septiembre se disputó en Cali el partido por los cuartos de final del Mundial de Fútbol Sub-20 Femenino entre la Selección Colombia y su similar de Países Bajos. El encuentro, que inició a las 4:30 de la tarde quedará en la historia de este torneo debido a el gran número de asistentes.'    }
    listNews.append(data)
   
    return listNews  


def get_featured_groups_new():
    """
    Procedimiento que consulta los grupos creadas en la BD y la muestra en una pagina HTML

    devuelve una Dict
    """ 

    groupList=[]
    #Procedimiento que consige la lista de Nombre de los gropos
    list=logic.get_action('group_list')({}, {})
    for group in list:
         data={}
         #Procedimiento que consige la informacion de los gropos en BD                        
         data=get_group_new(group)                                           
         if data["type"]=="group":
            #Creamos el Dict por cada groupo
            data={"name":data["name"],"type":data["type"],"display_name":data["display_name"],"title":data["title"],"description":data["description"],
                  "image_display_url":data["image_display_url"]}           
            #la agregamos a la lista
            groupList.append(data)
    #devolvemos en un Post hacia la pagina        
    return groupList 



def get_group_new(org: Optional[str] = None,
                     include_datasets: bool = False) -> dict[str, Any]:
    if org is None:
        return {}
    try:
        return logic.get_action('group_show')(
            {}, {'id': org, 'include_datasets': include_datasets})
    except (logic.NotFound, logic.ValidationError, logic.NotAuthorized):
        return {}



def contar_visualizacion(resource_id, package_id):
    guardar_contador(package_id, resource_id, "Visualizacion")


def contar_descargas(resource_id, package_id):
    guardar_contador(package_id, resource_id, "DownLoad")


