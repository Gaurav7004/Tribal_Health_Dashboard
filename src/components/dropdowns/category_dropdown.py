from dash import html, dcc
from dash.dependencies import Input, Output

def CategoryDropdown(id, data, label="Select a Category"):
    # options = [{'label': item['categories'], 'value': item['categories_id']} for item in data]
    return html.Div([
        html.Label(label, style={'marginBottom': '5px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id=id,
            options=[],
            value=None,
            placeholder="Select a category...",
            style={'width': '100%'},
            optionHeight=60
        )
    ], style={"paddingLeft": "10px"})

# def CategoryDropdown_tab2(id, data, label="Select a Category (Tab 2)"):
#     return CategoryDropdown(id=id, data=data, label=label)
