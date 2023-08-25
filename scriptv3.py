import json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

# Load the GeoJSON data for the regions and the rivers
with open('./Municipalities_Risaralda.geojson') as f:
    regions_data = json.load(f)

with open('./RiverNetworkColombia.geojson') as f:
    rivers_data = json.load(f)

# Convert GeoJSON features to Shapely geometries
region_features = regions_data['features']  # Keep the region features as-is
river_features = rivers_data['features']  # Keep the river features as-is

# Create an empty list to store the filtered rivers for each region
filtered_rivers_by_region = []

# Iterate through each region feature
for region_feature in region_features:
    region_geom = shape(region_feature['geometry'])
    
    # Create a new list to store the filtered river features for this region
    filtered_rivers_for_this_region = []
    
    # Iterate through each river feature
    for river_feature in river_features:
        river_geom = shape(river_feature['geometry'])
        
        # Use intersection to get the river parts that are inside the region
        river_inside_region = region_geom.intersection(river_geom)
        
        # If the intersection is not empty, add the filtered river feature to the list
        if not river_inside_region.is_empty:
            filtered_river_feature = {
                "type": "Feature",
                "geometry": mapping(river_inside_region),
                "properties": {
                    **river_feature['properties'],  # Preserve river properties
                    "region_properties": region_feature['properties']  # Add region properties
                }
            }
            filtered_rivers_for_this_region.append(filtered_river_feature)
    
    # Create a GeoJSON feature collection for the filtered rivers in this region
    filtered_rivers_for_this_region_data = {
        "type": "FeatureCollection",
        "features": filtered_rivers_for_this_region
    }
    
    # Add the filtered rivers feature collection to the list
    filtered_rivers_by_region.append(filtered_rivers_for_this_region_data)

# Write the list of filtered rivers feature collections to a new GeoJSON file
with open('testv3.geojson', 'w') as f:
    json.dump(filtered_rivers_by_region, f)
