from dash import dcc
import plotly.graph_objects as go
import textwrap

def BarChartComponent(chart_id, indicators, y_labels, category_, title="Bullet Bars"):
    """
    Render bullet bars for 1–4 indicators on one chart.
    - First indicator: broad background bar
    - Subsequent indicators: narrower overlay bars
    """
    fig = go.Figure()

    if not indicators:
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
                            xanchor="center", yanchor="middle",
                            showarrow=False,
                            font=dict(size=16, color="gray")
                        )
                    ]
                )
            ),
            config={"displayModeBar": False}
        )

    for i, ind in enumerate(indicators):
        if i == 0:
            # Background bar (broad)
            fig.add_trace(
                go.Bar(
                    x=ind["values"],
                    y=y_labels,
                    orientation="h",
                    name=ind["name"],
                    marker_color=ind.get("color", "#a6bddb"),
                    opacity=0.6,
                    width=0.9   # broader
                )
            )
        else:
            # Overlay bars (narrower)
            fig.add_trace(
                go.Bar(
                    x=ind["values"],
                    y=y_labels,
                    orientation="h",
                    name=ind["name"],
                    marker_color=ind.get("color", "#045a8d"),
                    opacity=0.8,
                    width=0.4   # narrower
                )
            )

    fig.update_layout(
        barmode="group",
        bargap=0.3,
        bargroupgap=0.1,
        title=dict(
            text="<br>".join(textwrap.wrap(title, width=100)),
            x=0.5,
            xanchor="center",
            font=dict(size=14),
            y=0.95
        ),
        xaxis=dict(title=category_),
        yaxis=dict(title=""),
        template="plotly_white",
        height=800,
        margin=dict(r=40, t=80, l=60, b=70),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )

    return dcc.Graph(id=chart_id, figure=fig, config={"displayModeBar": False})
