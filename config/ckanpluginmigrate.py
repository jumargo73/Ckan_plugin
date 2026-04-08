from alembic.config import Config
from alembic import command
import os

migration_path = "/usr/lib/ckan/default/src/ckan/ckanext/ckanplugin/migration/ckan"

cfg = Config(os.path.join(migration_path, "alembic.ini"))

# PON TU URL REAL AQUÍ
cfg.set_main_option("sqlalchemy.url", "postgresql://ckan_default:car2986@localhost/ckan_default")

command.upgrade(cfg, "head")
