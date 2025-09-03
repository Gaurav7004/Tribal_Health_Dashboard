from dash import html, dcc

def IndicatorDropdown(id, data=None, label="Select an Indicator"):
    options = [{'label': item['indicator_name'], 'value': item['indicator_id']} for item in data] if data else []

    return html.Div([
        html.Label(label, style={'marginBottom': '5px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id=id,
            options=options,
            value=None,
            placeholder="Select an indicator...",
            style={'width': '100%'},
            optionHeight=110
        )
    ], style={"paddingLeft": "10px","paddingRight": "10px"})

# def IndicatorDropdown_tab2(id, label="Select Indicator (Tab 2)"):
#     return IndicatorDropdown(id=id, label=label)
