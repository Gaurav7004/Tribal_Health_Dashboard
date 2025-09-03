from dash import dcc, html
import plotly.graph_objects as go
from src.data.scale_helper import get_scale_range

# Create Bubble Plot
def BubbleChartComponent(chart_id, data, x_key, y_key, size_key, color_key, label_key, title=None,
                         x_id=None, y_id=None, size_id=None, color_id=None):

    if not data or not all(k in data[0] for k in [x_key, y_key, size_key, color_key, label_key]):
        fig = go.Figure()
        fig.update_layout(title="Invalid or empty data")
    else:
        # Extract values
        x_vals = [d[x_key] for d in data]
        y_vals = [d[y_key] for d in data]
        sizes = [d[size_key] for d in data]
        colors = [d[color_key] for d in data]
        labels = [d[label_key] for d in data]

        # Get fixed ranges
        x_range = get_scale_range(x_id)
        y_range = get_scale_range(y_id)
        size_range = get_scale_range(size_id)
        color_range = get_scale_range(color_id)

        # Fallbacks if size_range not available
        max_size = max(sizes) if sizes else 1
        sizeref = 2. * max_size / (100. ** 2)

        if size_range:
            sizeref = 2. * size_range[1] / (100. ** 2)

        fig = go.Figure(
            data=go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=colors,
                    colorscale=[
                        [0.0, "#b6d6f4"],
                        [0.5, "#a8d1f8"],
                        [1.0, "#084594"]
                    ],
                    colorbar=dict(title=""),
                    cmin=color_range[0] if color_range else None,
                    cmax=color_range[1] if color_range else None,
                    showscale=True,
                    sizemode='area',
                    sizeref=sizeref,
                    sizemin=4,
                    line=dict(width=0.5, color='white')
                ),
                text=labels,
                hovertemplate=(
                    f"<b>%{{text}}</b><br>"
                    f"{x_key}: %{{x}}<br>"
                    f"{y_key}: %{{y}}<br>"
                    f"{size_key}: %{{marker.size}}<br>"
                    f"{color_key}: %{{marker.color:.2f}}<extra></extra>"
                )
            )
        )

        fig.update_layout(
            title=dict(
                text=title or "",
                x=0.5,
                xanchor="center",
                yanchor="top",
                pad=dict(t=10, b=10)
            ),
            height=600,
            margin=dict(t=60, b=40, l=50, r=30),
            showlegend=False,
            plot_bgcolor='white',
            xaxis=dict(title=None, range=x_range),
            yaxis=dict(title=None, range=y_range)
        )

    return dcc.Graph(
        id=chart_id,
        figure=fig,
        config={'displayModeBar': False}
    )


# Legend Renderer
def render_bubble_with_legend(chart_id, data, x_key, y_key, size_key, color_key, label_key, title=None,
                               x_id=None, y_id=None, size_id=None, color_id=None):
    chart = BubbleChartComponent(
        chart_id=chart_id,
        data=data,
        x_key=x_key,
        y_key=y_key,
        size_key=size_key,
        color_key=color_key,
        label_key=label_key,
        title=title,
        x_id=x_id,
        y_id=y_id,
        size_id=size_id,
        color_id=color_id
    )

    legend = html.Div([
        html.H6("Legend"),
        html.P(f"X-Axis: {x_key}"),
        html.P(f"Y-Axis: {y_key}"),
        html.P(f"Bubble Size: {size_key}"),
        html.P(f"Bubble Color: {color_key}"),
    ], style={
        "padding": "10px",
        "border": "1px solid #ccc",
        "borderRadius": "5px",
        "fontSize": "14px"
    })

    return html.Div([
        html.Div(chart, style={"width": "75%", "display": "inline-block", "verticalAlign": "top"}),
        html.Div(legend, style={"width": "23%", "display": "inline-block", "marginLeft": "2%", "verticalAlign": "top"})
    ])
