from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
import  geojson_pydantic
from geoalchemy2 import func
from geoalchemy2.shape import from_shape,to_shape
from sqlalchemy.orm import Session
router = APIRouter()
from db import SessionLocal
import models
from shapely import geometry
import json

class FindRequest( BaseModel) :
    location : geojson_pydantic.Point
    distance : float = Body(...,gt=0)


class PropertyFoundFields(BaseModel) :
    property_id : str
    distance_m : float
    closest_point : str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def find(request : FindRequest, db: Session = Depends(get_db)):


    location  = geometry.Point(request.location.coordinates[0], request.location.coordinates[1])

    wkb_point  = from_shape(location)

    results = db.query(models.property). \
        filter(func.ST_DWithin(models.property.geocode_geo, func.ST_GeogFromWKB(wkb_point), request.distance)).all()

    properties_found = []
    for result in results :

        property_id = result.id
        distance_m = db.query(func.ST_Distance(result.geocode_geo,wkb_point,True)).first()[0]
        closest_point = geometry.mapping(to_shape(db.query(func.ST_ClosestPoint(result.parcel_geo,wkb_point)).first()[0]))

        properties_found.append(PropertyFoundFields(property_id=property_id,distance_m=distance_m,closest_point=json.dumps(closest_point)))


    return properties_found