import dash, json
import requests
import dash_bootstrap_components as dbc
from dash import ctx, html, Output, Input, dcc, State, ALL, dash_table
from src.data.fetch_data import fetch_states, fetch_categories
from src.components.dropdowns.state_dropdown import StateDropdown
from src.components.dropdowns.category_dropdown import CategoryDropdown
from src.components.dropdowns.indicator_dropdown import IndicatorDropdown
from src.components.plots.bar_chart import BarChartComponent
from src.components.plots.violin_chart import ViolinChartComponent
from src.data.map_helper import filter_geojson_by_district_ids, compute_geojson_center
from src.components.plots.map_chart import MapChartComponent, district_geojson, state_geojson
from src.components.plots.bubble_chart import render_bubble_with_legend

BASE_URL = "http://localhost:8000"

def tab1_layout(states_data, placeholder_categories):
    return html.Div([

        # Top control row with loading spinners
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id="loading-state-dropdown-tab1",
                    type="circle",
                    children=StateDropdown(id='state-selection', data=states_data)
                ),
                width=4
            ),

            dbc.Col(
                dcc.Loading(
                    id="loading-radio-tab1",
                    type="circle",
                    children=dcc.RadioItems(
                        id='category-selection-type',
                        options=[{'label': i, 'value': i} for i in ['ST', 'Non-ST', 'Total']],
                        value='Total',
                        inline=True,
                        labelStyle={'marginRight': '10px'}
                    )
                ),
                width=4,
                style={"textAlign": "center", 'color': 'black', 'font-size': 20}
            ),

            dbc.Col(
                html.Div([
                    dcc.Loading(
                        id="loading-reset-btn-tab1",
                        type="circle",
                        children=dbc.Button("Reset", id="reset", color="primary", className="me-2")
                    ),
                    dcc.Loading(
                        id="loading-download-btn-tab1",
                        type="circle",
                        children=dbc.Button("Download", id="download-btn", color="success")
                    )
                ], className="d-flex justify-content-end"),
                width=4
            )
        ], style={"paddingRight": "10px"}, className="mb-3"),

        # Category dropdown with loading
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id="loading-category-dropdown-tab1",
                    type="circle",
                    children=CategoryDropdown(
                        id='category-selection-dropdown-tab1',
                        data=placeholder_categories
                    )
                ),
                width=4
            )
        ], className="mx-1 mb-3 gx-2"),

        # Indicator dropdowns
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id=f"loading-indicator-{i}-tab1",
                    type="circle",
                    children=IndicatorDropdown(id={'type': 'indicator-selection-tab1', 'index': i}, data=[])
                ),
                width=3
            ) for i in range(4)
        ], justify="between", className="mb-3 gx-2"),

        # Chart containers inside a single box
        dbc.Card(
            [
                dbc.CardHeader("Visualizations", className="fw-bold"),
                dbc.CardBody(
                    [
                        dcc.Loading(
                            id="loading-bar-tab1",
                            type="circle",
                            children=html.Div(id='bar-chart-container', style={"display": "none"})
                        ),
                        dcc.Loading(
                            id="loading-violin-tab1",
                            type="circle",
                            children=html.Div(id='violin-chart-container', style={"display": "none"})
                        ),
                        dcc.Loading(
                            id="loading-map-tab1",
                            type="circle",
                            children=html.Div(id='map-container', style={"display": "none"})
                        ),
                        dcc.Loading(
                            id="loading-bubble-tab1",
                            type="circle",
                            children=html.Div(id='bubble-chart-container', style={"display": "none"})
                        )
                    ],
                    style={"padding": "20px"}
                )
            ], className="mx-2"
        ),


        # AI Insights section
        dcc.Loading(
            id="loading-ai-tab1",
            type="circle",
            children=html.Div(
                dbc.Card([
                    dbc.CardHeader("Analytical Summary", className="fw-bold"),
                    dbc.CardBody([
                        html.Div(id="ai-insights-output-tab1")
                    ])
                ]),
                style={
                    "marginTop": "40px",
                    "marginBottom": "20px",
                    "paddingLeft": "10px",
                    "paddingRight": "10px"
                }
            )
        )
    ])

def tab2_layout(states_data, placeholder_categories):
    return html.Div([

        # Top control row with loading
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id="loading-state-dropdown-tab2",
                    type="circle",
                    children=StateDropdown(id='state-selection-tab2', data=states_data)
                ),
                width=4
            ),

            dbc.Col(
                dcc.Loading(
                    id="loading-radio-tab2",
                    type="circle",
                    children=dcc.RadioItems(
                        id='category-selection-type-tab2',
                        options=[{'label': i, 'value': i} for i in ['ST', 'Non-ST', 'Total']],
                        value='Total',
                        inline=True,
                        labelStyle={'marginRight': '10px'}
                    )
                ),
                width=4,
                style={"textAlign": "center", 'color': 'black', 'font-size': 20}

            ),

            dbc.Col(
                html.Div([
                    dcc.Loading(
                        id="loading-reset-btn-tab2",
                        type="circle",
                        children=dbc.Button("Reset", id="reset-tab2", color="primary", className="me-2")
                    ),
                    dcc.Loading(
                        id="loading-download-btn-tab2",
                        type="circle",
                        children=dbc.Button("Download", id="download-btn-tab2", color="success")
                    )
                ], className="d-flex justify-content-end"),
                width=4
            )
        ], style={"paddingRight": "10px"}, className="mb-3 gx-2"),

        # Category dropdowns A and B with loading
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id="loading-category-dropdown-tab2-a",
                    type="circle",
                    children=CategoryDropdown(
                        id='category-selection-dropdown-tab2-a',
                        data=placeholder_categories
                    )
                ),
                width=6
            ),
            dbc.Col(
                dcc.Loading(
                    id="loading-category-dropdown-tab2-b",
                    type="circle",
                    children=CategoryDropdown(
                        id='category-selection-dropdown-tab2-b',
                        data=placeholder_categories
                    )
                ),
                width=6
            )
        ], className="mx-1 mb-3"),

        # Indicator dropdowns with loading
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id=f"loading-indicator-{i}-tab2",
                    type="circle",
                    children=IndicatorDropdown(id={'type': 'indicator-selection-tab2', 'index': i}, data=[])
                ),
                width=3
            ) for i in range(4)
        ], justify="between", className="mt-3 mb-3 gx-2"),

        # Chart containers inside a single card
        dbc.Card(
            [
                dbc.CardHeader("Visualizations", className="fw-bold"),
                dbc.CardBody(
                    [
                        dcc.Loading(
                            id="loading-bar-tab2",
                            type="circle",
                            children=html.Div(id='bar-chart-container-tab2', style={"display": "none"})
                        ),
                        dcc.Loading(
                            id="loading-violin-tab2",
                            type="circle",
                            children=html.Div(id='violin-chart-container-tab2', style={"display": "none"})
                        ),
                        dcc.Loading(
                            id="loading-map-tab2",
                            type="circle",
                            children=html.Div(id='map-container-tab2', style={"display": "none"})
                        ),
                        dcc.Loading(
                            id="loading-bubble-tab2",
                            type="circle",
                            children=html.Div(id='bubble-chart-container-tab2', style={"display": "none"})
                        )
                    ],
                    style={"padding": "20px"}
                )
            ], className="mx-2 mt-3"
        ),

        # AI Insights section
        dcc.Loading(
            id="loading-ai-tab2",
            type="circle",
            children=html.Div(
                dbc.Card([
                    dbc.CardHeader("Analytical Summary", className="fw-bold"),
                    dbc.CardBody([
                        html.Div(id="ai-insights-output-tab2")
                    ])
                ]),
                style={
                    "marginTop": "40px",
                    "marginBottom": "20px",
                    "paddingLeft": "10px",
                    "paddingRight": "10px"
                }
            )
        )
    ])


