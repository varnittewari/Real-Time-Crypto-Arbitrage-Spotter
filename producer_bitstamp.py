import websocket
import json
import time
from kafka import KafkaProducer

# Kafka Producer setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

KAFKA_TOPIC = 'market-data'

def on_message(ws, message):
    try:
        data = json.loads(message)

        # Check if it's an 'order_book' data update
        if data.get('channel') == 'order_book_btcusd' and data.get('event') == 'data':
            # Extract the best bid (highest buy order) and best ask (lowest sell order)
            best_bid = float(data['data']['bids'][0][0])
            best_ask = float(data['data']['asks'][0][0])

            payload = {
                'source': 'bitstamp',
                'symbol': 'BTC-USD',
                'bid_price': best_bid,
                'ask_price': best_ask,
                'timestamp': time.time()
            }

            # Send to Kafka
            producer.send(KAFKA_TOPIC, value=payload, key=b'BTC-USD')
            print(f"BITSTAMP: Sent {payload}")

        # Bitstamp sends a subscription success message
        elif data.get('event') == 'bts:subscription_succeeded':
            print(f"BITSTAMP: Subscription successful to {data.get('channel')}")

    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### Bitstamp WebSocket closed ###")

def on_open(ws):
    print("Bitstamp WebSocket Opened")
    # Subscribe to the BTC-USD order book stream
    subscribe_message = {
        "event": "bts:subscribe",
        "data": {
            "channel": "order_book_btcusd"
        }
    }
    ws.send(json.dumps(subscribe_message))

if __name__ == "__main__":
    # Bitstamp WebSocket URL
    ws_url = "wss://ws.bitstamp.net"
    ws = websocket.WebSocketApp(ws_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()
