from app.db import Base
from app.db import BaseModelObject

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID


class Category(Base, BaseModelObject):
    __tablename__ = 'categories'
    uuid = Column(UUID, primary_key=True)
    name = Column(String(500), nullable=False, unique=True)
