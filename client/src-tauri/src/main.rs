// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use reqwest::blocking::{self, Client};
use serde_json::json;

#[tauri::command]
fn connect(url: &str, username: &str, password: &str) -> bool {
    let client = Client::new();

    client
        .post("ss")
        .json(&json!(format!(
            r#"
    {{
        "username": {},
        "password": {}
    }}
    "#,
            username, password
        )))
        .send()
        .unwrap();

    return true;
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
