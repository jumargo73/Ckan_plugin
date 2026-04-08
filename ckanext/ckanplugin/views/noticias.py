import ckan.plugins.toolkit as tk
from flask import Blueprint


noticias = Blueprint(
    'noticias', 
    __name__,
    url_prefix='/noticias'
)


estadistica = Blueprint(u'noticias', __name__)

@noticias.route('/new')
def new() -> str:
     
    u''' display about page'''
   
    return tk.render(u'noticias/new.html')

@noticias.route('/new_1')
def new_1() -> str:
     
    u''' display about page'''
   
    return tk.render(u'noticias/new_1.html')

@noticias.route('/new_2')    
def new_2() -> str:
     
    u''' display about page'''
   
    return tk.render(u'noticias/new_2.html')   

@noticias.route('/new_3')
def new_3() -> str:
     
    u''' display about page'''
   
    return tk.render(u'noticias/new_3.html')      

