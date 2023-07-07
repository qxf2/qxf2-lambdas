extern crate google_sheets4 as sheets4;
use sheets4::Sheets;
use std::collections::HashMap;

mod auth;
mod config;
mod http_client;
mod sheets;

#[tokio::main]
async fn main() {
    let config = config::Config::new();
    let client = http_client::http_client();
    let auth = auth::auth(&config, client.clone()).await;
    let mut hub = Sheets::new(client.clone(), auth);

    let result = sheets::read(&hub, &config).await;

    match result {
        Err(e) => println!("{}", e),
        Ok((_, spreadsheet)) => {
            let totals = HashMap::<String, i32>::new();

            println!(
                "Success: {:?}",
                spreadsheet
                    .values
                    .unwrap()
                    .into_iter()
                    .fold(totals, |mut acc, next_row| {
                        let key: String = next_row[0].clone();
                        let current_value: Option<&i32> = acc.get(&key);
                        let next_value: i32 = next_row[1].parse::<i32>().unwrap();

                        let new_value: i32 = match current_value {
                            None => next_value + 0,
                            Some(x) => next_value + x,
                        };

                        acc.insert(key, new_value);

                        return acc;
                    })
            );
        }
    }
}