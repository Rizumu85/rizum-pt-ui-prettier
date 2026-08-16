mod components;
mod model;
mod motion;
mod theme;

use std::borrow::Cow;
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

use anyhow::Result;
use components::{
    ComboSpec, ComboVisualState, app_text_style, combo, host_panel, icon_button, inset_separator,
};
use gpui::{
    App, Application, AssetSource, Bounds, Context, Entity, SharedString, TitlebarOptions, Window,
    WindowBounds, WindowOptions, div, prelude::*, px, size,
};
use model::PreviewData;
use motion::{GROUP_TOGGLE, IconMotion, MotionValue, PopupMotion, WINDOW_FADE};
use theme::Theme;

const TEXTURE_SET_COMBO: ComboSpec = ComboSpec {
    id: "texture-set",
    label: "Texture Set:",
    options: &["M_Body", "M_Clothes", "M_Wings"],
    width: 146.0,
};
const CHANNEL_COMBO: ComboSpec = ComboSpec {
    id: "channel",
    label: "Channel:",
    options: &["BaseColor", "Roughness", "Normal"],
    width: 140.0,
};
const ICON_IDS: &[&str] = &["reset", "settings", "undo", "redo", "apply"];

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
    texture_set_index: usize,
    channel_index: usize,
    texture_set_popup: PopupMotion,
    channel_popup: PopupMotion,
    icon_motion: HashMap<&'static str, IconMotion>,
    source_expansion: MotionValue,
    target_expansion: MotionValue,
    source_expanded: bool,
    target_expanded: bool,
    window_opacity: MotionValue,
}

impl BridgePreview {
    fn new() -> Self {
        let mut window_opacity = MotionValue::new(0.0);
        window_opacity.animate_to(1.0, WINDOW_FADE);
        Self {
            data: PreviewData::sample(),
            texture_set_index: 0,
            channel_index: 0,
            texture_set_popup: PopupMotion::new(),
            channel_popup: PopupMotion::new(),
            icon_motion: ICON_IDS
                .iter()
                .copied()
                .map(|id| (id, IconMotion::new()))
                .collect(),
            source_expansion: MotionValue::new(1.0),
            target_expansion: MotionValue::new(1.0),
            source_expanded: true,
            target_expanded: true,
            window_opacity,
        }
    }

    fn toggle_popup(&mut self, popup_id: &'static str) {
        let texture_set_open = popup_id == "texture-set" && !self.texture_set_popup.open;
        let channel_open = popup_id == "channel" && !self.channel_popup.open;
        self.texture_set_popup.set_open(texture_set_open);
        self.channel_popup.set_open(channel_open);
    }

    fn close_popups(&mut self) {
        self.texture_set_popup.set_open(false);
        self.channel_popup.set_open(false);
    }

    fn select_popup_option(&mut self, popup_id: &'static str, index: usize) {
        if popup_id == "texture-set" {
            self.texture_set_index = index;
            self.texture_set_popup.set_open(false);
        } else {
            self.channel_index = index;
            self.channel_popup.set_open(false);
        }
    }

    fn set_icon_pressed(&mut self, id: &'static str, pressed: bool) {
        if let Some(motion) = self.icon_motion.get_mut(id) {
            motion.set_pressed(pressed);
        }
    }

    fn toggle_group(&mut self, panel_id: &'static str) {
        let (expanded, motion) = if panel_id == "source" {
            (&mut self.source_expanded, &mut self.source_expansion)
        } else {
            (&mut self.target_expanded, &mut self.target_expansion)
        };
        *expanded = !*expanded;
        motion.animate_to(if *expanded { 1.0 } else { 0.0 }, GROUP_TOGGLE);
    }

    fn advance_motion(&mut self, window: &mut Window) {
        let now = Instant::now();
        let mut active = self.window_opacity.advance(now)
            | self.texture_set_popup.advance(now)
            | self.channel_popup.advance(now)
            | self.source_expansion.advance(now)
            | self.target_expansion.advance(now);
        for motion in self.icon_motion.values_mut() {
            active |= motion.advance(now);
        }
        if active {
            window.request_animation_frame();
        }
    }

