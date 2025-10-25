import websocket
import json
import time
from kafka import KafkaProducer

# --- START OF DIAGNOSTIC ---
# This enables verbose logging to see all websocket frames (Ping/Pong, etc.)
websocket.enableTrace(True)
# --- END OF DIAGNOSTIC ---

# Kafka Producer setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

KAFKA_TOPIC = 'market-data'

def on_message(ws, message):
    print(f"\n--- ON_MESSAGE RECEIVED: {message[:150]}...\n") # Added a clearer print
    try:
        data = json.loads(message)

        # Look for subscription status
        if isinstance(data, dict) and data.get('event') == 'subscriptionStatus':
            print(f"*** DIAGNOSTIC: Received subscription status! ***\n{message}\n")
            if data.get('status') == 'error':
                print(f"*** KRAKEN ERROR: {data.get('errorMessage')} ***")

        # We look for the 'book-10' channel data
        elif isinstance(data, list) and data[1].get('b') and data[1].get('a'):
            book_data = data[1]
            payload = {
                'source': 'kraken',
                'symbol': 'BTC/USD',
                'bid_price': float(book_data['b'][0]), # Best bid
                'ask_price': float(book_data['a'][0]), # Best ask
                'timestamp': time.time()
            }
            producer.send(KAFKA_TOPIC, value=payload, key=b'BTCUSDT')
            print(f"KRAKEN: Sent {payload}")

    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"--- ON_ERROR: {error}") # Added a clearer print

def on_close(ws, close_status_code, close_msg):
    print(f"--- ON_CLOSE: Code={close_status_code}, Msg={close_msg}") # Added a clearer print

def on_open(ws):
    print("Kraken WebSocket Opened")
    subscribe_message = {
        "event": "subscribe",
        "pair": ["XBT/USD"], # XBT is the classic ticker for BTC on Kraken
        "subscription": {"name": "book", "depth": 10}
    }
    print(f"DIAGNOSTIC: Sending subscription message: {json.dumps(subscribe_message)}")
    ws.send(json.dumps(subscribe_message))
    print("DIAGNOSTIC: Subscription message sent.")

if __name__ == "__main__":
    # Kraken WebSocket URL
    ws_url = "wss://ws.kraken.com/"
    ws = websocket.WebSocketApp(ws_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()
