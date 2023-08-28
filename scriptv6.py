import json
from shapely.geometry import shape
from shapely.ops import unary_union

# Load the GeoJSON data for the regions and the rivers
with open('./Municipalities_Risaralda.geojson') as f:
    regions_data = json.load(f)

with open('./RiverNetworkColombia.geojson') as f:
    rivers_data = json.load(f)

# Convert GeoJSON features to Shapely geometries
region_features = regions_data['features']
river_features = rivers_data['features']

# Create an empty list to store the final filtered features
final_filtered_features = []


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
                "geometry": river_inside_region.__geo_interface__,
                "properties": {
                    **river_feature['properties'],  # Preserve river properties
                    "region_properties": region_feature['properties']  # Add region properties
                }
            }
            filtered_rivers_for_this_region.append(filtered_river_feature)
    
    # Add the filtered river features for this region to the final list
    final_filtered_features.extend(filtered_rivers_for_this_region)

# Create a dictionary to store the river features indexed by HYRIV_ID
river_features_by_hyrid = {}

for filtered_river_feature in final_filtered_features:
    hyriv_id = filtered_river_feature['properties']['HYRIV_ID']
    if hyriv_id not in river_features_by_hyrid:
        river_features_by_hyrid[hyriv_id] = []
    river_features_by_hyrid[hyriv_id].append(filtered_river_feature)


# Additional operation: For each river, check NEXT_DOWN and calculate SUM
for filtered_river_feature in final_filtered_features:
    region_properties = filtered_river_feature['properties']['region_properties']
    next_down = filtered_river_feature['properties']['NEXT_DOWN']
    hyriv_id = filtered_river_feature['properties']['HYRIV_ID']
    
    # Find the river features with the matching NEXT_DOWN
    if next_down in river_features_by_hyrid:
        next_down_features = river_features_by_hyrid[next_down]
        
        # Check if NEXT_DOWN value exists in any of HYRIV_ID values
        exists_in_any_hyriv_id = any(
            next_down == feature['properties']['HYRIV_ID']
            for feature in next_down_features
        )
        
        # If NEXT_DOWN doesn't exist, update the SUM for each feature
        if not exists_in_any_hyriv_id:
            dis_av_cms = filtered_river_feature['properties']['DIS_AV_CMS']
            sum_dis_av_cms = sum(
                feature['properties']['DIS_AV_CMS']
                for feature in next_down_features
            )
            
            # Update each feature's properties with the calculated SUM
            for feature in next_down_features:
                feature['properties']['SUM'] = dis_av_cms + sum_dis_av_cms

# Create the final FeatureCollection for the filtered river features
final_filtered_feature_collection = {
    "type": "FeatureCollection",
    "features": final_filtered_features
}

# Write the final FeatureCollection to a new GeoJSON file
with open('testv6.geojson', 'w', encoding='utf-8') as f:
    json.dump(final_filtered_feature_collection, f, ensure_ascii=False)
