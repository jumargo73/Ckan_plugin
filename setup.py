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
        SelloExcelenciaView=ckanext.ckanplugin.sello:SelloExcelenciaView
        Odata_Api=ckanext.ckanplugin.pluginOdata:ApiODataPluginView
        ShpGeoJsonPlugin=ckanext.ckanplugin.pluginZip_Shp:ShpPlugin    
        FixDateFormatPlugin=ckanext.ckanplugin.pluginFixDateFormatPlugin:FixDateFormatPlugin
        DataJSon=ckanext.ckanplugin.pluginAPI:DataJson
        DatasetResourcePlugin=ckanext.ckanplugin.pluginDatasetResource:CSVtoGeoJSONDatasetResourcePlugin
    ''',
)
