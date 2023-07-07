pub struct Config {
    pub priv_key: String,
    pub sheet_id: String,
    pub deposit_range_input: String,
    pub deposit_range_output: String,
}

impl Config {
    pub fn new() -> Config {
        Config {
            priv_key: String::from("src/newsletter-remainder.json"),
            sheet_id: String::from("14hKG2KauvpHCBeK4wUtMYnl5u0kD4hQTAzTejFr3nlQ"),
            deposit_range_input: String::from("Deposits Stream!A2:B"),
            deposit_range_output: String::from("Deposits Stream!G1"),
        }
    }
}