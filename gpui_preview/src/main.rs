mod components;
mod model;
mod theme;

use std::borrow::Cow;
use std::fs;
use std::path::PathBuf;

use anyhow::Result;
use components::{app_text_style, combo, host_panel, icon_button, inset_separator};
use gpui::{
    App, Application, AssetSource, Bounds, Context, SharedString, TitlebarOptions, Window,
    WindowBounds, WindowOptions, div, prelude::*, px, size,
};
use model::PreviewData;
use theme::Theme;

struct Assets {
    root: PathBuf,
}

impl AssetSource for Assets {
    fn load(&self, path: &str) -> Result<Option<Cow<'static, [u8]>>> {
        fs::read(self.root.join(path))
            .map(|bytes| Some(Cow::Owned(bytes)))
            .map_err(Into::into)
    }

    fn list(&self, path: &str) -> Result<Vec<SharedString>> {
        let entries = fs::read_dir(self.root.join(path))?
            .filter_map(|entry| entry.ok())
            .filter_map(|entry| entry.file_name().into_string().ok())
            .map(SharedString::from)
            .collect();
        Ok(entries)
    }
}

struct BridgePreview {
    data: PreviewData,
}

impl BridgePreview {
    fn new() -> Self {
        Self {
            data: PreviewData::sample(),
        }
    }

    fn action_bar(&self, theme: Theme) -> impl IntoElement {
        div()
            .flex()
            .items_center()
            .h(px(43.0))
            .px(px(16.0))
            .gap(px(8.0))
            .child(combo(theme, "Texture Set:", "M_Body", 146.0))
            .child(combo(theme, "Channel:", "BaseColor", 140.0))
            .child(div().flex_1())
            .child(icon_button(theme, "reset", "icons/reset.svg"))
            .child(icon_button(theme, "settings", "icons/settings.svg"))
            .child(div().w(px(1.0)).h(px(18.0)).bg(theme.line))
            .child(icon_button(theme, "undo", "icons/undo.svg"))
            .child(icon_button(theme, "redo", "icons/redo.svg"))
            .child(div().w(px(1.0)).h(px(18.0)).bg(theme.line))
            .child(icon_button(theme, "apply", "icons/checkmark.svg"))
    }
}

impl Render for BridgePreview {
    fn render(&mut self, _window: &mut Window, _cx: &mut Context<Self>) -> impl IntoElement {
        let theme = Theme::painter_dark();

        app_text_style(theme)
            .size_full()
            .flex()
            .flex_col()
            .bg(theme.app)
            .child(self.action_bar(theme))
            .child(inset_separator(theme, 12.0))
            .child(
                div()
                    .flex()
                    .flex_1()
                    .min_h(px(0.0))
                    .gap(px(16.0))
                    .p(px(16.0))
                    .child(host_panel(theme, &self.data.source, true, "source"))
                    .child(host_panel(theme, &self.data.target, true, "target")),
            )
    }
}

fn main() {
    let repository_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("gpui_preview must stay inside the UI source repository")
        .to_path_buf();

    Application::new()
        .with_assets(Assets {
            root: repository_root,
        })
        .run(|cx: &mut App| {
            let bounds = Bounds::centered(None, size(px(580.0), px(430.0)), cx);
            cx.open_window(
                WindowOptions {
                    titlebar: Some(TitlebarOptions {
                        title: Some("Pt Bridge".into()),
                        ..Default::default()
                    }),
                    window_bounds: Some(WindowBounds::Windowed(bounds)),
                    window_min_size: Some(size(px(540.0), px(380.0))),
                    ..Default::default()
                },
                |_, cx| cx.new(|_| BridgePreview::new()),
            )
            .expect("failed to open the PT Bridge GPUI preview");
            cx.activate(true);
        });
}
