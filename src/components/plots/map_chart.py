import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc
import textwrap
from src.data.scale_helper import get_scale_range  

# === Load GeoJSON Files ===
GEOJSON_BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
with open(os.path.join(GEOJSON_BASE, "NFHS5_statefiles.geojson"), "r", encoding="utf-8") as f:
    state_geojson = json.load(f)
with open(os.path.join(GEOJSON_BASE, "NFHS5_districtlevel.geojson"), "r", encoding="utf-8") as f:
    district_geojson = json.load(f)

# === MapChartComponent ===
def MapChartComponent(
    chart_id,
    data,              # list of dicts
    geojson,
    location_key,      # e.g. 'state_acronym'
    feature_id_key,    # e.g. 'properties.STUSPS'
    value_key,         # e.g. 'Total'
    label_key,         # e.g. 'state_name'
    title="Map",
    center=None,
    colorscale=None,
    indicator_id=None
):
    if not data:
        return _empty_map(chart_id, "No data available")

    # Build a DataFrame so px.express doesn't need to import pandas
    df = pd.DataFrame(data)

    # Replace invalid values
    df[value_key] = pd.to_numeric(df[value_key], errors="coerce")

    # Determine color range
    scale_range = get_scale_range(indicator_id)
    if scale_range:
        range_color = tuple(scale_range)
    else:
        v = df[value_key].dropna()
        range_color = (float(v.min()), float(v.max())) if not v.empty else (0, 100)

    # Prepare hover text
    df["hover_text"] = df.apply(
        lambda row: f"{row[label_key]}<br>Value: {row[value_key]:.1f}"
                    if pd.notna(row[value_key])
                    else f"{row[label_key]}<br>Value: NA",
        axis=1
    )

    # Default color scale
    if colorscale is None:
        colorscale = [[0.0, "#b6d6f4"], [0.5, "#a8d1f8"], [1.0, "#084594"]]

    # Zoom logic
    zoom = 5 if center and center != {"lat": 22, "lon": 80} else 3

    # Create the figure, passing in the DataFrame explicitly
    fig = px.choropleth_mapbox(
        df,                              # <— pass the DataFrame here
        geojson=geojson,
        locations=location_key,
        featureidkey=feature_id_key,
        color=value_key,
        color_continuous_scale=colorscale,
        range_color=range_color,
        mapbox_style="carto-positron",
        center=center or {"lat": 22, "lon": 80},
        zoom=zoom,
        hover_data=["hover_text"],       # use our hover_text column
    )

    # Use our hover_text column as the sole hover template
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        customdata=df[["hover_text"]].values,
        marker_line_color="black",
        marker_line_width=0.5,
    )

    # Layout tweaks
    fig.update_layout(
        title=dict(
            text="<br>".join(textwrap.wrap(title, width=50)),
            x=0.5,
            xanchor="center",
            font=dict(size=14),
            y=0.95
        ),
        margin={"r": 0, "t": 80, "l": 0, "b": 0},
        height=500,
    )

    return dcc.Graph(
        id=chart_id,
        figure=fig,
        config={"displayModeBar": False}
    )


def _empty_map(chart_id, message):
    return dcc.Graph(
        id=chart_id,
        figure=go.Figure(
            layout=go.Layout(
                title="No Data Available",
                template="plotly_white",
                height=400,
                annotations=[{
                    "text": message,
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "xanchor": "center",
                    "yanchor": "middle",
                    "showarrow": False,
                    "font": {"size": 16, "color": "gray"}
                }]
            )
        ),
        config={"displayModeBar": False}
    )
