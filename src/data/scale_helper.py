import json
import os

# Load the graph scales JSON
file_path = os.path.join(os.path.dirname(__file__), "graph_scales.json")

with open(file_path, "r") as f:
    graph_scales = json.load(f)

def get_scale_range(indicator_id):
    scale = graph_scales.get(str(indicator_id))  # JSON keys are strings
    if scale:
        return [scale["min"], scale["max"]]
    return None
