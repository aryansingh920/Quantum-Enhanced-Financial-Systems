python3 -m venv python/venv-quant
source ./python/venv-quant/bin/activate


pip3 install -r python/requirements.txt


python3 python/src/real-time-stock-server/server.py --flask_port 8000 --websocket_port 9000 --host 0.0.0.0


python3 python/src/historical_stock/historical_data_generator.py --symbol AAPL --timeframe 1year --output python/src/data/aapl_1yrs.json


python python/src/view_graph/updated_realtime_stock_plot.py --view all --websocket_port 9000 --json_file python/src/data/aapl_1yrs.json

python python/src/view_graph/updated_realtime_stock_plot.py --websocket_port 9000 --instant
