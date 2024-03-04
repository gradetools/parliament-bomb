use serenity::{
    async_trait,
    client::{Client, Context, EventHandler},
    framework::{standard::{macros::{command, group}, CommandResult, StandardFramework}},
    model::{channel::Message, gateway::Ready},
};
use dotenv::dotenv;
use std::env;
use std::time::{SystemTime, UNIX_EPOCH};


struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);
    }
}

#[group]
#[commands(ping, timestamp)]
struct General;

#[command]
async fn ping(ctx: &Context, msg: &Message) -> CommandResult {
    msg.channel_id.say(&ctx.http, "Pong! -- parliamentbomb rust version").await?;

    Ok(())
}

#[command]
async fn timestamp(ctx: &Context, msg: &Message) -> CommandResult {
    let now = SystemTime::now();
    let since_the_epoch = now.duration_since(UNIX_EPOCH)
        .expect("Time went backwards");
    let timestamp = since_the_epoch.as_secs();

    msg.channel_id.say(&ctx.http, format!("Current Unix timestamp: {}", timestamp)).await?;

    Ok(())
}

#[tokio::main]
async fn main() {
    dotenv().ok(); // Load the .env file

    // Get the bot token from the environment variables
    let token = env::var("DISCORD_TOKEN").expect("Expected a token in the environment");

    let framework = StandardFramework::new()
        .configure(|c| c.prefix("!")) // Set the bot's prefix
        .group(&GENERAL_GROUP);

    let mut client = Client::builder(&token)
        .event_handler(Handler)
        .framework(framework)
        .await
        .expect("Error creating client");

    if let Err(why) = client.start().await {
        println!("Client error: {:?}", why);
    }
}

