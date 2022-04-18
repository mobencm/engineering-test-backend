from sqlalchemy import Column, Integer, String, VARCHAR , ARRAY, Float
from geoalchemy2 import Geography

from db import Base


class property(Base):
    __tablename__ = "properties"

    id = Column(VARCHAR(100), unique=True, primary_key=True)
    geocode_geo = Column(Geography,nullable=False)
    parcel_geo = Column(Geography,nullable=False)
    building_geo = Column(Geography,nullable=False)
    image_bounds = Column(ARRAY(Float),nullable=False)
    image_url = Column(String,nullable=False)
