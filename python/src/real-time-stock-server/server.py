import asyncio
import random
import websockets
import json
import argparse
from flask import Flask
from threading import Thread

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Run a real-time stock simulation server.')
parser.add_argument('--flask_port', type=int, default=5000,
                    help='Port for the Flask server (default: 5000)')
parser.add_argument('--websocket_port', type=int, default=6789,
                    help='Port for the WebSocket server (default: 6789)')
parser.add_argument('--host', type=str, default='localhost',
                    help='Host for the WebSocket server (default: localhost)')
args = parser.parse_args()

app = Flask(__name__)

# Flask API for basic HTTP requests


@app.route('/')
def home():
    return "WebSocket Real-Time Stock Simulation Server is running!"

# Function to simulate stock prices


async def stock_price_simulator(websocket, path):
    stock_symbol = "AAPL"
    current_price = 150.00  # Starting price
    while True:
        # Simulate price change
        price_change = random.uniform(-1, 1)  # Random change between -1 and 1
        current_price += price_change
        current_price = round(current_price, 2)

        # Create a stock update message
        message = {
            "stock_symbol": stock_symbol,
            "real_time_price": current_price,
            "volume": random.randint(1000, 10000),
            "price_change": price_change,
        }

        # Send message to the client
        await websocket.send(json.dumps(message))

        # Wait for a short interval before sending the next update
        await asyncio.sleep(0.1)  # 1-second interval for real-time updates

# Start Flask in a separate thread


def start_flask():
    app.run(port=args.flask_port)

# Start the WebSocket server


async def start_websocket():
    async with websockets.serve(stock_price_simulator, args.host, args.websocket_port):
        await asyncio.Future()  # Run forever

# Run Flask in a separate thread so that it can run alongside the WebSocket server
flask_thread = Thread(target=start_flask)
flask_thread.start()

# Run WebSocket server using asyncio
asyncio.run(start_websocket())
