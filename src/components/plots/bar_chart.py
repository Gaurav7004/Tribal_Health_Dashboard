from dash import dcc
import plotly.graph_objects as go
import textwrap
from src.data.scale_helper import get_scale_range 

def BarChartComponent(chart_id, x_data, y_data, category_, label_field,
                      title="Bar Chart", is_empty=False, indicator_id=None): 

    if is_empty or not x_data or not y_data or not any(x_data):
        return dcc.Graph(
            id=chart_id,
            figure=go.Figure(
                layout=go.Layout(
                    title="No Data Available",
                    template="plotly_white",
                    height=400,
                    annotations=[
                        dict(
                            text="No data available",
                            xref="paper", yref="paper",
                            x=0.5, y=0.5,
                            xanchor='center', yanchor='middle',
                            showarrow=False,
                            font=dict(size=16, color="gray")
                        )
                    ]
                )
            ),
            config={'displayModeBar': False}
        )

    # Get fixed scale if indicator_id is provided
    range_values = get_scale_range(indicator_id) if indicator_id else None

    return dcc.Graph(
        id=chart_id,
        figure=go.Figure(
            data=[
                go.Bar(
                    x=x_data,
                    y=y_data,
                    orientation='h',
                    marker_color='#084594'
                )
            ],
            layout=go.Layout(
                title=dict(
                    text="<br>".join(textwrap.wrap(title, width=50)),
                    x=0.5,
                    xanchor="center",
                    font=dict(size=14),
                    y=0.95
                ),
                xaxis=dict(title=category_, range=range_values),
                yaxis=dict(title=label_field),
                template="plotly_white",
                height=500,
                margin=dict(r=0, t=80, l=0, b=0),
            )
        ),
        config={'displayModeBar': False}
    )
