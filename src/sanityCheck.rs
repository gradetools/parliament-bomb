use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::process;

// parliamentbomb sanity check file.
//
// this program sends a small heartbeat request to
// a main server to display server & client server status.
// this could be used to show server data at a web portal
// for example.
//
// this is all still a huge TODO, and will be completed later.


// get env variables. currently supports
//
// HEARTBEAT_URL=<url or ip>
// > defines the place to send the heartbeat signal.

fn get_env_var(name: &str) -> io::Result<String> {
    let file = File::open(".env")?;
    let reader = BufReader::new(file);

    for line in reader.lines() {
        let line = line?;
        let parts: Vec<&str> = line.splitn(2, '=').collect();
        if parts.len() == 2 && parts == name {
            return Ok(parts.to_string());
        }
    }

    Err(io::Error::new(io::ErrorKind::NotFound, "Environment variable not found"))
}

// send heartbeat request
async fn send_heartbeat_request(url: &str) -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let response = client.get(url).send().await?;

    if response.status().is_success() {
        let text = response.text().await?;
        println!("Response: {}", text);
    } else {
        eprintln!("Failed to send heartbeat request");
    }

    Ok(())
}

#[tokio::main]
async fn main() {
    match get_env_var("HEARTBEAT_URL") {
        Ok(url) => {
            if let Err(e) = send_heartbeat_request(&url).await {
                eprintln!("Error sending heartbeat request: {}", e);
            }
        }
        Err(e) => {
            eprintln!("Error getting HEARTBEAT_URL: {}", e);
            process::exit(1);
        }
    }
}