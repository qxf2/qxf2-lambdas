use sheets4::{api::ValueRange, hyper, hyper_rustls, Error, Sheets};

use crate::config::Config;

pub async fn read(
    hub: &Sheets,
    config: &Config,
) -> Result<(hyper::Response<hyper::Body>, ValueRange), Error> {
    return hub
        .spreadsheets()
        .values_get(&config.sheet_id, &config.deposit_range_input)
        .doit()
        .await;
}