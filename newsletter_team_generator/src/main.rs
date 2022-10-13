extern crate rusoto_core;
extern crate rusoto_sqs;
extern crate rusoto_credential;

use rusoto_sqs::SqsClient;
use rusoto_credential::ChainProvider;
use crate::rusoto_sqs::Sqs;
use lambda_runtime::{service_fn, LambdaEvent, Error};
use serde_json::{json, Value};


const QUEUE_URL:&str = "https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender"

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = service_fn(func);
    lambda_runtime::run(func).await?;
    Ok(())
}

async fn func(event: LambdaEvent<Value>) -> Result<Value, Error> {
    let (event, _context) = event.into_parts();
    let mut team_list = vec!["Akkul","Drishya","Raghava","Ajitava", "Shiva","Avinash","RohanD","Sravanti","Preedhi","Raji"];
    
    
    //Pick a random user from the list
    let random_member_1 = pick_one::pick_one_str(&team_list);
    
    println!("{}",random_member_1);
    let mut member_1 = String::new();
    
    //Remove the user that was already picked
    if let Some(pos) = team_list.iter().position(|x| *x == random_member_1) {
      member_1 = random_member_1.to_string();
      team_list.remove(pos);
    }

    //Pick another user from the altered list
    let member_2 = pick_one::pick_one_str(&team_list);
    println!("{}",member_2 );

    let provider = ChainProvider::new();
    let dispatcher = match HttpClient::new(){
        Ok(client) => client,
        Err(e) => panic!(e)
    };


    let client = SqsClient::new_with(dispatcher, provider, Region::ApSouth1);
      
    Ok(json!({ "Newsletter team": (member_1, member_2) }))

    
}