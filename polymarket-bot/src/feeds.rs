use crate::config::Config;
use futures::{SinkExt, StreamExt};
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use url::Url;

// Prices are shared across tasks using AtomicF64 for zero-lock reads
pub struct PriceFeeds {
    pub polymarket_btc: Arc<AtomicU64>,
    pub oracle_btc: Arc<AtomicU64>,
}

impl PriceFeeds {
    pub fn new() -> Self {
        Self {
            polymarket_btc: Arc::new(AtomicU64::new(0.0f64.to_bits())),
            oracle_btc: Arc::new(AtomicU64::new(0.0f64.to_bits())),
        }
    }
}

pub async fn start_polymarket_feed(config: Config, shared_price: Arc<AtomicU64>) {
    let url = Url::parse(&config.polymarket.ws_url).expect("Invalid WebSocket URL");

    loop {
        log::info!("Connecting to Polymarket WebSocket...");
        match connect_async(url.clone()).await {
            Ok((mut ws_stream, _)) => {
                log::info!("Connected to Polymarket WebSocket");

                // Construct subscription message
                let sub_msg = serde_json::json!({
                    "assets_ids": [config.polymarket.btc_contract_id],
                    "type": "market"
                });

                if let Err(e) = ws_stream.send(Message::Text(sub_msg.to_string())).await {
                    log::error!("Failed to subscribe to Polymarket: {}", e);
                    continue;
                }

                while let Some(msg) = ws_stream.next().await {
                    match msg {
                        Ok(Message::Text(text)) => {
                            // Basic parsing: in production, you'll need the exact JSON schema of Polymarket WS
                            // For this reverse-engineered bot, we assume it sends a `price` field.
                            if let Ok(json) = serde_json::from_str::<serde_json::Value>(&text) {
                                if let Some(price) = json.get("price").and_then(|p| p.as_f64()) {
                                    shared_price.store(price.to_bits(), Ordering::Relaxed);
                                    log::debug!("Polymarket BTC Price Update: {}", price);
                                }
                            }
                        }
                        Ok(Message::Ping(p)) => {
                            let _ = ws_stream.send(Message::Pong(p)).await;
                        }
                        Err(e) => {
                            log::error!("Polymarket WS Error: {}", e);
                            break;
                        }
                        _ => {}
                    }
                }
            }
            Err(e) => {
                log::error!("Failed to connect to Polymarket WS: {}", e);
            }
        }

        log::warn!("Disconnected from Polymarket WS. Reconnecting in 1 second...");
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    }
}

pub async fn start_oracle_feed(config: Config, shared_price: Arc<AtomicU64>) {
    // We'll mock the Oracle feed here. In reality, you'd connect to TradingView WS or CryptoQuant WS.
    // The TradingView implementation requires parsing socket.io payloads.
    // For this blueprint, we'll simulate a feed that randomly walks to test the strategy.

    // In a real implementation:
    // let url = Url::parse(&config.oracles.tradingview_ws_url).unwrap();
    // let (mut ws_stream, _) = connect_async(url).await.unwrap();
    // ... parse tradingview lightcharts format

    log::info!("Starting Simulated Oracle (Real feed implementation pending API access...)");
    let mut current_price = 60000.0; // Simulated starting BTC price

    loop {
        // Random walk
        let change = (rand::random::<f64>() - 0.5) * 100.0;
        current_price += change;

        shared_price.store(current_price.to_bits(), Ordering::Relaxed);
        log::debug!("Oracle BTC Price Update: {}", current_price);

        // Oracle updates typically come in around 10-100ms intervals
        tokio::time::sleep(std::time::Duration::from_millis(100)).await;
    }
}
