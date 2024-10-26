import asyncio
import websockets
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from threading import Thread
import argparse
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor
import pandas as pd

# Parse command line arguments for historical data view
parser = argparse.ArgumentParser(
    description='Run a real-time stock simulation server with historical data visualization.')
parser.add_argument('--view', type=str, default='1D', choices=[
                    '1D', '1W', '1M', '6M', '1Y', '5Y', 'all'], help='View mode for historical data (default: 1D)')
parser.add_argument('--websocket_port', type=int, default=6789,
                    help='Port for the WebSocket server (default: 6789)')
parser.add_argument('--json_file', type=str, default='historical_data.json',
                    help='Path to the historical data JSON file (default: historical_data.json)')
parser.add_argument('--instant', action='store_true',
                    help='Show updates instantaneously without delay')
args = parser.parse_args()

# Parameters for connecting to the WebSocket server
WEBSOCKET_URI = f"ws://localhost:{args.websocket_port}"

# If not in instant mode, load historical data
if not args.instant:
    # Load historical data from JSON file
    with open(args.json_file, 'r') as f:
        historical_data = json.load(f)

    # Convert historical data to a DataFrame
    historical_df = pd.DataFrame(historical_data)
    historical_df['date'] = pd.to_datetime(historical_df['date'])

    # Determine the date range for the chosen view
    def filter_historical_data(view):
        end_date = datetime.now()
        if view == '1D':
            start_date = end_date - pd.Timedelta(days=1)
        elif view == '1W':
            start_date = end_date - pd.Timedelta(weeks=1)
        elif view == '1M':
            start_date = end_date - pd.Timedelta(weeks=4)
        elif view == '6M':
            start_date = end_date - pd.Timedelta(weeks=26)
        elif view == '1Y':
            start_date = end_date - pd.Timedelta(weeks=52)
        elif view == '5Y':
            start_date = end_date - pd.Timedelta(weeks=52*5)
        else:
            start_date = historical_df['date'].min()
        return historical_df[(historical_df['date'] >= start_date) & (historical_df['date'] <= end_date)]

    # Filter the data for the selected view
    filtered_df = filter_historical_data(args.view)

    # Lists to store real-time data for plotting
    times = filtered_df['date'].tolist()
    prices = filtered_df['close_price'].tolist()
    volumes = filtered_df['volume'].tolist()
    price_changes = [0] * len(prices)  # Initialize with 0 for historical data
else:
    # Initialize empty lists for instant mode
    times = []
    prices = []
    volumes = []
    price_changes = []

# Function to connect to the WebSocket and receive data


async def fetch_stock_data():
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            # Add current time and price to the lists
            times.append(datetime.now())
            prices.append(data["real_time_price"])
            volumes.append(data["volume"])
            price_changes.append(data["price_change"])

# Function to update the plot in real-time


def update_plot(frame):
    ax.clear()
    ax.plot(times, prices, label="Real-Time Price", color='b')
    ax.set_title("Real-Time Stock Price of AAPL")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price ($)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()

    # Formatting the x-axis with time
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    # Adding a cursor with information on hover
    cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

    # Annotate details when hovering over a point
    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        x, y = times[ind[0]], prices[ind[0]]
        annot.xy = (mdates.date2num(x), y)
        text = f"Time: {x.strftime('%Y-%m-%d %H:%M:%S')}\nPrice: ${y}\nVolume: {
            volumes[ind[0]]}\nPrice Change: {price_changes[ind[0]]}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def on_hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind["ind"])
                annot.set_visible(True)
                fig.canvas.draw_idle()
            elif vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

    # Plot line for real-time price
    line, = ax.plot(times, prices, label="Real-Time Price", color='b')
    fig.canvas.mpl_connect("motion_notify_event", on_hover)


# Set up the figure and axis for the plot
fig, ax = plt.subplots()
interval = 1000  # Keep the default interval for real-time updates
ani = animation.FuncAnimation(
    fig, update_plot, interval=interval, cache_frame_data=False)

# Start the asyncio event loop in a separate thread to fetch data
data_thread = Thread(target=lambda: asyncio.run(fetch_stock_data()))
data_thread.start()

# Show the real-time plot
plt.show()
