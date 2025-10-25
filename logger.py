import json
from kafka import KafkaConsumer

# Setup Consumer
consumer = KafkaConsumer(
    'arbitrage-opportunities',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

print("Logger Service Started. Waiting for opportunities...")

for message in consumer:
    opportunity = message.value
    # I want to write to DynamoDB
    print("-------------------------------------------------")
    print(f"          ACTIONABLE OPPORTUNITY LOGGED")
    print(f"Buy at:    {opportunity['buy_at']} @ {opportunity['buy_price']}")
    print(f"Sell at:   {opportunity['sell_at']} @ {opportunity['sell_price']}")
    print(f"Spread:    ${opportunity['spread']}")
    print("-------------------------------------------------\n")