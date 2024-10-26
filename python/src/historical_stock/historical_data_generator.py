import random
import json
from datetime import datetime, timedelta
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Generate historical stock data and store it in a JSON file.')
parser.add_argument('--symbol', type=str, default='AAPL',
                    help='Stock symbol (default: AAPL)')
parser.add_argument('--timeframe', type=str, default='1year', choices=[
                    '1day', '1week', '1month', '6months', '1year', '5years', 'alltime'], help='Timeframe for historical data (default: 1year)')
parser.add_argument('--output', type=str, default='historical_data.json',
                    help='Output JSON file (default: historical_data.json)')
args = parser.parse_args()

# Generate the date range based on the selected timeframe


def get_date_range(timeframe):
    today = datetime.now()
    if timeframe == '1day':
        return [today - timedelta(days=1)]
    elif timeframe == '1week':
        return [today - timedelta(days=i) for i in range(7)]
    elif timeframe == '1month':
        return [today - timedelta(days=i) for i in range(30)]
    elif timeframe == '6months':
        return [today - timedelta(weeks=i) for i in range(26)]
    elif timeframe == '1year':
        return [today - timedelta(weeks=i) for i in range(52)]
    elif timeframe == '5years':
        return [today - timedelta(weeks=i) for i in range(52 * 5)]
    elif timeframe == 'alltime':
        # Example for a decade
        return [today - timedelta(weeks=i) for i in range(52 * 10)]
    else:
        return []

# Generate stock price data for each date


def generate_historical_data(symbol, dates):
    data = []
    current_price = 150.00  # Starting price
    for date in dates:
        open_price = round(current_price + random.uniform(-5, 5), 2)
        high_price = round(open_price + random.uniform(0, 10), 2)
        low_price = round(open_price - random.uniform(0, 10), 2)
        close_price = round(low_price + random.uniform(0, 5), 2)
        volume = random.randint(1000, 10000)

        data_point = {
            'date': date.strftime('%Y-%m-%d'),
            'symbol': symbol,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'close_price': close_price,
            'volume': volume
        }
        data.append(data_point)
        current_price = close_price  # Next day's price starts from previous close

    return data


# Main function
if __name__ == "__main__":
    dates = get_date_range(args.timeframe)
    historical_data = generate_historical_data(args.symbol, dates)

    # Save the generated data to a JSON file
    with open(args.output, 'w') as f:
        json.dump(historical_data, f, indent=4)

    print(f"Historical data for {args.symbol} saved to {args.output}")
