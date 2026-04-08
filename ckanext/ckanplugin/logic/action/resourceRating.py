import ckan.plugins.toolkit as tk
from ckan import model
from ckan.plugins import toolkit
from sqlalchemy import func
import ckan.model as model
from ckanext.ckanplugin.model.resourceRating import ResourceRating
import json, logging,os,  mimetypes

log = logging.getLogger(__name__)


def resource_rating_set(context, data_dict):

    try:
        log.warning("[action][resource_rating_set] ejecutado")
        tk.check_access('resource_rating_set', context, data_dict)

        resource_id = data_dict.get('resource_id')
        rating = data_dict.get('rating')
        user_id = data_dict.get('user_id')
    
        #log.warning("[action][resource_rating_set] resource_id %s",resource_id)
        #log.warning("[action][resource_rating_set] rating %s",rating)
        #log.warning("[action][resource_rating_set] user_id %s",user_id)

        if not resource_id:
            raise tk.ValidationError({'resource_id': 'Missing resource_id'})

        if not rating:
            raise tk.ValidationError({'rating': 'Missing rating'})

        rating = int(rating)

        if rating < 1 or rating > 5:
            raise tk.ValidationError({'rating': 'Rating must be between 1 and 5'})

    

        # Buscar si ya existe calificación del usuario
        existing = model.Session.query(ResourceRating).filter_by(
            package_Id=resource_id,
            user_id=user_id
        ).first()

        if existing:
            existing.ratings = rating            
            #log.warning("[action][resource_rating_set][existing] rating %s",existing.ratings)
            #log.warning("[action][resource_rating_set][existing] package_Id %s",existing.package_Id)
            #log.warning("[action][resource_rating_set][existing] user_id %s",existing.user_id)
        else:
            new_rating = ResourceRating(
                package_Id=resource_id,
                user_id=user_id,          
                ratings=rating,
            )

            #log.warning("[action][resource_rating_set][new_rating] %s",new_rating)
            
            model.Session.add(new_rating)
            

        resutl=model.Session.commit()
        #log.warning("[action][resource_rating_set] store resutl %s",resutl)

        return {'success': True}
    except Exception as e:
        log.error(
            f"[Action][resource_rating_set] Error al guardar la calificacion: {str(e)}"
        )
        return {'success': False}


def resource_rating_get(context, data_dict):

    try:

        log.warning("[action][resource_rating_get] ejecutado")

        tk.check_access('resource_rating_get', context, data_dict)

        resource_id = data_dict.get('resource_id')
        user_id = data_dict.get('user_id')
        #log.warning("[action][resource_rating_get] resource_id=%s",resource_id )
        #log.warning("[action][resource_rating_get] user_id %s",user_id) 

        if not resource_id:
            raise tk.ValidationError({'resource_id': 'Missing resource_id'})

        existing = model.Session.query(ResourceRating).filter_by(
            package_Id=resource_id,
            user_id=user_id
        ).first()
        
        #log.warning("[action][resource_rating_get] existing %s",existing)

        result = model.Session.query(
            func.avg(ResourceRating.ratings),
            func.count(ResourceRating.id)
        ).filter_by(package_Id=resource_id).first()

        #log.warning("[action][resource_rating_get] result %s",result)
        average = result[0] or 0
        count = result[1]

        #log.warning("[action][resource_rating_get] average=%s",float(round(average, 2)))
        #log.warning("[action][resource_rating_get] count=%s",count)
    

        return {
            'resource_id': resource_id,
            'average': float(round(average, 2)),
            'count': count,
            'user-rating':existing.ratings
        }
    
    except Exception as e:
        log.error(
            f"[Action][resource_rating_get] Error al recibir la calificacion: {str(e)}"
        )
        return {
            'resource_id': resource_id,
            'average': 0,
            'count': 0,
            'user-rating':0
        }