    fn action_bar(&self, theme: Theme, cx: &mut Context<Self>) -> impl IntoElement {
        let entity = cx.entity();
        div()
            .flex()
            .items_center()
            .h(px(43.0))
            .px(px(16.0))
            .gap(px(8.0))
            .child(self.combo_control(
                theme,
                TEXTURE_SET_COMBO,
                self.texture_set_index,
                &self.texture_set_popup,
                entity.clone(),
            ))
            .child(self.combo_control(
                theme,
                CHANNEL_COMBO,
                self.channel_index,
                &self.channel_popup,
                entity.clone(),
            ))
            .child(div().flex_1())
            .child(self.toolbar_button(theme, "reset", "icons/reset.svg", entity.clone()))
            .child(self.toolbar_button(theme, "settings", "icons/settings.svg", entity.clone()))
            .child(div().w(px(1.0)).h(px(18.0)).bg(theme.line))
            .child(self.toolbar_button(theme, "undo", "icons/undo.svg", entity.clone()))
            .child(self.toolbar_button(theme, "redo", "icons/redo.svg", entity.clone()))
            .child(div().w(px(1.0)).h(px(18.0)).bg(theme.line))
            .child(self.toolbar_button(theme, "apply", "icons/checkmark.svg", entity))
    }

    fn combo_control(
        &self,
        theme: Theme,
        spec: ComboSpec,
        selected: usize,
        motion: &PopupMotion,
        entity: Entity<Self>,
    ) -> impl IntoElement {
        let id = spec.id;
        let toggle_entity = entity.clone();
        let select_entity = entity;
        combo(
            theme,
            spec,
            ComboVisualState {
                selected,
                open: motion.open,
                fade: motion.fade.value(),
                slide: motion.slide.value(),
            },
            move |_, _, cx| {
                cx.stop_propagation();
                toggle_entity.update(cx, |this, cx| {
                    this.toggle_popup(id);
                    cx.notify();
                });
            },
            move |index, _, _, cx| {
                select_entity.update(cx, |this, cx| {
                    this.select_popup_option(id, index);
                    cx.notify();
                });
            },
        )
    }

    fn toolbar_button(
        &self,
        theme: Theme,
        id: &'static str,
        path: &'static str,
        entity: Entity<Self>,
    ) -> impl IntoElement {
        let motion = &self.icon_motion[id];
        let press_entity = entity.clone();
        let release_entity = entity;
        icon_button(
            theme,
            id,
            path,
            motion.scale.value(),
            motion.opacity.value(),
            move |_, _, cx| {
                press_entity.update(cx, |this, cx| {
                    this.set_icon_pressed(id, true);
                    cx.notify();
                });
            },
            move |_, _, cx| {
                release_entity.update(cx, |this, cx| {
                    this.set_icon_pressed(id, false);
                    cx.notify();
                });
            },
        )
    }
}

impl Render for BridgePreview {
    fn render(&mut self, window: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        self.advance_motion(window);
        let theme = Theme::painter_dark();
        let entity = cx.entity();
        let source_entity = entity.clone();
        let target_entity = entity.clone();
        let root_entity = entity;

        app_text_style(theme)
            .id("bridge-preview-root")
            .size_full()
            .flex()
            .flex_col()
            .bg(theme.app)
            .opacity(self.window_opacity.value())
            .on_click(move |_, _, cx| {
                root_entity.update(cx, |this, cx| {
                    this.close_popups();
                    cx.notify();
                });
            })
            .child(self.action_bar(theme, cx))
            .child(inset_separator(theme, 12.0))
            .child(
                div()
                    .flex()
                    .flex_1()
                    .min_h(px(0.0))
                    .gap(px(16.0))
                    .p(px(16.0))
                    .child(host_panel(
                        theme,
                        &self.data.source,
                        self.source_expansion.value(),
                        "source",
                        move |_, _, cx| {
                            source_entity.update(cx, |this, cx| {
                                this.toggle_group("source");
                                cx.notify();
                            });
                        },
                    ))
                    .child(host_panel(
                        theme,
                        &self.data.target,
                        self.target_expansion.value(),
                        "target",
                        move |_, _, cx| {
                            target_entity.update(cx, |this, cx| {
                                this.toggle_group("target");
                                cx.notify();
                            });
                        },
                    )),
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
