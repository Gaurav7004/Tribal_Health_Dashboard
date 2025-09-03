import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.components.layout import create_layout

if __name__ == "__main__":
    dash_app = create_layout()  
    dash_app.run(debug=True, port=8050)
