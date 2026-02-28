use serde::Deserialize;
use std::fs::File;

#[derive(Debug, Deserialize, Clone)]
pub struct PolymarketConfig {
    pub rest_url: String,
    pub ws_url: String,
    pub api_key: String,
    pub api_secret: String,
    pub api_passphrase: String,
    pub btc_contract_id: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct OracleConfig {
    pub tradingview_ws_url: String,
    pub cryptoquant_api_url: String,
    pub tradingview_session: String,
    pub cryptoquant_api_key: String,
    pub cryptoquant_api_secret: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct StrategyConfig {
    pub lag_threshold: f64,
    pub max_trade_percent: f64,
    pub daily_loss_cap: f64,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub polymarket: PolymarketConfig,
    pub oracles: OracleConfig,
    pub strategy: StrategyConfig,
}

pub fn load_config(path: &str) -> Config {
    let file = File::open(path).expect("Could not open config file");
    serde_yaml::from_reader(file).expect("Could not parse config file")
}
