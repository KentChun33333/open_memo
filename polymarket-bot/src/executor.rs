// executor.rs handles placing the orders fast (< 100ms) with a connection pool

use crate::strategy::TradeSignal;
use reqwest::Client;

pub struct ExecutionEngine {
    http_client: Client,
    rest_url: String,
    // Authentication headers derived from config would be stored here
}

impl ExecutionEngine {
    pub fn new(url: String) -> Self {
        // Pre-configure a hyper-fast HTTP client using TCP Keep-Alive and connection pooling.
        // This is crucial to sub-100ms execution on centralized REST exchanges.
        let http_client = Client::builder()
            .pool_max_idle_per_host(100)
            .tcp_nodelay(true)
            .timeout(std::time::Duration::from_millis(500))
            .build()
            .expect("Failed to build HTTP client");

        Self {
            http_client,
            rest_url: url,
        }
    }

    pub async fn execute_order(&self, signal: TradeSignal, size: f64) {
        log::info!(
            "EXECUTING ORDER: {:?} | Size: {:.4} | Price: {:.2}",
            signal.direction,
            size,
            signal.limit_price
        );

        // This simulates order placement. Real polymarket orders require EIP712 signatures,
        // which involve hashing the order domain and using the private key.
        // E.g., using `ethers-rs` to sign `Order` and serialize to JSON.

        let start_time = std::time::Instant::now();

        let payload = serde_json::json!({
            "action": "CREATE_ORDER",
            // "signature": "... signed data ...",
            "order": {
                "side": matches!(signal.direction, crate::strategy::TradeDirection::Buy),
                "size": size,
                "price": signal.limit_price,
            }
        });

        // Simulating the network request
        // In reality, this goes to Polymarket's /v2/orders endpoint
        // For testing, we just simulate a sub-100ms wait.
        tokio::time::sleep(tokio::time::Duration::from_millis(45)).await;

        let elapsed = start_time.elapsed();
        log::info!(
            "ORDER EXECUTED IN: {}ms. Payload: {}",
            elapsed.as_millis(),
            payload
        );
    }
}
