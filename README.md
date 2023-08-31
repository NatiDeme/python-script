Extract Script
=========================

Python Script that organizes the sum of river flow in a certain municipality.

### Prerequisite

- Make sure you have the latest `Python` version running on your machine.
- Make sure you have `shapely` library installed on your machine and globally accessible.
  
### Use

- Major detail parts of the code have comments on them so the user can go along.
- In case you don't have `shapely` library on your machine, run the code below.
 ```
  pip install shapely
  
  ````

- In order to use the code you have to provide Two `geojson` files manually.
- one file with the rivers and the other with regions consisting of municipalities.

After the necessary steps, just run the code in your code editor`(VS Code)` preferably
```py
import json
from shapely.geometry import shape
from shapely.ops import unary_union
from collections import defaultdict

# Load the GeoJSON data for the regions and the rivers
with open('./Municipalities_Risaralda.geojson') as f:
    regions_data = json.load(f)

with open('./RiverNetworkColombia.geojson') as f:
    rivers_data = json.load(f)
```
