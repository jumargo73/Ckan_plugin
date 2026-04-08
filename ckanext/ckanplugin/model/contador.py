
from sqlalchemy import Column, UnicodeText, Integer, ForeignKey,String,UniqueConstraint
from ckan.model.meta import metadata
from ckan.model.types import make_uuid
from sqlalchemy.ext.declarative import declarative_base
import logging

log = logging.getLogger(__name__)

Base = declarative_base(metadata=metadata)

class Contador(Base):

    __tablename__ = 'contadores'

    id = Column(Integer, primary_key=True,autoincrement=True)
    package_Id = Column(String, nullable=False)
    source_Id = Column(String, nullable=False)
    contVistas = Column(Integer, nullable=False,default=0)
    contDownload = Column(Integer, nullable=False,default=0)

    __table_args__ = (
        UniqueConstraint('source_Id', 'package_Id',name='uix_source_package'),
    )

    def __init__(self, package_id=None, resource_id=None, contVistas=0, contDownload=0, **kwargs ):
        super().__init__(**kwargs)
        self.package_Id = package_id
        self.source_Id =  resource_id

        
        # Garantizar valores por defecto si no vienen
        self.contVistas = contVistas
        self.contDownload = contDownload
        
        log.warning("[Model][Contador][__init__] package_Id %s",self.package_Id)
        log.warning("[Model][Contador][__init__] source_Id %s",self.source_Id) 
        log.warning("[Model][Contador][__init__] contVistas %s",self.contVistas)
        log.warning("[Model][Contador][__init__] contDownload %s",self.contDownload)  
        