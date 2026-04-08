import ckan.plugins.toolkit as tk
from flask import Blueprint


estadistica = Blueprint(
    'estadistica', 
    __name__,
    url_prefix='/estadistica'
)

@estadistica.route('/form')
def form() -> str:
     
    u''' display about page'''
   
    return tk.render(u'estadistica/form.html')

@estadistica.route('/powerbi')
def powerbi() -> str:
     
    u''' display about page'''
   
    return tk.render(u'estadistica/powerbi.html')
    
@estadistica.route('/powerbi_1')    
def powerbi_1() -> str:
     
    u''' display about page'''
   
    return tk.render(u'estadistica/powerbi_1.html')

@estadistica.route('/powerbi_2')   
def powerbi_2() -> str:
     
    u''' display about page'''
   
    return tk.render(u'estadistica/powerbi_2.html')  
