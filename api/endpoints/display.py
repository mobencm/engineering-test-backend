from fastapi import APIRouter , Path,Depends
from pydantic.color import Color
from typing import Optional, Union
from enum import Enum
from sqlalchemy.orm import Session
from models import property
from db import SessionLocal
import matplotlib.pyplot as plt
import rasterio
from rasterio import plot
from geoalchemy2 import shape
from io import BytesIO
from starlette.responses import StreamingResponse

router = APIRouter()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ColorlName(str, Enum):
    red = "red"
    green = "green"
    orange = "orange"

async def opentiff(url) :
    return rasterio.open(url)

@router.get("/{id}")
async def display_image(id : str = Path(..., title="Property ID" ), db: Session = Depends(get_db)):

    image_url = db.query(property.image_url).filter(property.id == id).first()[0]
    property_image = rasterio.open(image_url)
    fig, ax = plt.subplots()
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    plot.show(property_image, ax=ax)
    buf = BytesIO()
    plt.savefig(buf, format="jpeg")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")

@router.get("/{id}/overlays")
async def display_image_overlays(id : str,
                                 geocode : Optional[Union[Color,ColorlName]] = None ,
                                 parcel : Optional[Union[Color,ColorlName]] = None,
                                 building : Optional[Union[Color,ColorlName]]= None,
                                 db: Session = Depends(get_db)):


    features_query = []
    colors = []
    if (geocode) :
        features_query.append(property.geocode_geo)
        colors.append(geocode)
    if (parcel) :
        features_query.append(property.parcel_geo)
        colors.append(parcel)
    if (building) :
        features_query.append(property.building_geo)
        colors.append(building)


    image_url, *features_wkb = db.query(property.image_url, *features_query).filter(property.id == id).first()


    fig, ax = plt.subplots()
    property_image = rasterio.open(image_url)

    for wkb_element,color in zip(features_wkb,colors):
        vector_shape = shape.to_shape(wkb_element)
        if vector_shape.geom_type =='Point' :
            xs, ys = vector_shape.x, vector_shape.y
            plt.scatter(xs, ys, marker="*", s=800,c=str(color))
        if vector_shape.geom_type =='Polygon':
            xs, ys = vector_shape.exterior.xy
            ax.fill(xs, ys, alpha=0.5, fc=str(color))

    plot.show(property_image, ax=ax)
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)

    buf = BytesIO()
    plt.savefig(buf, format="jpeg")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")


