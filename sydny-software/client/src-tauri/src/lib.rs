use std::net::TcpStream;
use std::process::Command;
use std::thread;
use std::time::{Duration, Instant};
use tauri_plugin_shell::ShellExt;

fn is_ollama_running() -> bool {
    TcpStream::connect_timeout(
        &"127.0.0.1:11434".parse().unwrap(),
        Duration::from_millis(500),
    )
    .is_ok()
}

fn wait_for_ollama(timeout_secs: u64) -> bool {
    let start = Instant::now();
    while start.elapsed().as_secs() < timeout_secs {
        if is_ollama_running() {
            return true;
        }
        thread::sleep(Duration::from_millis(500));
    }
    false
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // start Ollama if it's not already running
            if !is_ollama_running() {
                Command::new("/opt/homebrew/bin/ollama").arg("serve").spawn().ok();
                wait_for_ollama(10);
            }

            // start the Python backend sidecar
            app.shell().sidecar("sydny-server")?.spawn()?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
