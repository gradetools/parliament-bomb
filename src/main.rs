#![warn(clippy::str_to_string)]

mod commands;
mod splashes;

use poise::serenity_prelude as serenity;
use colored::Colorize;
use dotenv::dotenv;
use std::env;
use std::path::PathBuf;
use ctrlc;
use rand::Rng;
use rand::SeedableRng;
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
    time::Duration,
};


type Error = Box<dyn std::error::Error + Send + Sync>;
type Context<'a> = poise::Context<'a, Data, Error>;

fn get_binary_location() -> String {
    let binary_location: PathBuf = match env::current_exe() {
        Ok(path) => path,
        Err(e) => {
            println!("Failed to get the binary location: {}", e);
            return "Unknown location".to_string(); 
        }
    };

    // Convert PathBuf to String
    binary_location.to_str().unwrap_or("Unknown location").to_string()
}

pub struct Data {
    votes: Mutex<HashMap<String, u32>>,
}

async fn on_error(error: poise::FrameworkError<'_, Data, Error>) {
    match error {
        poise::FrameworkError::Setup { error, .. } => panic!("Failed to start bot: {:?}", error),
        poise::FrameworkError::Command { error, ctx, .. } => {
            println!("Error in command `{}`: {:?}", ctx.command().name, error,);
        }
        error => {
            if let Err(e) = poise::builtins::on_error(error).await {
                println!("Error while handling error: {}", e)
            }
        }
    }
}

#[tokio::main]
async fn main() {
    env_logger::init();
    dotenv().ok();

    let options = poise::FrameworkOptions {
        commands: vec![commands::help(), commands::vote(), commands::getvotes()],
        prefix_options: poise::PrefixFrameworkOptions {
            prefix: Some("~".into()),
            edit_tracker: Some(Arc::new(poise::EditTracker::for_timespan(
                Duration::from_secs(3600),
            ))),
            additional_prefixes: vec![
                poise::Prefix::Literal("hey bot"),
                poise::Prefix::Literal("hey bot,"),
            ],
            ..Default::default()
        },
        on_error: |error| Box::pin(on_error(error)),
        pre_command: |ctx| {
            Box::pin(async move {
                println!("Executing command {}...", ctx.command().qualified_name);
            })
        },
        post_command: |ctx| {
            Box::pin(async move {
                println!("Executed command {}!", ctx.command().qualified_name);
            })
        },
        command_check: Some(|ctx| {
            Box::pin(async move {
                if ctx.author().id == 123456789 {
                    return Ok(false);
                }
                Ok(true)
            })
        }),
        skip_checks_for_owners: false,
        event_handler: |_ctx, event, _framework, _data| {
            Box::pin(async move {
                println!(
                    "Got an event in event handler: {:?}",
                    event.snake_case_name()
                );
                Ok(())
            })
        },
        ..Default::default()
    };

    let framework = poise::Framework::builder()
        .setup(move |ctx, _ready, framework| {
            Box::pin(async move {
                let version = env!("CARGO_PKG_VERSION");
                let binary_location_str = get_binary_location();
                let mut rng = rand::rngs::StdRng::from_entropy();
                let splash = rng.gen_range(0..splashes::SPLASHES.len());
                println!("");
                println!("{}", "Welcome to ParliamentBomb!".green().bold());
                println!("{}", splashes::SPLASHES[splash]);
                println!("");
                println!("{}", format!("Version: {}", version));
                println!("Binary Location: {}", binary_location_str);
                println!("Bug Reports: https://github.com/gradetools/parliament-bomb/issues");
                println!("Discussion Board: https://github.com/gradetools/parliament-bomb/discussions");
                println!("");
                println!("Successfully Logged in as {}", _ready.user.name);
                println!(">>>>> BEGIN PARLIAMENTBOMB LOGGING HERE <<<<<");
                ctrlc::set_handler(move || {
                    println!(" <-- Ctrl+C pressed, exiting...");
                    println!(">>>>> END PARLIAMENTBOMB LOGGING HERE <<<<<");
                    std::process::exit(0); 
                }).expect("Error setting Ctrl-C handler");
            
            
                poise::builtins::register_globally(ctx, &framework.options().commands).await?;
                Ok(Data {
                    votes: Mutex::new(HashMap::new()),
                })
            })
        })
        .options(options)
        .build();

    let token = env::var("DISCORD_TOKEN")
        .expect("Missing `DISCORD_TOKEN` env var, see README for more information.");
    let intents =
        serenity::GatewayIntents::non_privileged() | serenity::GatewayIntents::MESSAGE_CONTENT;

    let client = serenity::ClientBuilder::new(token, intents)
        .framework(framework)
        .await;

    client.unwrap().start().await.unwrap();
}