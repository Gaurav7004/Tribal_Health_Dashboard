from shapely.geometry import shape
from shapely.ops import unary_union

def filter_geojson_by_district_ids(geojson, district_ids):
    return {
        "type": "FeatureCollection",
        "features": [
            feature for feature in geojson.get("features", [])
            if str(feature["properties"].get("district_id")) in set(map(str, district_ids))
        ]
    }

def filter_geojson_by_state_id(geojson, state_id):
    return {
        "type": "FeatureCollection",
        "features": [
            feature for feature in geojson.get("features", [])
            if str(feature["properties"].get("state_id")) == str(state_id)
        ]
    }

def compute_geojson_center(geojson):
    try:
        features = geojson.get("features", [])
        geometries = [
            shape(feature["geometry"])
            for feature in features
            if feature.get("geometry") is not None
        ]

        if not geometries:
            return {"lat": 22, "lon": 80}

        merged_geometry = unary_union(geometries)
        centroid = merged_geometry.centroid

        return {"lat": centroid.y, "lon": centroid.x}
    except Exception as e:
        print(f"[map_helper.py] Error computing centroid: {e}")
        return {"lat": 22, "lon": 80}
