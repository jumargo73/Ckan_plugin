import ckan.plugins.toolkit as tk
from ckan import model
from ckan.plugins import toolkit
from sqlalchemy import func
import ckan.model as model
import json, logging,os,  mimetypes
import logging
from ckan.model import Session
from ckanext.ckanplugin.model.contador import Contador

def guardar_contador(package_id, resource_id, tipo):

    try:
        log.warning("[helplers][guardar_contador] ejecutado")
        log.warning("[helplers][guardar_contador] package_id %s",package_id)
        log.warning("[helplers][guardar_contador] resource_id %s",resource_id)
        
        registro = Session.query(Contador).filter(           
            Contador.package_Id == package_id,
            Contador.source_Id == resource_id            
        ).first()

        log.warning("[helplers][guardar_contador] registro %s",registro)
        log.warning("[helplers][guardar_contador] tipo %s",tipo)   

        if not registro:
           
            if tipo == "Visualizacion":
                contVistas=1
                contDownload = 0
            elif tipo == "Download":
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
            elif tipo == "Download":
                registro.contDownload += 1
            #session.add(registro)
        
        log.warning("[helplers][guardar_contador] registro despues de contar package_Id %s",registro.package_Id) 
        log.warning("[helplers][guardar_contador] registro despues de contar source_Id %s",registro.source_Id)   
        log.warning("[helplers][guardar_contador] registro despues de contar contVistas %s",registro.contVistas)   
        log.warning("[helplers][guardar_contador] registro despues de contar contDownload %s",registro.contDownload)      
        
        Session.commit()  
        return True
    except Exception as e:
        log.error(
            f"[Helplers][obtener_contador_package] Error en obtener el contador: {str(e)}"
        ) 

        return False
