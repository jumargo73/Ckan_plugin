import ckan.plugins.toolkit as tk
from ckan import model
from ckan.plugins import toolkit
from sqlalchemy import func
import ckan.model as model
import json, logging,os,  mimetypes


def guardar_contador(package_id, resource_id, tipo):
    return {'success': True}   