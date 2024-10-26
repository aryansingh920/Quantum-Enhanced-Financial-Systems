import asyncio
import websockets
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from threading import Thread
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor

# Parameters for connecting to the WebSocket server
WEBSOCKET_URI = "ws://localhost:6789"

# Lists to store real-time data for plotting
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
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    # Adding a cursor with information on hover
    cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

    # Annotate details when hovering over a point
    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        x, y = times[ind[0]], prices[ind[0]]
        annot.xy = (mdates.date2num(x), y)
        text = f"Time: {x.strftime('%H:%M:%S')}\nPrice: ${y}\nVolume: {
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
ani = animation.FuncAnimation(
    fig, update_plot, interval=1000, cache_frame_data=False)

# Start the asyncio event loop in a separate thread to fetch data
data_thread = Thread(target=lambda: asyncio.run(fetch_stock_data()))
data_thread.start()

# Show the real-time plot
plt.show()
