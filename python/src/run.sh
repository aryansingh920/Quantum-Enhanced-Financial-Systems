python3.10 -m venv .venv
source .venv/bin/activate

pip3.10 install --upgrade pip setuptools


pip3.10 install -r python/requirements.txt


python3.10 python/src/real-time-stock-server/server.py --flask_port 8000 --websocket_port 9000 --host 0.0.0.0


python3.10 python/src/historical_stock/historical_data_generator.py --symbol AAPL --timeframe 1year --output python/src/data/aapl_1yrs.json


python3.10 python/src/view_graph/updated_realtime_stock_plot.py --view all --websocket_port 9000 --json_file python/src/data/aapl_1yrs.json

python3.10 python/src/view_graph/updated_realtime_stock_plot.py --websocket_port 9000 --instant
