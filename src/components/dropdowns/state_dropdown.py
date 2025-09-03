from dash import html, dcc
import dash
from dash.dependencies import Input, Output

def StateDropdown(id, data, label="Select a State"):
    # Extract state names for display and create value-label pairs
    options = [{'label': item['state_name'], 'value': item['state_id']} for item in data]
    
    return html.Div([
        html.Label(label, style={'marginBottom': '5px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id=id,
            options=options,
            value=None,
            placeholder="Select a state...",
            style={'width': '100%'}
        )
    ], style={"paddingLeft": "10px"})