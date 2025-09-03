import plotly.graph_objs as go
from dash import dcc, html
from typing import List
import textwrap
from src.data.scale_helper import get_scale_range

def ViolinChartComponent(chart_id, x_data, y_data, title="Violin Chart", 
                         indicator_type="Neutral", show_points=True, 
                         color_scheme="default", indicator_id=None):
    
    if not x_data or not y_data or len(x_data) != len(y_data):
        return _empty_graph(chart_id, "No data to display")

    valid_x = []
    valid_y = []

    for x, y in zip(x_data, y_data):
        try:
            num = float(y)
            valid_x.append(x)
            valid_y.append(num)
        except (ValueError, TypeError):
            continue

    if not valid_y:
        return _empty_graph(chart_id, "No valid numeric data")

    def get_point_colors(values, indicator_type):
        colors = []
        for val in values:
            if indicator_type == 'Positive':
                if val >= 75:
                    colors.append('#28a745')
                elif val >= 50:
                    colors.append('#fd7e14')
                else:
                    colors.append('#dc3545')
            elif indicator_type == 'Negative':
                if val <= 25:
                    colors.append('#28a745')
                elif val <= 50:
                    colors.append('#fd7e14')
                else:
                    colors.append('#dc3545')
            else:
                colors.append('#6c757d')
        return colors

    violin_trace = go.Violin(
        x=[''] * len(valid_y),
        y=valid_y,
        box_visible=True,
        meanline_visible=True,
        line_color='#003a5d',
        fillcolor='rgba(0, 102, 204, 0.3)',
        opacity=0.7,
        name='Distribution',
        hoverinfo='y',
        points=False
    )

    traces = [violin_trace]

    if show_points:
        point_colors = get_point_colors(valid_y, indicator_type)
        scatter_trace = go.Scatter(
            x=[''] * len(valid_y),
            y=valid_y,
            mode='markers',
            marker=dict(
                color=point_colors,
                size=8,
                line=dict(width=1, color='white'),
                opacity=0.8
            ),
            customdata=valid_x,
            hovertemplate="<b>%{customdata}</b><br>Value: %{y:.2f}<extra></extra>",
            name='Data Points',
            showlegend=False
        )
        traces.append(scatter_trace)

    # Get fixed y-axis scale
    y_range = get_scale_range(indicator_id) if indicator_id else None

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text="<br>".join(textwrap.wrap(title, width=50)),
            x=0.5,
            xanchor='center',
            font=dict(size=16, color='#2c3e50'),
            y=0.95
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Value",
            range=y_range,
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            title_font=dict(size=12, color='#2c3e50')
        ),
        template="plotly_white",
        height=450,
        margin=dict(t=60, l=70, r=30, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    return dcc.Graph(
        id=chart_id,
        figure=fig,
        config={'displayModeBar': False}
    )


def _empty_graph(chart_id, message):
    return dcc.Graph(
        id=chart_id,
        figure=go.Figure(
            layout=go.Layout(
                title="No Data Available",
                template="plotly_white",
                height=400,
                annotations=[
                    dict(
                        text=message,
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
