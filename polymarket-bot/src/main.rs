mod config;
mod executor;
mod feeds;
mod risk_manager;
mod strategy;

use std::sync::Arc;
use tokio::sync::mpsc;

#[tokio::main(flavor = "multi_thread", worker_threads = 8)]
async fn main() {
    // Initialize the logger for standard output debugging
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    log::info!("Starting Polymarket Sub-100ms Arbitrage Bot");

    // 1. Load Configurations
    let cfg = config::load_config("config.yaml");

    // 2. Initialize Shared Memory for Zero-Lock Price Feeds
    let price_feeds = feeds::PriceFeeds::new();

    // 3. Spawn Feed Handlers (WebSockets)
    let pm_cfg = cfg.clone();
    let polymarket_price_ref = Arc::clone(&price_feeds.polymarket_btc);
    tokio::spawn(async move {
        feeds::start_polymarket_feed(pm_cfg, polymarket_price_ref).await;
    });

    let oracle_cfg = cfg.clone();
    let oracle_price_ref = Arc::clone(&price_feeds.oracle_btc);
    tokio::spawn(async move {
        feeds::start_oracle_feed(oracle_cfg, oracle_price_ref).await;
    });

    log::info!("Waiting for price feeds to warm up...");
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

    // 4. Initialize Communication Channels
    let (tx_signal, mut rx_signal) = mpsc::channel::<strategy::TradeSignal>(100);

    // 5. Initialize Engine Components
    let strategy_engine = strategy::StrategyEngine::new(
        cfg.clone(),
        Arc::clone(&price_feeds.polymarket_btc),
        Arc::clone(&price_feeds.oracle_btc),
    );

    // Simulating the "$50 -> $435,000" starting capital
    let mut risk_manager = risk_manager::RiskManager::new(cfg.clone(), 50.0);

    let executor = executor::ExecutionEngine::new(cfg.polymarket.rest_url.clone());

    // 6. Spawn the core Loop (Arbitrage Detector)
    tokio::spawn(async move {
        strategy_engine.run_detector(tx_signal).await;
    });

    // 7. Event Loop to handle Signals -> Risk Check -> Execute
    while let Some(signal) = rx_signal.recv().await {
        // Step A: Risk Management sizes the position or blocks the trade
        if let Some(position_size) = risk_manager.process_signal(&signal) {
            // Step B: Fire off the execution concurrently to avoid blocking the event loop
            // In a burst scenario (1000 orders/sec), each execution gets its own Green Thread
            let execution_payload = signal;

            // In this version, we sequentially block the main loop on execution for safety,
            // but in production we'd spawn a task: tokio::spawn(async move { executor.execute(...) })
            executor
                .execute_order(execution_payload, position_size)
                .await;

            // Assume 0.5% profit on the lag capture
            let pnl = cfg.strategy.max_trade_percent * 50.0 * 0.005; // Dummy PnL hook
            risk_manager.record_trade_result(pnl);
        } else {
            log::warn!("Risk Manager rejected trade signal! Daily max loss hit.");
            break; // Max daily loss hit; shutdown the bot
        }
    }

    log::error!("Event loop terminated. Bot exiting.");
}
