"""
GIS-Utilities für Geometrie-Validierung und -Operationen
"""

from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from shapely.geometry.base import BaseGeometry
from pyproj import CRS, Transformer
from typing import Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger("sailight.gis")


def validate_geometry(geom: Optional[Dict[str, Any]]) -> bool:
    """
    Validiert eine Geometrie
    
    Args:
        geom: Geometrie als Dictionary (GeoJSON-Format)
    
    Returns:
        True wenn gültig, sonst False
    
    Raises:
        GISException: Wenn die Geometrie ungültig ist
    """
    if not geom:
        return True
    
    try:
        geometry_type = geom.get("type", "").lower()
        coordinates = geom.get("coordinates")
        
        if not coordinates:
            return True
        
        # Geometrie erstellen
        if geometry_type == "point":
            if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
                raise ValueError("Point muss genau 2 Koordinaten haben")
            point = Point(coordinates)
            if not point.is_valid:
                raise ValueError("Ungültige Point-Geometrie")
        
        elif geometry_type == "linestring":
            if not isinstance(coordinates, list) or len(coordinates) < 2:
                raise ValueError("LineString muss mindestens 2 Punkte haben")
            linestring = LineString(coordinates)
            if not linestring.is_valid:
                raise ValueError("Ungültige LineString-Geometrie")
        
        elif geometry_type == "polygon":
            if not isinstance(coordinates, list) or len(coordinates) < 1:
                raise ValueError("Polygon muss mindestens einen Ring haben")
            polygon = Polygon(coordinates[0], coordinates[1:] if len(coordinates) > 1 else None)
            if not polygon.is_valid:
                raise ValueError("Ungültige Polygon-Geometrie")
        
        elif geometry_type == "multipoint":
            points = [Point(coord) for coord in coordinates]
            multipoint = MultiPoint(points)
            if not multipoint.is_valid:
                raise ValueError("Ungültige MultiPoint-Geometrie")
        
        elif geometry_type == "multilinestring":
            linestrings = [LineString(coord) for coord in coordinates]
            multilinestring = MultiLineString(linestrings)
            if not multilinestring.is_valid:
                raise ValueError("Ungültige MultiLineString-Geometrie")
        
        elif geometry_type == "multipolygon":
            polygons = [Polygon(coord[0], coord[1:] if len(coord) > 1 else None) for coord in coordinates]
            multipolygon = MultiPolygon(polygons)
            if not multipolygon.is_valid:
                raise ValueError("Ungültige MultiPolygon-Geometrie")
        
        else:
            raise ValueError(f"Unbekannter Geometrie-Typ: {geometry_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"Geometrie-Validierung fehlgeschlagen: {e}")
        from app.utils.exceptions import GISException
        raise GISException(str(e))


def create_point(lon: float, lat: float) -> Dict[str, Any]:
    """Erstellt eine Point-Geometrie"""
    return {
        "type": "Point",
        "coordinates": [lon, lat]
    }


def create_linestring(coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Erstellt eine LineString-Geometrie"""
    return {
        "type": "LineString",
        "coordinates": coordinates
    }


def create_polygon(coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Erstellt eine Polygon-Geometrie"""
    # Schließe das Polygon
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
    
    return {
        "type": "Polygon",
        "coordinates": [coordinates]
    }


def calculate_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    units: str = "meters"
) -> float:
    """
    Berechnet die Entfernung zwischen zwei Punkten
    
    Args:
        point1: (Länge, Breite)
        point2: (Länge, Breite)
        units: Einheit (meters, kilometers, miles)
    
    Returns:
        Entfernung in der angegebenen Einheit
    """
    from geopy.distance import geodesic
    
    distance = geodesic(point1, point2)
    
    if units == "meters":
        return distance.meters
    elif units == "kilometers":
        return distance.kilometers
    elif units == "miles":
        return distance.miles
    else:
        return distance.meters


def buffer_geometry(
    geom: Dict[str, Any],
    distance: float,
    units: str = "meters"
) -> Dict[str, Any]:
    """
    Erstellt einen Buffer um eine Geometrie
    
    Args:
        geom: Geometrie als Dictionary
        distance: Buffer-Distanz
        units: Einheit (meters, kilometers)
    
    Returns:
        Neue Geometrie mit Buffer
    """
    try:
        geometry_type = geom.get("type", "").lower()
        coordinates = geom.get("coordinates")
        
        if geometry_type == "point":
            point = Point(coordinates)
            buffered = point.buffer(distance)
        elif geometry_type == "linestring":
            linestring = LineString(coordinates)
            buffered = linestring.buffer(distance)
        elif geometry_type == "polygon":
            polygon = Polygon(coordinates[0], coordinates[1:] if len(coordinates) > 1 else None)
            buffered = polygon.buffer(distance)
        else:
            raise ValueError(f"Ununterstützter Geometrie-Typ: {geometry_type}")
        
        # Konvertiere zurück zu GeoJSON
        if buffered.geom_type == "Polygon":
            coords = list(buffered.exterior.coords)
            return {"type": "Polygon", "coordinates": [coords]}
        elif buffered.geom_type == "MultiPolygon":
            coords = [[list(poly.exterior.coords) for poly in buffered.geoms]]
            return {"type": "MultiPolygon", "coordinates": coords}
        else:
            return {"type": buffered.geom_type, "coordinates": list(buffered.coords)}
            
    except Exception as e:
        logger.error(f"Buffer-Operation fehlgeschlagen: {e}")
        from app.utils.exceptions import GISException
        raise GISException(str(e))


def transform_coordinates(
    coordinates: Tuple[float, float],
    from_crs: str = "EPSG:4326",
    to_crs: str = "EPSG:3857"
) -> Tuple[float, float]:
    """
    Transformiert Koordinaten zwischen Koordinatensystemen
    
    Args:
        coordinates: (Länge, Breite)
        from_crs: Quell-Koordinatensystem
        to_crs: Ziel-Koordinatensystem
    
    Returns:
        Transformierte Koordinaten
    """
    try:
        transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
        return transformer.transform(coordinates[0], coordinates[1])
    except Exception as e:
        logger.error(f"Koordinaten-Transformation fehlgeschlagen: {e}")
        return coordinates


def get_centroid(geom: Dict[str, Any]) -> Tuple[float, float]:
    """
    Berechnet den Schwerpunkt einer Geometrie
    
    Args:
        geom: Geometrie als Dictionary
    
    Returns:
        (Länge, Breite) des Schwerpunkts
    """
    try:
        geometry_type = geom.get("type", "").lower()
        coordinates = geom.get("coordinates")
        
        if geometry_type == "point":
            return (coordinates[0], coordinates[1])
        elif geometry_type == "linestring":
            linestring = LineString(coordinates)
            return (linestring.centroid.x, linestring.centroid.y)
        elif geometry_type == "polygon":
            polygon = Polygon(coordinates[0], coordinates[1:] if len(coordinates) > 1 else None)
            return (polygon.centroid.x, polygon.centroid.y)
        else:
            raise ValueError(f"Ununterstützter Geometrie-Typ: {geometry_type}")
    except Exception as e:
        logger.error(f"Schwerpunkt-Berechnung fehlgeschlagen: {e}")
        return (0, 0)
