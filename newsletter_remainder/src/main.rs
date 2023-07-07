extern crate google_sheets4 as sheets4;
extern crate hyper;
extern crate hyper_tls;
extern crate yup_oauth2 as oauth2;
use sheets4::Error;
use sheets4::Sheets;
use rusoto_core::Region;
use rusoto_sqs::{SendMessageRequest, Sqs, SqsClient};

async fn send_message_to_sqs(queue_url: &str, msg: &str, channel: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Create an SQS client
    let client = SqsClient::new(Region::ApSouth1);
    
    // Send a message to the SQS queue
    let message = serde_json::json!({"msg": msg, "channel": channel}).to_string();
    
    let send_message_request = SendMessageRequest {
        queue_url: queue_url.to_string(),
        message_body: message,
        ..Default::default()
    };
    
    match client.send_message(send_message_request).await {
        Ok(response) => {
            println!("Message sent successfully. Message ID: {:?}", response.message_id);
            Ok(())
        }
        Err(error) => {
            Err(Box::new(error))
        }
    }
}

#[tokio::main]
async fn main() {
    // Get Service token
    let secret = yup_oauth2::read_service_account_key("src/newsletter-remainder.json")
        .await
        .unwrap();

    let auth = yup_oauth2::ServiceAccountAuthenticator::builder(secret)
        .build()
        .await
        .unwrap();

    let https_connector = hyper_tls::HttpsConnector::new();
    let client = hyper::Client::builder().build::<_, hyper::Body>(https_connector);

    let hub = Sheets::new(client, auth);
    let spreadsheet_id = "14hKG2KauvpHCBeK4wUtMYnl5u0kD4hQTAzTejFr3nlQ";
    let sheet_name = "Newsletter";
    
    // Get the last row number
    let last_row_range = format!("{}!A:A", sheet_name);
    let last_row_result = hub
        .spreadsheets()
        .values_get(spreadsheet_id, &last_row_range)
        .doit()
        .await;

    let last_row_values = match last_row_result {
        Ok(res) => {
            if let Some(values) = res.1.values {
                values.len()
            } else {
                0
            }
        }
        Err(e) => {
            println!("Error retrieving last row: {}", e);
            return;
        }
    };

    // Fetch the values of the last row
    let range = format!("{}!A{}:Z{}", sheet_name, last_row_values, last_row_values);
    let result = hub
        .spreadsheets()
        .values_get(spreadsheet_id, &range)
        .doit()
        .await;

    match result {
        Err(e) => match e {
            // The Error enum provides details about what exactly happened.
            // You can also just use its `Debug`, `Display`, or `Error` traits.
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
        Ok(res) => {
            if let Some(values) = res.1.values {
                for row in values {
                    println!("{:?}", row[1]);
                    let msg = "Remainder: Newsletter Team for the week: ".to_owned()+ &row[1].to_string();
              
                    let queue_url = "https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender";
                    //let msg = my_string;
                    let channel = "19:1941d15dada14943b5d742f2acdb99aa@thread.skype";
    
                    if let Err(error) = send_message_to_sqs(queue_url, &msg, channel).await {
                        eprintln!("Failed to send message: {:?}", error);
                    }

                }
            } else {
                println!("No data found.");
            }
        }
    }
}
