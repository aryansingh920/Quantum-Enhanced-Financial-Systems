import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import threading
import queue
import time
import random

# Global queue for price updates
price_queue = queue.Queue()


class RandomShockGenerator:
    def __init__(self, base_price, frequency=0.1, magnitude_range=(0.001, 0.01)):
        """
        frequency: probability of shock occurring (0-1)
        magnitude_range: (min_percent, max_percent) of base price for shock size
        """
        self.base_price = base_price
        self.frequency = frequency
        self.magnitude_range = magnitude_range

    def generate_shock(self):
        if random.random() < self.frequency:
            magnitude = random.uniform(*self.magnitude_range) * self.base_price
            return random.choice([-1, 1]) * magnitude
        return 0


class HFTSimulator(threading.Thread):
    def __init__(self, base_price, volatility_factor=0.0001, mean_reversion=0.1, random_enabled=False):
        super().__init__()
        self.base_price = base_price
        self.current_price = base_price
        self.volatility = base_price * volatility_factor
        self.mean_reversion = mean_reversion
        self.current_volatility = self.volatility
        self.running = True
        self.random_enabled = random_enabled
        self.shock_generator = RandomShockGenerator(base_price)

    def toggle_random(self):
        self.random_enabled = not self.random_enabled
        return self.random_enabled

    def run(self):
        while self.running:
            # Update volatility (volatility clustering)
            self.current_volatility = max(
                self.volatility,
                self.current_volatility * np.random.normal(1, 0.1)
            )

            # Generate price change with mean reversion
            deviation = self.current_price - self.base_price
            mean_reversion_effect = -self.mean_reversion * deviation
            random_change = np.random.normal(0, self.current_volatility)
            price_change = mean_reversion_effect + random_change

            # Add random shock if enabled
            if self.random_enabled:
                shock = self.shock_generator.generate_shock()
                price_change += shock

            # Update current price
            self.current_price += price_change

            # Put the new price and timestamp in the queue
            price_queue.put({
                'timestamp': datetime.now(),
                'price': self.current_price,
                'had_shock': bool(shock) if self.random_enabled else False
            })

            # Simulate HFT speed
            time.sleep(0.02)  # 50 trades per second

    def stop(self):
        self.running = False


# Initialize Dash app
app = dash.Dash(__name__)

# Store for historical data
historical_data = pd.DataFrame(columns=['timestamp', 'price', 'had_shock'])

# Global simulator reference
simulator = None

# Layout
app.layout = html.Div([
    html.H1('Live HFT Price Simulation with Random Shocks'),
    html.Button('Toggle Random Mode', id='toggle-random', n_clicks=0),
    html.Div(id='random-status'),
    dcc.Graph(id='live-candlestick'),
    dcc.Interval(
        id='interval-component',
        interval=100,  # Update every 100ms
        n_intervals=0
    ),
    html.Div(id='stats-display')
])


@app.callback(
    Output('random-status', 'children'),
    Input('toggle-random', 'n_clicks')
)
def toggle_random_mode(n_clicks):
    if n_clicks == 0 or simulator is None:
        return "Random Mode: OFF"

    is_enabled = simulator.toggle_random()
    return f"Random Mode: {'ON' if is_enabled else 'OFF'}"


@app.callback(
    [Output('live-candlestick', 'figure'),
     Output('stats-display', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    global historical_data

    # Collect all available updates from the queue
    while not price_queue.empty():
        try:
            data = price_queue.get_nowait()
            historical_data = pd.concat([
                historical_data,
                pd.DataFrame([data])
            ], ignore_index=True)
        except queue.Empty:
            break

    if len(historical_data) == 0:
        return go.Figure(), "Waiting for data..."

    # Keep only last 5 minutes of data
    cutoff_time = datetime.now() - timedelta(minutes=5)
    historical_data = historical_data[historical_data['timestamp'] > cutoff_time]

    # Create OHLC data
    df_resampled = historical_data.set_index('timestamp')
    ohlc = df_resampled['price'].resample('1s').ohlc().dropna()

    # Create candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=ohlc.index,
            open=ohlc['open'],
            high=ohlc['high'],
            low=ohlc['low'],
            close=ohlc['close'],
            name='Price'
        )
    ])

    # Add markers for random shocks if they exist
    shock_points = historical_data[historical_data['had_shock']]
    if not shock_points.empty:
        fig.add_trace(go.Scatter(
            x=shock_points['timestamp'],
            y=shock_points['price'],
            mode='markers',
            marker=dict(
                symbol='star',
                size=12,
                color='red'
            ),
            name='Random Shock'
        ))

    fig.update_layout(
        title='Live HFT Price Movement',
        yaxis_title='Price ($)',
        xaxis_title='Time',
        template='plotly_dark',
        height=600
    )

    # Calculate statistics
    stats = {
        'Current Price': historical_data['price'].iloc[-1],
        'Max Price': historical_data['price'].max(),
        'Min Price': historical_data['price'].min(),
        'Price Range': historical_data['price'].max() - historical_data['price'].min(),
        'Total Trades': len(historical_data),
        'Random Shocks': len(shock_points) if 'had_shock' in historical_data.columns else 0
    }

    stats_display = html.Div([
        html.H3('Live Statistics'),
        *[html.P(f'{key}: ${value:.2f}' if 'Price' in key else f'{key}: {int(value)}')
          for key, value in stats.items()]
    ])

    return fig, stats_display


def run_simulation(base_price):
    global simulator
    # Start the HFT simulator in a separate thread
    simulator = HFTSimulator(base_price)
    simulator.start()

    # Run the Dash app
    app.run_server(debug=False)

    # Cleanup when the app is closed
    simulator.stop()
    simulator.join()


if __name__ == '__main__':
    BASE_PRICE = 100.0  # Starting price in dollars
    run_simulation(BASE_PRICE)
