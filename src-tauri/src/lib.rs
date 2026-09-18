use std::sync::Mutex;
use tauri::{
    image::Image,
    menu::{MenuBuilder, MenuItemBuilder},
    tray::TrayIconBuilder,
    Emitter, Manager, State,
};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut};

struct ClickThroughState(Mutex<bool>);

#[tauri::command]
fn set_click_through(ignore: bool, app: tauri::AppHandle) -> Result<(), String> {
    let window = app.get_webview_window("main").ok_or("Window not found")?;
    window
        .set_ignore_cursor_events(ignore)
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn toggle_click_through(app: tauri::AppHandle, state: State<ClickThroughState>) -> Result<bool, String> {
    let mut is_click_through = state.0.lock().map_err(|e| e.to_string())?;
    *is_click_through = !*is_click_through;
    let new_value = *is_click_through;

    let window = app.get_webview_window("main").ok_or("Window not found")?;
    window
        .set_ignore_cursor_events(new_value)
        .map_err(|e| e.to_string())?;

    app.emit("click-through-changed", new_value)
        .map_err(|e| e.to_string())?;

    update_tray_menu(&app, new_value)?;

    Ok(new_value)
}

fn update_tray_menu(app: &tauri::AppHandle, is_click_through: bool) -> Result<(), String> {
    let label = if is_click_through {
        "Click-through ON"
    } else {
        "Click-through OFF"
    };

    let toggle_item = MenuItemBuilder::with_id("toggle", format!("{} (Option+T)", label))
        .build(app)
        .map_err(|e| e.to_string())?;

    let quit_item = MenuItemBuilder::with_id("quit", "Quit Yomeru")
        .build(app)
        .map_err(|e| e.to_string())?;

    let menu = MenuBuilder::new(app)
        .item(&toggle_item)
        .separator()
        .item(&quit_item)
        .build()
        .map_err(|e| e.to_string())?;

    if let Some(tray) = app.tray_by_id("main") {
        tray.set_menu(Some(menu)).map_err(|e| e.to_string())?;
    }

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .manage(ClickThroughState(Mutex::new(true)))
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            let shortcut = Shortcut::new(Some(Modifiers::ALT), Code::KeyT);

            app.global_shortcut().on_shortcut(
                shortcut,
                |app_handle, _shortcut, event| {
                    if event.state == tauri_plugin_global_shortcut::ShortcutState::Pressed {
                        let state = app_handle.state::<ClickThroughState>();
                        let _ = toggle_click_through(app_handle.clone(), state);
                    }
                },
            )?;

            if let Some(window) = app.get_webview_window("main") {
                let _ = window.set_ignore_cursor_events(true);
                if let Some(monitor) = window.primary_monitor().ok().flatten() {
                    let size = monitor.size();
                    let pos = monitor.position();
                    let scale = monitor.scale_factor();
                    let _ = window.set_size(tauri::LogicalSize::new(size.width as f64 / scale, size.height as f64 / scale));
                    let _ = window.set_position(tauri::LogicalPosition::new(pos.x as f64 / scale, pos.y as f64 / scale));
                }
            }

            let toggle_item = MenuItemBuilder::with_id("toggle", "Click-through ON (Option+T)")
                .build(app)
                .map_err(|e| e.to_string())?;

            let quit_item = MenuItemBuilder::with_id("quit", "Quit Yomeru")
                .build(app)
                .map_err(|e| e.to_string())?;

            let menu = MenuBuilder::new(app)
                .item(&toggle_item)
                .separator()
                .item(&quit_item)
                .build()
                .map_err(|e| e.to_string())?;

            let icon = Image::from_path("icons/icon.png")
                .map_err(|e| e.to_string())?;

            let _tray = TrayIconBuilder::with_id("main")
                .icon(icon)
                .icon_as_template(true)
                .menu(&menu)
                .tooltip("Yomeru - Overlay Translator")
                .on_menu_event(move |app, event| {
                    match event.id().as_ref() {
                        "toggle" => {
                            let state = app.state::<ClickThroughState>();
                            let _ = toggle_click_through(app.clone(), state);
                        }
                        "quit" => {
                            app.exit(0);
                        }
                        _ => {}
                    }
                })
                .build(app)
                .map_err(|e| e.to_string())?;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![set_click_through, toggle_click_through])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
