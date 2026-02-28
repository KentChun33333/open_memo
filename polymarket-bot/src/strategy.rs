use crate::config::Config;
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};

pub struct StrategyEngine {
    pub config: Config,
    pub polymarket_price: Arc<AtomicU64>,
    pub oracle_price: Arc<AtomicU64>,
}

#[derive(Debug)]
pub enum TradeDirection {
    Buy,
    Sell,
}

#[derive(Debug)]
pub struct TradeSignal {
    pub direction: TradeDirection,
    pub limit_price: f64,
    pub oracle_reference: f64,
}

impl StrategyEngine {
    pub fn new(
        config: Config,
        polymarket_price: Arc<AtomicU64>,
        oracle_price: Arc<AtomicU64>,
    ) -> Self {
        Self {
            config,
            polymarket_price,
            oracle_price,
        }
    }

    pub async fn run_detector(&self, tx: tokio::sync::mpsc::Sender<TradeSignal>) {
        log::info!("Starting Arbitrage Engine...");
        let threshold = self.config.strategy.lag_threshold;

        loop {
            let pm_price = f64::from_bits(self.polymarket_price.load(Ordering::Acquire));
            let or_price = f64::from_bits(self.oracle_price.load(Ordering::Acquire));

            // Wait for feeds to initialize
            if pm_price == 0.0 || or_price == 0.0 {
                tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;
                continue;
            }

            let diff = or_price - pm_price;
            let percent_lag = diff.abs() / pm_price;

            if percent_lag > threshold {
                log::warn!(
                    "Arbitrage Opportunity Detected! Lag: {:.2}%",
                    percent_lag * 100.0
                );

                let direction = if pm_price < or_price {
                    TradeDirection::Buy // Polymarket is underpriced
                } else {
                    TradeDirection::Sell // Polymarket is overpriced
                };

                let signal = TradeSignal {
                    direction,
                    // We target the current PM price or slightly better depending on orderbook
                    limit_price: pm_price,
                    oracle_reference: or_price,
                };

                if let Err(e) = tx.send(signal).await {
                    log::error!("Failed to send trade signal to executor: {}", e);
                }

                // Temporary sleep to prevent flooding the channel while the opportunity persists.
                // In a real bot, you'd track the state to only buy once per side.
                tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
            }

            // High frequency polling the memory location with zero IO cost
            // A tight loop could hit CPU hard, so we hint the async runtime to yield
            tokio::task::yield_now().await;
        }
    }
}