def create_layout():
    app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.enable_dev_tools(debug=False)

    states_data = fetch_states()
    categories_data = fetch_categories()

    app.layout = dcc.Loading(
        id="global-loading",
        fullscreen=True,
        type="circle",
        children=html.Div([

            # === Fixed Header ===
            html.Div([
                dbc.Container([
                    dbc.Row([
                        dbc.Col(html.H2("Tribal Health FactSheet Dashboard", className="text-white fw-bold mb-0"), md="auto"),
                        dbc.Col(
                            dbc.Nav([
                                dbc.NavLink("Focused Indicator Comparison", className="text-white mb-0", href="#", active=True, id="tab-1", n_clicks=0),
                                dbc.NavLink("Indicator Comparison by Category", className="text-white mb-0", href="#", active=False, id="tab-2", n_clicks=0)
                            ], pills=True, justified=False, navbar=True, className="d-flex justify-content-end"),
                            width="auto"
                        )
                    ], align="center", justify="between")
                ], fluid=True)
            ], style={
                'backgroundColor': '#003a5d',
                'position': 'fixed',
                'top': '0',
                'zIndex': '1000',
                'width': '100%',
                'padding': '15px 20px',
                'boxShadow': '0 2px 6px rgba(0,0,0,0.3)'
            }),

            # Spacer below fixed header
            html.Div(style={'height': '10px'}),

            # === Sub-Nav Visualization Tabs ===
            html.Div([
                dbc.Container([
                    dbc.Row([
                        dbc.Col(html.H4("Indicators Data Visualization", className="text-white mb-0"), style={"backgroundColor": "#6abf4b"}),
                        dbc.Col(html.Div(id='visualization-nav', children=[
                            dbc.Nav([
                                dbc.NavLink("Geographic Distribution", href="#", n_clicks=0, id="tab-map-tab", style={"color": "white"}),
                                dbc.NavLink("Regional Indicator Insights", href="#", n_clicks=0, id="tab-bar-tab", style={"color": "white"}),
                                dbc.NavLink("Distribution & Density", href="#", n_clicks=0, id="tab-violin-tab", style={"color": "white"}),
                                dbc.NavLink("Bubble Correlation Matrix", href="#", n_clicks=0, id="tab-bubble-tab", style={"color": "white"}),
                            ], pills=True, justified=False, navbar=True, className="d-flex justify-content-end")
                        ]), width="auto")
                    ], align="center", justify="between", style={"backgroundColor": "#6abf4b"})
                ], fluid=True)
            ], id='sub-nav-header', style={
                'backgroundColor': "#6abf4b",
                'position': 'fixed',
                'top': '70px',
                'zIndex': '999',
                'width': '90%',
                'padding': '5px 20px',
                'display': 'none',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
            }),

            html.Div(id='sub-nav-spacer', style={'height': '140px'}),

            # === Tab Content ===
            html.Div(id='tab-1-container', children=tab1_layout(states_data, categories_data), style={'display': 'block'}),
            html.Div(id='tab-2-container', children=tab2_layout(states_data, categories_data), style={'display': 'none'}),

            # === Utility Components ===
            dcc.Store(id='main-tabs', data='tab-1'),
            dcc.Store(id='view-tab', data='tab-map-tab'),
            dcc.Download(id="download-figures"),
            dcc.Store(id='clicked-state-store'),
            html.Div(id='visualization-panel'),

            # === Footer ===
            html.Div([
                dbc.Container(
                    html.P("© 2025 PopulationCouncil Consulting", className="text-white text-center mb-0", style={"padding": "10px", "fontSize": "14px"})
                )
            ], style={"backgroundColor": "#003a5d", "marginTop": "auto"})
        ], style={
            'minHeight': '100vh',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'space-between',
            'width': '100%',
            'overflowX': 'hidden'
        })
    )

    
    ##################################################################################################
    ''' ****************************** Callbacks Tab 1 ************************************ '''
    ##################################################################################################

    ######## Control View and Active Tab Tab 1 ##############
    @app.callback(
        Output('tab-map-tab', 'active'),
        Output('tab-bar-tab', 'active'),
        Output('tab-violin-tab', 'active'),
        Output('tab-bubble-tab', 'active'),
        Input('view-tab', 'data')
    )
    def toggle_active_tabs(view_id):
        return (
            view_id == 'tab-map-tab',
            view_id == 'tab-bar-tab',
            view_id == 'tab-violin-tab',
            view_id == 'tab-bubble-tab'
        )
    
    @app.callback(
        Output('tab-1', 'active'),
        Output('tab-2', 'active'),
        Input('main-tabs', 'data')
    )
    def toggle_main_tab_active(tab_id):
        return tab_id == 'tab-1', tab_id == 'tab-2'

    @app.callback(
        Output('map-container', 'style'),
        Output('bar-chart-container', 'style'),
        Output('violin-chart-container', 'style'),
        Output('bubble-chart-container', 'style'),
        Output('map-container-tab2', 'style'),
        Output('bar-chart-container-tab2', 'style'),
        Output('violin-chart-container-tab2', 'style'),
        Output('bubble-chart-container-tab2', 'style'),
        Input('view-tab', 'data'),
        State('main-tabs', 'data')
    )
    def toggle_views(triggered_id, current_tab):
        # Initialize all 8 containers as hidden
        styles = [{'display': 'none'}] * 8

        # Decide the index shift based on the active tab
        base_index = 0 if current_tab == 'tab-1' else 4

        # Map tab IDs to the correct index
        index_map = {
            'tab-map-tab': 0,
            'tab-bar-tab': 1,
            'tab-violin-tab': 2,
            'tab-bubble-tab': 3
        }

        if triggered_id in index_map:
            output_index = base_index + index_map[triggered_id]
            styles[output_index] = {
                'display': 'flex' if 'map' in triggered_id or 'bar' in triggered_id else 'block',
                'flexWrap': 'wrap',
                'gap': '20px'
            }

        return styles
    
    @app.callback(
        Output('tab-1-container', 'style'),
        Output('tab-2-container', 'style'),
        Output('sub-nav-header', 'style'),
        Output('sub-nav-spacer', 'style'),
        Output('main-tabs', 'data'),
        Output('view-tab', 'data'),
        Input('tab-1', 'n_clicks'),
        Input('tab-2', 'n_clicks'),
        Input('tab-map-tab', 'n_clicks'),
        Input('tab-bar-tab', 'n_clicks'),
        Input('tab-violin-tab', 'n_clicks'),
        Input('tab-bubble-tab', 'n_clicks'),
        prevent_initial_call=True
    )
    def switch_tab_and_subtab(tab1_clicks, tab2_clicks, n_map, n_bar, n_violin, n_bubble):
        triggered_id = ctx.triggered_id or 'tab-1'

        sub_nav_style = {
            'backgroundColor': "#6abf4b",
            'position': 'fixed',
            'top': '70px',
            'zIndex': '999',
            'width': '100%',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'padding': '10px 20px',
            'display': 'block'
        }
        spacer_style = {'height': '140px'}

        if triggered_id in ['tab-map-tab', 'tab-bar-tab', 'tab-violin-tab', 'tab-bubble-tab']:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                triggered_id  
            )

        elif triggered_id == 'tab-2':
            return (
                {'display': 'none'},
                {'display': 'block'},
                sub_nav_style,
                spacer_style,
                'tab-2',
                'tab-map-tab'
            )

        else:
            return (
                {'display': 'block'},
                {'display': 'none'},
                sub_nav_style,
                spacer_style,
                'tab-1',
                'tab-map-tab' 
            )

    ### update Bar Chart Callback Tab 1 ###
    ### ************************* ###
    @app.callback(
        Output("bar-chart-container", "children"),
        Input({'type': 'indicator-selection-tab1', 'index': ALL}, 'value'),
        Input('category-selection-type', 'value'),
        Input('state-selection', 'value'),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_bar_charts(selected_indicators, category_type, selected_state, current_tab):
        if current_tab != 'tab-1':
            return []

        selected = [val for val in selected_indicators if val]

        if not selected:
            return [html.Div("No indicator selected")]

        if not category_type:
            category_type = "Total"

        try:
            response = requests.post(
                BASE_URL + "/getDistrictsByIndicators" if selected_state else BASE_URL + "/getStatesByIndicators",
                json={
                    "selected_indicators": selected,
                    "category_type": category_type,
                    "selected_state": selected_state
                }
            )

            response.raise_for_status()
        except Exception as e:
            return [html.Div(f"API Error: {str(e)}")]

        data = response.json().get("indicator_data", [])
        if not data:
            return [html.Div("API returned no data")]

        charts = []
        for ind in data:
            raw = ind["data"]
            indicator_name = ind["indicator_name"]

            label_field = "district_name" if selected_state else "state_name"
            y_vals = [entry[label_field] for entry in raw]
            x_vals = [entry.get(category_type, None) for entry in raw]

            if not y_vals or not any(x_vals):
                charts.append(html.Div(f"No data for {indicator_name}", style={"color": "orange"}))
                continue

            chart = BarChartComponent(
                chart_id=f"bar-chart-{ind['indicator_id']}",
                x_data=x_vals,
                y_data=y_vals,
                category_=category_type,
                label_field=label_field,
                title=indicator_name,
                indicator_id=ind['indicator_id']
            )
            charts.append(html.Div(chart, style={"marginBottom": "30px"}))

        if not charts:
            return [html.Div("No valid charts to display")]

        return charts

    ### update Violin Chart Callback Tab 1 ###
    ### **************************** ###
    @app.callback(
        Output("violin-chart-container", "children"),
        Input({'type': 'indicator-selection-tab1', 'index': ALL}, 'value'),
        Input('category-selection-type', 'value'),
        Input('state-selection', 'value'), 
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_violin_charts(selected_indicators, category_type, selected_state, current_tab):
        if current_tab != 'tab-1':
            return []

        selected = [val for val in selected_indicators if val]
        if not selected:
            return [html.Div("No indicator selected")]

        if not category_type:
            category_type = "Total"

        try:
            response = requests.post(
                BASE_URL + ("/getDistrictsByIndicators" if selected_state else "/getStatesByIndicators"),
                json={
                    "selected_indicators": selected,
                    "category_type": category_type,
                    "selected_state": selected_state
                }
            )
            response.raise_for_status()
        except Exception as e:
            return [html.Div(f"API Error: {str(e)}")]

        data = response.json().get("indicator_data", [])
        if not data:
            return [html.Div("API returned no data")]

        chart_components = []
        for ind in data:
            raw = ind["data"]
            indicator_name = ind["indicator_name"]

            label_field = "district_name" if selected_state else "state_name"
            x_vals = [entry.get(label_field, "Unknown") for entry in raw]
            y_vals = [entry.get(category_type, None) for entry in raw]

            if not y_vals or not any(y_vals):
                chart_components.append(html.Div(f"No data for {indicator_name}", style={"color": "orange"}))
                continue

            chart = ViolinChartComponent(
                chart_id=f"violin-chart-{ind['indicator_id']}",
                x_data=x_vals,
                y_data=y_vals,
                title=f"{indicator_name} ({category_type})"
            )
            chart_components.append(html.Div(chart, style={"marginBottom": "30px"}))

        if not chart_components:
            return [html.Div("No valid charts to display")]

        return html.Div(chart_components, style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'gap': '20px',
            'justifyContent': 'flex-start'
        })

    ### update map Chart Callback Tab 1 ###
    ### ************************* ###
    @app.callback(
        Output('map-container', 'children'),
        Input({'type': 'indicator-selection-tab1', 'index': ALL}, 'value'),
        Input('category-selection-type', 'value'),
        Input('state-selection', 'value'),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_map_tab1(selected_indicators, category_type, selected_state, current_tab):
        if current_tab != 'tab-1':
            return []

        selected = [val for val in selected_indicators if val]
        if not selected or not category_type:
            return []

        endpoint = "/getDistrictsByIndicators" if selected_state else "/getStatesByIndicators"

        try:
            response = requests.post(
                BASE_URL + endpoint,
                json={
                    "selected_indicators": selected,
                    "category_type": category_type,
                    "selected_state": selected_state
                }
            )
            response.raise_for_status()
            indicator_data = response.json().get("indicator_data", [])
        except Exception as e:
            return [html.Div(f"API Error: {str(e)}")]

        plots = []

        for i in range(4):  # fixed to 4 chart slots
            if i < len(indicator_data):
                indicator = indicator_data[i]
                raw = indicator["data"]
                indicator_name = indicator["indicator_name"]

                if selected_state:
                    filtered_geojson = filter_geojson_by_district_ids(
                        district_geojson,
                        [r["district_id"] for r in raw]
                    )
                    center = compute_geojson_center(filtered_geojson)
                    records = [
                        {
                            "district_id": r["district_id"],
                            "district_name": r["district_name"],
                            "value": r.get(category_type)
                        } for r in raw if r.get(category_type) is not None
                    ]
                    chart = MapChartComponent(
                        chart_id=f"map-chart-{i+1}",
                        data=records,
                        geojson=filtered_geojson,
                        location_key="district_name",
                        feature_id_key="properties.district_name",
                        value_key="value",
                        label_key="district_name",
                        title=f"{indicator_name} (District View)",
                        center=center
                    )
                else:
                    records = [
                        {
                            "state_acronym": r["state_acronym"],
                            "state_name": r["state_name"],
                            "value": r.get(category_type)
                        } for r in raw if r.get(category_type) is not None
                    ]
                    chart = MapChartComponent(
                        chart_id=f"map-chart-{i+1}",
                        data=records,
                        geojson=state_geojson,
                        location_key="state_acronym",
                        feature_id_key="properties.state_acronym",
                        value_key="value",
                        label_key="state_name",
                        title=f"{indicator_name} (State View)",
                        center={"lat": 22, "lon": 80}
                    )
            else:
                chart = MapChartComponent(
                    chart_id=f"map-chart-{i+1}",
                    data=[],
                    geojson={"type": "FeatureCollection", "features": []},
                    location_key="dummy",
                    feature_id_key="properties.dummy",
                    value_key="value",
                    label_key="dummy",
                    title="No Data"
                )

            plots.append(html.Div(chart, style={"width": "48%", "minWidth": "400px", "paddingLeft": "10px", "paddingRight": "10px"}))

        return plots

    ### update Bubble Chart Callback Tab 1 ###
    ### **************************** ###
    @app.callback(
        Output("bubble-chart-container", "children"),
        Input({'type': 'indicator-selection-tab1', 'index': 0}, 'value'),
        Input({'type': 'indicator-selection-tab1', 'index': 1}, 'value'),
        Input({'type': 'indicator-selection-tab1', 'index': 2}, 'value'),
        Input({'type': 'indicator-selection-tab1', 'index': 3}, 'value'),
        Input("category-selection-type", "value"),
        Input("state-selection", "value"),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_bubble_chart(ind_x, ind_y, ind_size, ind_color, hh_type, selected_state, current_tab):
        if current_tab != 'tab-1':
            return []

        indicators = [ind_x, ind_y, ind_size, ind_color]
        if not all(indicators) or not hh_type:
            return [html.Div("All 4 indicators and category type must be selected.")]

        endpoint = f"{BASE_URL}/getDistrictsByIndicators" if selected_state else f"{BASE_URL}/getStatesByIndicators"
        payload = {
            "selected_indicators": indicators,
            "category_type": hh_type,
            "selected_state": selected_state
        }

        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            response_json = response.json()
        except Exception as e:
            return [html.Div(f"API error: {str(e)}")]

        indicator_data = response_json.get("indicator_data", [])
        if not indicator_data:
            return [html.Div("No data returned from the server.")]

        indicator_id_to_name = {
            entry["indicator_id"]: entry["indicator_name"]
            for entry in indicator_data
        }

        label_key = "district_name" if selected_state else "state_name"

        merged = {}
        for indicator in indicator_data:
            name = indicator["indicator_name"]
            for row in indicator["data"]:
                key = row[label_key]
                if key not in merged:
                    merged[key] = {label_key: key}
                merged[key][name] = row.get(hh_type)

        cleaned = [
            row for row in merged.values()
            if all(indicator_id_to_name.get(i) in row and row[indicator_id_to_name.get(i)] is not None for i in indicators)
        ]

        if not cleaned:
            return [html.Div("No usable data found for the selected indicators.")]

        x_key = indicator_id_to_name[ind_x]
        y_key = indicator_id_to_name[ind_y]
        size_key = indicator_id_to_name[ind_size]
        color_key = indicator_id_to_name[ind_color]

        chart = render_bubble_with_legend(
            chart_id="bubble-chart",
            data=cleaned,
            x_key=x_key,
            y_key=y_key,
            size_key=size_key,
            color_key=color_key,
            label_key=label_key
        )

        return [chart]


    ### State Selction Tab 1 ###
    ### ************** ###
    @app.callback(
            [Output('category-selection-type', 'value'),
            Output({'type': 'indicator-selection-tab1', 'index': ALL}, 'value')],
            Input('state-selection', 'value'),
            prevent_initial_call=True
        )
    def update_on_state_selection(selected_state):
        if selected_state is None:
            raise dash.exceptions.PreventUpdate

        # Reset category selection and all indicator dropdowns
        reset_category = "Total"
        reset_indicators = [None for _ in range(4)]
        
        return reset_category, reset_indicators


    ### Category and Indicator Dropdown Callback Tab 1 ###
    ### ********************************************** ###
    @app.callback(
        Output("category-selection-dropdown-tab1", "options"),
        Input("category-selection-dropdown-tab1", "value"),
    )
    def update_category_dropdowns(categories_data):
        # Simulated or fetched categories list
        categories_data = fetch_categories()  
        # Convert to dropdown options
        options = [
            {"label": c["categories"], "value": c["categories_id"]}
            for c in categories_data
        ]

        return options
    
    @app.callback(
        Output({'type': 'indicator-selection-tab1', 'index': dash.ALL}, 'options'),
        Input({'type': 'indicator-selection-tab1', 'index': dash.ALL}, 'value'),
        Input('category-selection-dropdown-tab1', 'value'),
        prevent_initial_call=True
    )
    def update_indicator_dropdowns(selected_values, selected_category):
        if selected_category is None:
            return [[] for _ in range(4)]
        
        response = requests.post(BASE_URL  + "/receiveCategories", json={"selected_value": selected_category})

        if response.status_code == 200:
            # Full list of indicators from backend
            indicators = response.json().get("state_indicators", [])
            options_all = [{"label": i["indicator_name"], "value": i["indicator_id"]} for i in indicators]

            # Build options for each dropdown based on others' selected values
            options_per_dropdown = []
            for i in range(len(selected_values)):
                used_values = set(selected_values) - {selected_values[i]}
                filtered_options = [opt for opt in options_all if opt["value"] not in used_values]
                options_per_dropdown.append(filtered_options)

            return options_per_dropdown
        else:
            return [[] for _ in range(4)]
        
    ########### AI INSIGHTS TAB 1 ########
    ######################################
    @app.callback(
        Output("ai-insights-output-tab1", "children"),
        Input({'type': 'indicator-selection-tab1', 'index': ALL}, 'value'),
        Input('state-selection', 'value'),
        Input('category-selection-type', 'value'),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_ai_insights_tab1(selected_indicators, selected_state, category_type, active_tab):
        if active_tab != 'tab-1':
            return []
        
        if not category_type:
            category_type = "Total"
        
        selected = [val for val in selected_indicators if val]
        if not selected:
            return [
                html.Div([
                    html.H4("📊 AI Insights", className="insights-header"),
                    html.P("Please select at least one indicator to generate an insight.", 
                        className="no-selection-message")
                ], className="insights-container")
            ]
        
        try:
            # Fetch indicator data
            endpoint = "/getDistrictsByIndicators" if selected_state else "/getStatesByIndicators"
            payload = {
                "selected_indicators": selected,
                "category_type": category_type,
                "selected_state": selected_state
            }
            response = requests.post(BASE_URL + endpoint, json=payload)
            response.raise_for_status()
            indicator_data = response.json().get("indicator_data", [])
            
            # --- Fetch stats table from new API ---
            stats_payload = {
                "selected_indicators": selected,
                "category_type": category_type,
                "selected_state": selected_state
            }
            stats_response = requests.post(BASE_URL + "/indicator-stats", json=stats_payload)
            correlation_response = requests.post(BASE_URL + "/indicator-correlation", json=stats_payload)

            stats_response.raise_for_status()
            correlation_response.raise_for_status()
            
            stats_data = stats_response.json().get("stats", [])
            correlation_data = correlation_response.json().get("correlations", [])

            # Convert stats_data into an HTML table
            if stats_data:
                table_header = [html.Th(col) for col in stats_data[0].keys()]
                table_rows = [
                    html.Tr([html.Td(str(val)) for val in row.values()])
                    for row in stats_data
                ]
                stats_table = html.Div(
                    [
                        # html.H4("📊 Indicator Statistics", className="table-title"),
                        html.Table(
                            [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)],
                            className="stats-table"
                        )
                    ],
                    className="stats-table-container"
                )
            else:
                stats_table = html.P("No statistics available.", className="no-stats-message")

            if correlation_data:
                table_header = [html.Th(col) for col in correlation_data[0].keys()]
                table_rows = [
                    html.Tr([html.Td(str(val)) for val in row.values()])
                    for row in correlation_data
                ]
                correlation_table = html.Div(
                    [
                        html.Table(
                            [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)],
                            className="stats-table"
                        )
                    ],
                    className="stats-table-container"
                )
            else:
                correlation_table = html.P("No statistics available.", className="no-stats-message")
            
            # --- Call AI summary endpoint ---
            summary_payload = {
                "selected_indicators": selected,
                "category_type": category_type,
                "selected_state": selected_state
            }
            try:
                summary_response = requests.post(BASE_URL + "/indicator-summary", json=summary_payload)
                summary_response.raise_for_status()
                summary_text = summary_response.json().get("summary", "No summary generated.")
            except requests.RequestException as e:
                summary_text = f"⚠️ Error generating summary: {str(e)}"
            
            # --- Final Layout ---
            return [
                html.Div([
                    html.Div([
                        html.H4("Indicator Description", className="stats-header"),
                    ], className="section-container"),

                    # Stats Table
                    html.Div([
                        stats_table
                    ], className="stats-container"),

                    html.Div([
                        html.H4("Indicator Correlation", className="stats-header"),
                    ], className="section-container"),

                    html.Div([
                        correlation_table
                    ], className="stats-container"),

                    html.Div([
                        html.H4("Analytical Summary", className="section-header"),
                        html.Div(
                            summary_text,
                            className="summary-box",   # <-- style this in CSS
                            style={
                                "border": "1px solid #ccc",
                                "padding": "12px",
                                "borderRadius": "8px",
                                "backgroundColor": "#f9f9f9",
                                "whiteSpace": "pre-wrap"
                            }
                        )
                    ], className="summary-container"),

                    html.Div([
                        html.Div(id="copy-confirmation", className="copy-confirmation")
                    ], className="insights-actions"),

                    # html.Div([
                    #     html.H4("📊 Analysis", className="section-header"),
                    # ], className="section-container"),

                    # html.Div([
                    #     html.H4("⚖️ Comparison of the Indicators", className="section-header"),
                    # ], className="section-container"),

                    # html.Div([
                    #     html.H4("📝 Conclusion", className="section-header"),
                    # ], className="section-container"),
                    
                ], className="insights-container")
            ]


        except requests.RequestException as e:
            return [
                html.Div([
                    html.H4("⚠️ Connection Error", className="error-title"),
                    html.P(f"Unable to fetch AI insights: {str(e)}", 
                        className="error-message"),
                    html.Button("🔄 Retry", id="retry-insights-btn", 
                            className="retry-button")
                ], className="error-container")
            ]
        except Exception as e:
            return [
                html.Div([
                    html.H4("❌ Error", className="error-title"),
                    html.P(f"An unexpected error occurred: {str(e)}", 
                        className="error-message")
                ], className="error-container")
            ]


    ''' -------     TAB 2 Callbacks   -------'''
    ############################################

    ### Category and Indicator Dropdown Callback Tab-2-a and Tab-2-b ###
    ### ************************************************************ ###

    # Define related category mappings (adjust based on your rules)
    CATEGORY_RELATIONS = {
        1: [2],   # A -> can only compare with B
        2: [1],   # B -> can only compare with A
        3: [4, 5, 6],  # C -> related to maternity/delivery/postnatal
        4: [3, 5, 6],
        5: [3, 4, 6],
        6: [3, 4, 5],
        7: [8],   # Child health -> Child nutrition
        8: [7, 9],
        9: [8],   # Nutrition adults -> child nutrition
        10: [11], # Diabetes -> Hypertension
        11: [10], # Hypertension -> Diabetes
        12: [13], # Substance use -> Infectious disease (example)
        13: [12],
        14: [15, 16], # Women's empowerment -> Gender violence, HIV knowledge
        15: [14],
        16: [14]
    }

    @app.callback(
        Output("category-selection-dropdown-tab2-a", "options"),
        Output("category-selection-dropdown-tab2-b", "options"),
        Input("category-selection-dropdown-tab2-a", "value"),
        Input("category-selection-dropdown-tab2-b", "value"),
    )
    def update_category_dropdowns_tab2(selected_a, selected_b):
        categories_data = fetch_categories()

        # Convert all categories into dropdown format
        all_options = [
            {"label": c["categories"], "value": c["categories_id"]}
            for c in categories_data
        ]

        if selected_a:
            allowed_b_ids = CATEGORY_RELATIONS.get(selected_a, [])
            options_b = [opt for opt in all_options if opt["value"] in allowed_b_ids]
        else:
            options_b = all_options

        if selected_b:
            allowed_a_ids = CATEGORY_RELATIONS.get(selected_b, [])
            options_a = [opt for opt in all_options if opt["value"] in allowed_a_ids]
        else:
            options_a = all_options

        return options_a, options_b


    @app.callback(
        Output({'type': 'indicator-selection-tab2', 'index': dash.ALL}, 'options'),
        Input({'type': 'indicator-selection-tab2', 'index': dash.ALL}, 'value'),
        Input('category-selection-dropdown-tab2-a', 'value'),
        Input('category-selection-dropdown-tab2-b', 'value'),
        prevent_initial_call=True
    )
    def update_indicator_dropdowns_tab2(selected_values, category_a, category_b):
        total_dropdowns = 4
        options_per_dropdown = [[] for _ in range(total_dropdowns)]

        # Helper function to get indicator options
        def get_options(category):
            if category is None:
                return []
            response = requests.post(BASE_URL + "/receiveCategories", json={"selected_value": category})
            if response.status_code == 200:
                indicators = response.json().get("state_indicators", [])
                return [{"label": i["indicator_name"], "value": i["indicator_id"]} for i in indicators]
            return []

        # Process first two dropdowns (category A)
        if category_a:
            options_a = get_options(category_a)
            for i in range(2):
                used_values = set(selected_values[:2]) - {selected_values[i]}
                filtered_options = [opt for opt in options_a if opt["value"] not in used_values]
                options_per_dropdown[i] = filtered_options

        # Process last two dropdowns (category B)
        if category_b:
            options_b = get_options(category_b)
            for i in range(2, 4):
                used_values = set(selected_values[2:]) - {selected_values[i]}
                filtered_options = [opt for opt in options_b if opt["value"] not in used_values]
                options_per_dropdown[i] = filtered_options

        return options_per_dropdown

    ### update Bar Chart Callback tab2 ###
    ### ****************************** ###
    @app.callback(
        Output("bar-chart-container-tab2", "children"),
        Input({'type': 'indicator-selection-tab2', 'index': ALL}, 'value'),
        Input('category-selection-dropdown-tab2-a', 'value'),
        Input('category-selection-dropdown-tab2-b', 'value'),
        Input('state-selection-tab2', 'value'),
        Input('category-selection-type-tab2', 'value'), 
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_bar_charts_tab2(selected_indicators, cat_a_id, cat_b_id, selected_state, category_type, current_tab):
        if current_tab != 'tab-2':
            return []

        selected = [val for val in selected_indicators if val]
        if len(selected) != 4 or not cat_a_id or not cat_b_id or not category_type:
            return [html.Div("Please select 4 indicators, both categories, and a population group.")]

        charts = []

        # Assign 2 indicators to cat A and 2 to cat B
        category_map = [cat_a_id, cat_a_id, cat_b_id, cat_b_id]

        for i, indicator_id in enumerate(selected):
            cat_id = category_map[i]

            try:
                endpoint = "/getDistrictsByIndicators" if selected_state else "/getStatesByIndicators"
                response = requests.post(
                    BASE_URL + endpoint,
                    json={
                        "selected_indicators": [indicator_id],
                        "category_type": category_type,  # ST, Non-ST, or Total
                        "selected_state": selected_state
                    }
                )
                response.raise_for_status()
            except Exception as e:
                return [html.Div(f"API Error for indicator {indicator_id} (Category ID {cat_id}): {str(e)}")]

            data = response.json().get("indicator_data", [])
            if not data:
                charts.append(html.Div(f"No data returned for indicator ID {indicator_id}", style={"color": "orange"}))
                continue

            ind = data[0]
            raw = ind["data"]
            label_field = "district_name" if selected_state else "state_name"
            x_vals = [entry.get(category_type, None) for entry in raw]
            y_vals = [entry[label_field] for entry in raw]

            if not y_vals or not any(x_vals):
                charts.append(html.Div(f"No data to display for {ind['indicator_name']}", style={"color": "orange"}))
                continue

            chart = BarChartComponent(
                chart_id=f"bar-chart-tab2-{indicator_id}",
                x_data=x_vals,
                y_data=y_vals,
                category_=category_type,
                label_field=label_field,
                title=f"{ind['indicator_name']} ({category_type})"
            )

            charts.append(html.Div(chart, style={"marginBottom": "30px"}))

        return charts if charts else [html.Div("No bar charts generated.")]

    ### update Violin Chart Callback tab2 ###
    ### ********************************* ###
    @app.callback(
        Output("violin-chart-container-tab2", "children"),
        Input({'type': 'indicator-selection-tab2', 'index': ALL}, 'value'),
        Input('category-selection-dropdown-tab2-a', 'value'),
        Input('category-selection-dropdown-tab2-b', 'value'),
        Input('state-selection-tab2', 'value'),
        Input('category-selection-type-tab2', 'value'),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_violin_charts_tab2(selected_indicators, cat_a, cat_b, selected_state, category_type, active_tab):
        if active_tab != 'tab-2':
            return []

        if not category_type:
            category_type = "Total"

        if not cat_a or not cat_b:
            return [html.Div("Please select both categories.")]

        selected = [val for val in selected_indicators if val]
        if len(selected) != 4:
            return [html.Div("Please select exactly 4 indicators.")]

        indicators_cat_a = selected[:2]
        indicators_cat_b = selected[2:]

        all_charts = []

        for indicators, cat_label in zip([indicators_cat_a, indicators_cat_b], [cat_a, cat_b]):
            try:
                response = requests.post(
                    BASE_URL + "/getDistrictsByIndicators" if selected_state else BASE_URL + "/getStatesByIndicators",
                    json={
                        "selected_indicators": indicators,
                        "category_type": category_type,
                        "selected_state": selected_state
                    }
                )
                response.raise_for_status()
            except Exception as e:
                return [html.Div(f"API Error for {cat_label}: {str(e)}")]

            indicator_data = response.json().get("indicator_data", [])
            if not indicator_data:
                all_charts.append(html.Div(f"No data returned for category {cat_label}"))
                continue

            for item in indicator_data:
                indicator_id = item["indicator_id"]
                indicator_name = item["indicator_name"]
                raw_data = item["data"]

                label_field = "district_name" if selected_state else "state_name"
                x_vals = [entry[label_field] for entry in raw_data]
                y_vals = [entry.get(category_type, None) for entry in raw_data]

                if not x_vals or not any(y_vals):
                    all_charts.append(html.Div(f"No data to plot for {indicator_name}", style={"color": "orange"}))
                    continue

                chart = ViolinChartComponent(
                    chart_id=f"violin-chart-tab2-{indicator_id}",
                    x_data=x_vals,
                    y_data=y_vals,
                    title=f"{indicator_name} ({category_type})"
                )
                all_charts.append(html.Div(chart, style={"marginBottom": "30px"}))

        if not all_charts:
            return [html.Div("No charts generated.")]

        return html.Div(all_charts, style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'gap': '20px',
            'justifyContent': 'flex-start'
        })

    ### update Map Chart Callback tab2 ###
    ### ****************************** ###
    @app.callback(
        Output('map-container-tab2', 'children'),
        Input({'type': 'indicator-selection-tab2', 'index': ALL}, 'value'),
        Input('category-selection-type-tab2', 'value'),
        Input('state-selection-tab2', 'value'),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_map_tab1(selected_indicators, category_type, selected_state, current_tab):
        if current_tab != 'tab-2':
            return []

        selected = [val for val in selected_indicators if val]
        if not selected or not category_type:
            return []

        endpoint = "/getDistrictsByIndicators" if selected_state else "/getStatesByIndicators"

        try:
            response = requests.post(
                BASE_URL + endpoint,
                json={
                    "selected_indicators": selected,
                    "category_type": category_type,
                    "selected_state": selected_state
                }
            )
            response.raise_for_status()
            indicator_data = response.json().get("indicator_data", [])
        except Exception as e:
            return [html.Div(f"API Error: {str(e)}")]

        plots = []

        for i in range(4):  # fixed to 4 chart slots
            if i < len(indicator_data):
                indicator = indicator_data[i]
                raw = indicator["data"]
                indicator_name = indicator["indicator_name"]

                if selected_state:
                    filtered_geojson = filter_geojson_by_district_ids(
                        district_geojson,
                        [r["district_id"] for r in raw]
                    )
                    center = compute_geojson_center(filtered_geojson)
                    records = [
                        {
                            "district_id": r["district_id"],
                            "district_name": r["district_name"],
                            "value": r.get(category_type)
                        } for r in raw if r.get(category_type) is not None
                    ]
                    chart = MapChartComponent(
                        chart_id=f"map-chart-{i+1}",
                        data=records,
                        geojson=filtered_geojson,
                        location_key="district_name",
                        feature_id_key="properties.district_name",
                        value_key="value",
                        label_key="district_name",
                        title=f"{indicator_name} (District View)",
                        center=center
                    )
                else:
                    records = [
                        {
                            "state_acronym": r["state_acronym"],
                            "state_name": r["state_name"],
                            "value": r.get(category_type)
                        } for r in raw if r.get(category_type) is not None
                    ]
                    chart = MapChartComponent(
                        chart_id=f"map-chart-{i+1}",
                        data=records,
                        geojson=state_geojson,
                        location_key="state_acronym",
                        feature_id_key="properties.state_acronym",
                        value_key="value",
                        label_key="state_name",
                        title=f"{indicator_name} (State View)",
                        center={"lat": 22, "lon": 80}
                    )
            else:
                chart = MapChartComponent(
                    chart_id=f"map-chart-{i+1}",
                    data=[],
                    geojson={"type": "FeatureCollection", "features": []},
                    location_key="dummy",
                    feature_id_key="properties.dummy",
                    value_key="value",
                    label_key="dummy",
                    title="No Data"
                )

            plots.append(html.Div(chart, style={"width": "48%", "minWidth": "400px", "paddingLeft": "10px", "paddingRight": "10px"}))

        return plots


    ### update Bubble Chart Callback ###
    ### **************************** ###
    @app.callback(
        Output("bubble-chart-container-tab2", "children"),
        Input({'type': 'indicator-selection-tab2', 'index': 0}, 'value'),
        Input({'type': 'indicator-selection-tab2', 'index': 1}, 'value'),
        Input({'type': 'indicator-selection-tab2', 'index': 2}, 'value'),
        Input({'type': 'indicator-selection-tab2', 'index': 3}, 'value'),
        Input("category-selection-type-tab2", "value"),
        Input("state-selection-tab2", "value"),
        Input("main-tabs", "data"),
        prevent_initial_call=True
    )
    def update_bubble_chart(ind_x, ind_y, ind_size, ind_color, hh_type, selected_state, current_tab):
        if current_tab != 'tab-2':
            return []

        indicators = [ind_x, ind_y, ind_size, ind_color]
        if not all(indicators) or not hh_type:
            return [html.Div("All 4 indicators and category type must be selected.")]

        endpoint = f"{BASE_URL}/getDistrictsByIndicators" if selected_state else f"{BASE_URL}/getStatesByIndicators"
        payload = {
            "selected_indicators": indicators,
            "category_type": hh_type,
            "selected_state": selected_state
        }

        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            response_json = response.json()
        except Exception as e:
            return [html.Div(f"API error: {str(e)}")]

        indicator_data = response_json.get("indicator_data", [])
        if not indicator_data:
            return [html.Div("No data returned from the server.")]

        indicator_id_to_name = {
            entry["indicator_id"]: entry["indicator_name"]
            for entry in indicator_data
        }

        label_key = "district_name" if selected_state else "state_name"

        merged = {}
        for indicator in indicator_data:
            name = indicator["indicator_name"]
            for row in indicator["data"]:
                key = row[label_key]
                if key not in merged:
                    merged[key] = {label_key: key}
                merged[key][name] = row.get(hh_type)

        cleaned = [
            row for row in merged.values()
            if all(indicator_id_to_name.get(i) in row and row[indicator_id_to_name.get(i)] is not None for i in indicators)
        ]

        if not cleaned:
            return [html.Div("No usable data found for the selected indicators.")]

        x_key = indicator_id_to_name[ind_x]
        y_key = indicator_id_to_name[ind_y]
        size_key = indicator_id_to_name[ind_size]
        color_key = indicator_id_to_name[ind_color]

        chart = render_bubble_with_legend(
            chart_id="bubble-chart",
            data=cleaned,
            x_key=x_key,
            y_key=y_key,
            size_key=size_key,
            color_key=color_key,
            label_key=label_key
        )

        return [chart]
        

    ########### AI INSIGHTS TAB 2 ########
    ######################################
    @app.callback(
        Output("ai-insights-output-tab2", "children"),
        Input({'type': 'indicator-selection-tab2', 'index': ALL}, 'value'),
        Input('state-selection-tab2', 'value'),
        Input('category-selection-type-tab2', 'value'),
        Input("main-tabs", "data"),
        State('category-selection-dropdown-tab2-a', 'value'),
        State('category-selection-dropdown-tab2-b', 'value'),
        prevent_initial_call=True
    )
    def update_ai_insights_tab2(selected_indicators, selected_state, category_type, active_tab, cat_a, cat_b):
        if active_tab != 'tab-2':
            return []

        if not category_type:
            category_type = "Total"

        selected = [val for val in selected_indicators if val]

        # Split into A & B groups
        indicators_cat_a = selected[:2]
        indicators_cat_b = selected[2:]

        # Ensure at least 1 indicator in each group
        if len(indicators_cat_a) < 1 or len(indicators_cat_b) < 1 or not cat_a or not cat_b:
            return []


        try:
            # Split into 2 groups (A & B)
            indicators_cat_a = selected[:2]
            indicators_cat_b = selected[2:]
            full_data = []

            for indicators in [indicators_cat_a, indicators_cat_b]:
                endpoint = "/getDistrictsByIndicators" if selected_state else "/getStatesByIndicators"
                payload = {
                    "selected_indicators": indicators,
                    "category_type": category_type,
                    "selected_state": selected_state
                }
                response = requests.post(BASE_URL + endpoint, json=payload)
                response.raise_for_status()
                full_data.extend(response.json().get("indicator_data", []))

            # --- Fetch stats + correlation tables ---
            stats_payload = {
                "selected_indicators": selected,
                "category_type": category_type,
                "selected_state": selected_state
            }
            stats_response = requests.post(BASE_URL + "/indicator-stats", json=stats_payload)
            correlation_response = requests.post(BASE_URL + "/indicator-correlation", json=stats_payload)

            stats_response.raise_for_status()
            correlation_response.raise_for_status()

            stats_data = stats_response.json().get("stats", [])
            correlation_data = correlation_response.json().get("correlations", [])

            # Convert stats table
            if stats_data:
                table_header = [html.Th(col) for col in stats_data[0].keys()]
                table_rows = [
                    html.Tr([html.Td(str(val)) for val in row.values()])
                    for row in stats_data
                ]
                stats_table = html.Div(
                    html.Table(
                        [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)],
                        className="stats-table"
                    ),
                    className="stats-table-container"
                )
            else:
                stats_table = html.P("No statistics available.", className="no-stats-message")

            # Convert correlation table
            if correlation_data:
                table_header = [html.Th(col) for col in correlation_data[0].keys()]
                table_rows = [
                    html.Tr([html.Td(str(val)) for val in row.values()])
                    for row in correlation_data
                ]
                correlation_table = html.Div(
                    html.Table(
                        [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)],
                        className="stats-table"
                    ),
                    className="stats-table-container"
                )
            else:
                correlation_table = html.P("No correlations available.", className="no-stats-message")

            # --- AI Summary ---
            summary_payload = {
                "selected_indicators": selected,
                "category_type": category_type,
                "selected_state": selected_state
            }
            try:
                summary_response = requests.post(BASE_URL + "/indicator-summary", json=summary_payload)
                summary_response.raise_for_status()
                summary_text = summary_response.json().get("summary", "No summary generated.")
            except requests.RequestException as e:
                summary_text = f"⚠️ Error generating summary: {str(e)}"

            # --- Final Layout ---
            return [
                html.Div([
                    html.Div([
                        html.H4("Indicator Description", className="stats-header"),
                    ], className="section-container"),

                    # Stats Table
                    html.Div([stats_table], className="stats-container"),

                    html.Div([
                        html.H4("Indicator Correlation", className="stats-header"),
                    ], className="section-container"),

                    html.Div([correlation_table], className="stats-container"),

                    html.Div([
                        html.H4("Analytical Summary", className="section-header"),
                        html.Div(
                            summary_text,
                            className="summary-box",
                            style={
                                "border": "1px solid #ccc",
                                "padding": "12px",
                                "borderRadius": "8px",
                                "backgroundColor": "#f9f9f9",
                                "whiteSpace": "pre-wrap"
                            }
                        )
                    ], className="summary-container"),
                ], className="insights-container")
            ]

        except requests.RequestException as e:
            return [
                html.Div([
                    html.H4("⚠️ Connection Error", className="error-title"),
                    html.P(f"Unable to fetch AI insights: {str(e)}", className="error-message"),
                    html.Button("🔄 Retry", id="retry-insights-btn-tab2", className="retry-button")
                ], className="error-container")
            ]
        except Exception as e:
            return [
                html.Div([
                    html.H4("❌ Error", className="error-title"),
                    html.P(f"An unexpected error occurred: {str(e)}", className="error-message")
                ], className="error-container")
            ]

    return app