from fastapi import APIRouter, Path,  Query, Depends
router = APIRouter()
from db import SessionLocal
import models
from sqlalchemy.orm import Session
from geoalchemy2 import func
from pydantic import BaseModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StatisticsResponse(BaseModel) :
    parcel_area_sqm : float
    building_area_sqm : float
    building_distance_m : float
    zone_density : float

@router.get("/{id}", response_model = StatisticsResponse)
async def statistics(id : str = Path(...,min_length=1),zone_size_m : int = Query(...,gt=0) , db: Session = Depends(get_db) ):
    property = db.query(models.property).filter(models.property.id == id).first()

    parcel_area_sqm = db.query(func.ST_Area(property.parcel_geo,True)).first()[0]

    building_area_sqm  = db.query(func.ST_Area(property.building_geo,True)).first()[0]

    centroid_property = db.query(func.ST_Centroid(property.parcel_geo)).first()[0]
    centroid_building = db.query(func.ST_Centroid(property.building_geo)).first()[0]
    building_distance_m = db.query(func.ST_Distance(centroid_property,centroid_building,True)).first()[0]

    circle_geo = db.query(func.ST_Buffer(property.geocode_geo, zone_size_m/1000, 'quad_segs=16')).first()[0]
    circle_sqm = db.query(func.ST_Area(circle_geo,True)).first()[0]

    intersection_property_circle = db.query(func.ST_Intersection(circle_geo,property.building_geo)).first()[0]
    intersection_sqm = db.query(func.ST_Area(intersection_property_circle,True)).first()[0]
    zone_density = (intersection_sqm /  circle_sqm ) * 100

    return StatisticsResponse(parcel_area_sqm=parcel_area_sqm,building_area_sqm=building_area_sqm,building_distance_m=building_distance_m,zone_density=zone_density)