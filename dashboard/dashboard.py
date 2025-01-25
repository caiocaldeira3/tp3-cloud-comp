import redis
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import json

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Initialize Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Metrics Monitor", style={"textAlign": "center"}),
    dash_table.DataTable(
        id='metrics-table',
        columns=[
            {"name": "Timestamp", "id": "timestamp"},
            {"name": "Metric", "id": "metric"},
            {"name": "Value", "id": "value"}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
    ),
    dcc.Interval(
        id='interval-component',
        interval=5000,  # 5 seconds in milliseconds
        n_intervals=0
    )
])

# Callback to update the table
@app.callback(
    Output('metrics-table', 'data'),
    [Input('interval-component', 'n_intervals')]
)
def update_table(_):
    metrics = json.load(open("metrics.json"))
    if metrics:
        return [
            {"timestamp": metrics["timestamp"], "metric": key, "value": round(value, 2)}
            for key, value in metrics.items() if key != "timestamp"
        ]

    return []

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)
