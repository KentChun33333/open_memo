use crate::config::Config;
use crate::strategy::TradeSignal;

pub struct RiskManager {
    config: Config,
    daily_pnl: f64,
    total_capital: f64, // E.g. $50 -> $435,000 tracked here
}

impl RiskManager {
    pub fn new(config: Config, initial_capital: f64) -> Self {
        Self {
            config,
            daily_pnl: 0.0,
            total_capital: initial_capital,
        }
    }

    pub fn process_signal(&mut self, signal: &TradeSignal) -> Option<f64> {
        // Halt if daily max loss is reached
        if self.daily_pnl <= -self.config.strategy.daily_loss_cap * self.total_capital {
            log::error!(
                "RISK MANAGER HALT: Max daily loss reached ({:.2}%). No more trades today.",
                self.config.strategy.daily_loss_cap * 100.0
            );
            return None;
        }

        // Calculate size based on exactly `max_trade_percent` of the portfolio
        let dollar_risk = self.total_capital * self.config.strategy.max_trade_percent;

        // Return exactly how many contracts/shares to buy based on the required dollar allocation
        let shares_to_buy = dollar_risk / signal.limit_price;

        Some(shares_to_buy)
    }

    pub fn record_trade_result(&mut self, pnl: f64) {
        self.daily_pnl += pnl;
        self.total_capital += pnl;
        log::info!(
            "Trade Result: {:.2} | Total Capital: {:.2} | Daily PnL: {:.2}",
            pnl,
            self.total_capital,
            self.daily_pnl
        );
    }
}
