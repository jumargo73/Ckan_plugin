import ckan.plugins.toolkit as tk
from ckan import model
from ckan.plugins import toolkit
from sqlalchemy import func
import ckan.model as model
from ckanext.ckanplugin.model.resourceRating import ResourceRating
import json, logging,os,  mimetypes

log = logging.getLogger(__name__)

def resource_rating_set(context, data_dict):
    return {'success': True}

def resource_rating_get(context, data_dict):
    return {'success': True}   