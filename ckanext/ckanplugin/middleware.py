import logging
from flask import request
from ckan.plugins import toolkit

log = logging.getLogger(__name__)

def registrar_analytics():
    try:

        log.warning("[middleware][registrar_analytics] ejecutado")
        path = request.path

        # ----------------------------
        # VISTA DEL RECURSO
        # ----------------------------
        if "/dataset/" in path and "/resource/" in path and "/download/" not in path:

            parts = path.split("/")

            if "dataset" in parts and "resource" in parts:
                dataset_index = parts.index("dataset")
                resource_index = parts.index("resource")

                dataset_id = parts[dataset_index + 1]
                resource_id = parts[resource_index + 1]

                log.warning("[analytics] Vista resource %s", resource_id)

                toolkit.get_action("guardar_contador")(
                    {"ignore_auth": True},
                    {
                        "package_id": dataset_id,
                        "resource_id": resource_id,
                        "tipo": "Visualizacion"
                    }
                )

        # ----------------------------
        # DOWNLOAD NORMAL
        # ----------------------------
        if "/download/" in path:

            parts = path.split("/")

            dataset_index = parts.index("dataset")
            resource_index = parts.index("resource")

            dataset_id = parts[dataset_index + 1]
            resource_id = parts[resource_index + 1]

            log.warning("[analytics] Download resource %s", resource_id)

            toolkit.get_action("guardar_contador")(
                {"ignore_auth": True},
                {
                    "package_id": dataset_id,
                    "resource_id": resource_id,
                    "tipo": "Download"
                }
            )

        # ----------------------------
        # DOWNLOAD DATASTORE
        # ----------------------------
        if "/datastore/dump/" in path:

            resource_id = path.split("/")[-1].split("?")[0]

            log.warning("[analytics] Download datastore %s", resource_id)

            toolkit.get_action("guardar_contador")(
                {"ignore_auth": True},
                {
                    "package_id": None,
                    "resource_id": resource_id,
                    "tipo": "Download"
                }
            )

    except Exception as e:
        log.error("Error analytics: %s", e)