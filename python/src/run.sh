python3 -m venv real-time-server
source ./real-time-server/bin/activate

python3 src/real-time-stock-server/server.py --flask_port 8000 --websocket_port 9000 --host 0.0.0.0

