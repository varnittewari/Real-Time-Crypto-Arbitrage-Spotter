import json
import time
from kafka import KafkaConsumer, KafkaProducer

# Setup Consumer
consumer = KafkaConsumer(
    'market-data',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest' # Start from new messages
)

# Setup Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

KAFKA_OPPORTUNITY_TOPIC = 'arbitrage-opportunities'

# in-memory state
current_market_state = {
    'bitstamp': {'bid_price': None, 'ask_price': None, 'timestamp': None},
    'kraken':  {'bid_price': None, 'ask_price': None, 'timestamp': None}
}

print("Strategy Engine Started...")

for message in consumer:
    data = message.value
    source = data['source']

    # Update the state for the source
    current_market_state[source]['bid_price'] = data['bid_price']
    current_market_state[source]['ask_price'] = data['ask_price']
    current_market_state[source]['timestamp'] = data['timestamp']

    # Check if we have data from both exchanges
    bitstamp = current_market_state['bitstamp']
    kraken = current_market_state['kraken']

    if bitstamp['bid_price'] and kraken['ask_price']:
        # Arbitrage Logic 1: Can we BUY on KRAKEN and SELL on bitstamp?
        # We buy at Kraken's ask price, sell at bitstamp's bid price
        if bitstamp['bid_price'] > kraken['ask_price']:
            spread = bitstamp['bid_price'] - kraken['ask_price']
            opportunity = {
                'type': 'ARBITRAGE',
                'buy_at': 'kraken',
                'sell_at': 'bitstamp',
                'buy_price': kraken['ask_price'],
                'sell_price': bitstamp['bid_price'],
                'spread': spread,
                'timestamp': time.time()
            }
            # Log to console AND send to Kafka
            print(f"!!! OPPORTUNITY FOUND: {opportunity}")
            producer.send(KAFKA_OPPORTUNITY_TOPIC, value=opportunity)

    if kraken['bid_price'] and bitstamp['ask_price']:
        # Arbitrage Logic 2: Can we BUY on BINANCE and SELL on KRAKEN?
        # We buy at bitstamp's ask price, sell at Kraken's bid price
        if kraken['bid_price'] > bitstamp['ask_price']:
            spread = kraken['bid_price'] - bitstamp['ask_price']
            opportunity = {
                'type': 'ARBITRAGE',
                'buy_at': 'bitstamp',
                'sell_at': 'kraken',
                'buy_price': bitstamp['ask_price'],
                'sell_price': kraken['bid_price'],
                'spread': spread,
                'timestamp': time.time()
            }
            # Log to console AND send to Kafka
            print(f"!!! OPPORTUNITY FOUND: {opportunity}")
            producer.send(KAFKA_OPPORTUNITY_TOPIC, value=opportunity)