import plotly.graph_objs as go
import plotly.io as pio


def plot_hourly_requests(data):
    hours = list(data.keys())
    counts = list(data.values())
    fig = go.Figure([go.Bar(x=hours, y=counts)])
    fig.update_layout(
        title="⌛ Hourly Request Volume", xaxis_title="Hour", yaxis_title="Requests"
    )
    return pio.to_html(fig, full_html=False)


def plot_daily_requests(data):
    # Sort the data by date
    sorted_items = sorted(data.items())
    days = [day for day, _ in sorted_items]
    counts = [count for _, count in sorted_items]

    fig = go.Figure(
        [go.Scatter(x=days, y=counts, mode="lines+markers", line=dict(color="blue"))]
    )
    fig.update_layout(
        title="📅 Daily Request Volume",
        xaxis_title="Date",
        yaxis_title="Number of Requests",
        xaxis_tickangle=-45,
        template="plotly_white",
        height=400,
    )

    return pio.to_html(fig, full_html=False)


def plot_status_codes(data):
    labels = list(data.keys())
    values = list(data.values())
    fig = go.Figure([go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title="📶 Status Code Distribution")
    return pio.to_html(fig, full_html=False)
