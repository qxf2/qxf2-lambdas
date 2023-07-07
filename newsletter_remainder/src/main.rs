extern crate google_sheets4 as sheets4;
extern crate hyper;
extern crate hyper_tls;
extern crate yup_oauth2 as oauth2;

use sheets4::Error;
use sheets4::Sheets;

#[tokio::main]
async fn main() {
    // Get an ApplicationSecret instance by some means. It contains the `client_id` and
    // `client_secret`, among other things.
    let secret = yup_oauth2::read_application_secret("src/credentials.json")
        .await
        .expect("client secret could not be read");


    // Instantiate the authenticator. It will choose a suitable authentication flow for you,
    // unless you replace `None` with the desired Flow.
    // Provide your own `AuthenticatorDelegate` to adjust the way it operates and get feedback about
    // what's going on. You probably want to bring in your own `TokenStorage` to persist tokens and
    // retrieve them from storage.
    let auth = yup_oauth2::InstalledFlowAuthenticator::builder(
        secret,
        yup_oauth2::InstalledFlowReturnMethod::HTTPRedirect,
    )
    .persist_tokens_to_disk("tokencache.json")
    .build()
    .await
    .unwrap();

    let https_connector = hyper_tls::HttpsConnector::new();
    let client = hyper::Client::builder().build::<_, hyper::Body>(https_connector);

    let hub = Sheets::new(client, auth);

    let result = hub
        .spreadsheets()
        .get("14hKG2KauvpHCBeK4wUtMYnl5u0kD4hQTAzTejFr3nlQ") // your spreadsheet id enters here
        .doit()
        .await;

    // println!("{:?}", result);
    match result {
        Err(e) => match e {
            // The Error enum provides details about what exactly happened.
            // You can also just use its `Debug`, `Display` or `Error` traits
            Error::HttpError(_)
            | Error::Io(_)
            | Error::MissingAPIKey
            | Error::MissingToken(_)
            | Error::Cancelled
            | Error::UploadSizeLimitExceeded(_, _)
            | Error::Failure(_)
            | Error::BadRequest(_)
            | Error::FieldClash(_)
            | Error::JsonDecodeError(_, _) => println!("{}", e),
        },
        Ok(res) => println!("Success: {:?}", res),
    }
}
