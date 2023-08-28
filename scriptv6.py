import json
from shapely.geometry import shape
from shapely.ops import unary_union
from collections import defaultdict

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
                    **river_feature['properties'],
                    "region_properties": region_feature['properties']  
                }
            }
            filtered_rivers_for_this_region.append(filtered_river_feature)
    
    # Add the filtered river features for this region to the final list
    final_filtered_features.extend(filtered_rivers_for_this_region)


# Create a dictionary to store the river features indexed by Mun_name
river_features_by_mun_name = defaultdict(list)

for filtered_river_feature in final_filtered_features:
    mun_name = filtered_river_feature['properties']['region_properties']['Mun_name']
    river_features_by_mun_name[mun_name].append(filtered_river_feature)

# Iterate through each group of features with the same Mun_name
for mun_name, features in river_features_by_mun_name.items():
    next_down_set = set()  # To store unique NEXT_DOWN values
    
    # Check if NEXT_DOWN value exists in any of the elements HYRIV_ID
    for feature in features:
        next_down = feature['properties']['NEXT_DOWN']
        hyriv_id = feature['properties']['HYRIV_ID']

        # Check if the current feature's next_down exists in other features' hyriv_id
        exists_in_other_hyriv = any(
            next_down == x['properties']['HYRIV_ID']
            for x in features if x != feature
        )

        # Only add distinct NEXT_DOWN values
        if not exists_in_other_hyriv:
            next_down_set.add(next_down)
    
    # Calculate SUM of DIS_AV_CMS values
    sum_dis_av_cms = sum(
        feature['properties']['DIS_AV_CMS']
        for feature in features
        if feature['properties']['NEXT_DOWN'] in next_down_set
    )
    
    # Update the SUM property for elements in this group
    for feature in features:
        feature['properties']['SUM'] = sum_dis_av_cms


# Create the final FeatureCollection for the filtered river features
final_filtered_feature_collection = {
    "type": "FeatureCollection",
    "features": final_filtered_features
}

# Write the final FeatureCollection to a new GeoJSON file
with open('filtered.geojson', 'w') as f:
    json.dump(final_filtered_feature_collection, f, ensure_ascii=False)
