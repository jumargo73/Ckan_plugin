from setuptools import setup, find_packages

setup(
    name='ckanext-ckanplugin',
    version='0.1',
    description='Extension Para Diferentes Funciones',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points='''
        [ckan.plugins]  
        CkanPlugin=ckanext.ckanplugin.plugin_logic:CkanPlugin
        CsvGeoJsonApi=ckanext.ckanplugin.plugin:CSVtoGeoJSONApiPlugin
        CsvGeoJsonPlugin=ckanext.ckanplugin.CSVtoGeoJSON:CSVtoGeoJSONPlugin
        SelloExcelenciaPlugin=ckanext.ckanplugin.sello:SelloExcelenciaPlugin
        OdataPlugin=ckanext.ckanplugin.pluginOdata:ODataPlugin
        ShpPlugin=ckanext.ckanplugin.pluginZip_Shp:ShpPlugin    
        FixDateFormatPlugin=ckanext.ckanplugin.pluginFixDateFormatPlugin:FixDateFormatPlugin
        DataJSonPlugin=ckanext.ckanplugin.pluginAPI:DataJsonPlugin
    ''',
)
