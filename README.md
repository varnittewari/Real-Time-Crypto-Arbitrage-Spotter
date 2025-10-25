# Real-Time Crypto Arbitrage Spotter

This project is a real-time, event-driven data pipeline that simulates a low-latency trading system. It ingests live order book data from multiple cryptocurrency exchanges (Bitstamp and Kraken), uses Kafka to process the stream in real-time, and identifies potential arbitrage opportunities.

## Core Features

* **Real-Time Ingestion:** Connects to exchange WebSockets (Bitstamp, Kraken) to stream live L2 order book data.
* **Decoupled Architecture:** Uses Kafka as a message bus to decouple data producers (exchanges) from data consumers (strategy engine).
* **Stream Processing:** A Python service consumes the unified data stream, maintains the current market state in memory, and applies arbitrage logic.
* **Scalable:** New exchanges can be added by simply running a new producer script, with no changes required to the core logic.

## System Architecture

The system is built on a simple "Publisher/Subscriber" model using microservices.



1.  **Producers (`producer_bitstamp.py`, `producer_kraken.py`):** These independent Python scripts connect to each exchange's WebSocket API. When they receive a trade, they format it as a JSON message and **produce** it to the `market-data` Kafka topic.
2.  **Kafka (`docker-compose.yml`):** Acts as the central nervous system. It receives all messages and buffers them for consumers.
3.  **Strategy Engine (`strategy_engine.py`):** This service **consumes** from the `market-data` topic. It listens for messages from *all* producers, compares their prices in real-time, and **produces** a new message to the `arbitrage-opportunities` topic if a profit is found.
4.  **Logger (`logger.py`):** A simple consumer that subscribes to `arbitrage-opportunities` and prints any findings to the console.

## Technologies Used

* **Python 3**
* **Apache Kafka:** The core message bus for stream processing.
* **Docker / Docker Compose:** For running Kafka and Zookeeper in a containerized environment.
* **AWS:** Hosted on an **EC2** instance.
* **Python Libraries:** `kafka-python`, `websocket-client`

## How to Run

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/real-time-arbitrage-spotter.git](https://github.com/YOUR_USERNAME/real-time-arbitrage-spotter.git)
    cd real-time-arbitrage-spotter
    ```

2.  **Launch Kafka & Zookeeper:**
    *Ensure you have Docker and Docker Compose installed.*
    ```bash
    docker-compose up -d
    ```

3.  **Wait for Kafka, then Create Topics:**
    ```bash
    echo "Waiting 30 seconds for Kafka to boot..."
    sleep 30
    docker-compose exec kafka kafka-topics --create --topic market-data --bootstrap-server localhost:9092
    docker-compose exec kafka kafka-topics --create --topic arbitrage-opportunities --bootstrap-server localhost:9092
    ```

4.  **Install Python Dependencies:**
    ```bash
    pip3 install kafka-python websocket-client
    ```

5.  **Run the Services (in 4 separate terminals):**

    * **Terminal 1:**
        ```bash
        python3 producer_bitstamp.py
        ```
    * **Terminal 2:**
        ```bash
        python3 producer_kraken.py
        ```
    * **Terminal 3:**
        ```bash
        python3 strategy_engine.py
        ```
    * **Terminal 4 (Watch for results!):**
        ```bash
        python3 logger.py
        ```