# __init__.py
from ckanext.ckanplugin.pluginDatasetResource import CSVtoGeoJSONDatasetResourcePlugin
from ckanext.ckanplugin.CSVtoGeoJSON import CSVtoGeoJSONPlugin
from ckanext.ckanplugin.sello import SelloExcelenciaPlugin
from ckanext.ckanplugin.pluginOdata import ODataPlugin
from ckanext.ckanplugin.pluginZip_Shp import ShpPlugin
from ckanext.ckanplugin.pluginFixDateFormatPlugin import FixDateFormatPlugin
from ckanext.ckanplugin.pluginAPI import DataJsonPlugin
from ckanext.ckanplugin.plugin_logic import CkanPlugin
from ckanext.ckanplugin.plugin import CSVtoGeoJSONApiPlugin

__all__ = [
    "CSVtoGeoJSONDatasetResourcePlugin",
    "CSVtoGeoJSONPlugin",
    "SelloExcelenciaPlugin",
    "ODataPlugin",
    "ShpPlugin",
    "FixDateFormatPlugin",
    "DataJsonPlugin",
    "CkanPlugin",
    "CSVtoGeoJSONApiPlugin"
    ]

