use std::f32::consts::{FRAC_PI_2, PI};

use gpui::{
    App, ClickEvent, Div, FontWeight, Hsla, MouseButton, MouseDownEvent, MouseUpEvent,
    SharedString, Transformation, Window, deferred, div, prelude::*, px, radians, rgb, size, svg,
};

use crate::model::{HostPanelData, LayerItem, LayerKind};
use crate::theme::{BODY_SIZE, BODY_WEIGHT, FONT_FAMILY, SUB_SIZE, Theme};

fn icon(path: &'static str, size: f32) -> gpui::Svg {
    svg().path(path).size(px(size)).text_color(rgb(0x9e9e9e))
}

fn transformed_icon(
    path: &'static str,
    size_px: f32,
    scale: f32,
    opacity: f32,
    rotation: f32,
) -> gpui::Svg {
    icon(path, size_px)
        .text_color(Hsla::from(rgb(0x9e9e9e)).opacity(opacity))
        .with_transformation(
            Transformation::scale(size(scale, scale)).with_rotation(radians(rotation)),
        )
}

pub fn inset_separator(theme: Theme, inset: f32) -> Div {
    div()
        .w_full()
        .h(px(1.0))
        .px(px(inset))
        .child(div().w_full().h(px(1.0)).bg(theme.line))
}

#[derive(Clone, Copy)]
pub struct ComboSpec {
    pub id: &'static str,
    pub label: &'static str,
    pub options: &'static [&'static str],
    pub width: f32,
}

#[derive(Clone, Copy)]
pub struct ComboVisualState {
    pub selected: usize,
    pub open: bool,
    pub fade: f32,
    pub slide: f32,
}

pub fn combo<Toggle, Select>(
    theme: Theme,
    spec: ComboSpec,
    visual: ComboVisualState,
    on_toggle: Toggle,
    on_select: Select,
) -> impl IntoElement
where
    Toggle: Fn(&ClickEvent, &mut Window, &mut App) + Clone + 'static,
    Select: Fn(usize, &ClickEvent, &mut Window, &mut App) + Clone + 'static,
{
    let value = spec.options[visual.selected];
    let show_popup = visual.open || visual.fade > 0.001;
    let popup = div()
        .id(SharedString::from(format!("combo-popup-{}", spec.id)))
        .absolute()
        .top(px(30.0 - 6.0 * (1.0 - visual.slide)))
        .left(px(0.0))
        .w_full()
        .py(px(4.0))
        .rounded(px(6.0))
        .bg(theme.control)
        .border_1()
        .border_color(theme.line)
        .shadow_md()
        .opacity(visual.fade)
        .occlude()
        .children(spec.options.iter().enumerate().map(|(index, option)| {
            let on_select = on_select.clone();
            div()
                .id(("combo-option", index))
                .flex()
                .items_center()
                .h(px(26.0))
                .px(px(9.0))
                .text_color(if *option == value {
                    theme.text
                } else {
                    theme.text_muted
                })
                .cursor_pointer()
                .hover(move |style| style.bg(theme.control_hover))
                .on_click(move |event, window, cx| {
                    cx.stop_propagation();
                    on_select(index, event, window, cx);
                })
                .child(*option)
        }));

    div()
        .id(SharedString::from(format!("combo-{}", spec.id)))
        .relative()
        .flex()
        .items_center()
        .justify_between()
        .w(px(spec.width))
        .h(px(26.0))
        .px(px(9.0))
        .rounded(px(6.0))
        .bg(theme.control)
        .cursor_pointer()
        .hover(move |style| style.bg(theme.control_hover))
        .on_click(on_toggle)
        .child(
            div()
                .flex()
                .items_center()
                .gap(px(4.0))
                .child(div().text_color(theme.text_faint).child(spec.label))
                .child(div().text_color(theme.text).child(value)),
        )
        .child(transformed_icon(
            "icons/chevron-down.svg",
            12.0,
            1.0,
            1.0,
            PI * visual.slide,
        ))
        .when(show_popup, |this| this.child(deferred(popup)))
}

pub fn icon_button<Press, Release>(
    theme: Theme,
    id: &'static str,
    path: &'static str,
    scale: f32,
    opacity: f32,
    on_press: Press,
    on_release: Release,
) -> impl IntoElement
where
    Press: Fn(&MouseDownEvent, &mut Window, &mut App) + 'static,
    Release: Fn(&MouseUpEvent, &mut Window, &mut App) + Clone + 'static,
{
    div()
        .id(id)
        .flex()
        .items_center()
        .justify_center()
        .size(px(28.0))
        .rounded(px(6.0))
        .cursor_pointer()
        .hover(move |style| style.bg(theme.control_hover))
        .on_mouse_down(MouseButton::Left, on_press)
        .on_mouse_up(MouseButton::Left, on_release.clone())
        .on_mouse_up_out(MouseButton::Left, on_release)
        .child(transformed_icon(path, 15.0, scale, opacity, 0.0))
}

fn layer_icon(theme: Theme, item: LayerItem) -> Div {
    let icon_path = match item.kind {
        LayerKind::Layer => "icons/layers.svg",
        LayerKind::Folder => "icons/folder-filled.svg",
    };

    div()
        .flex()
        .items_start()
        .w(px(25.0))
        .h(px(22.0))
        .child(
            div()
                .flex()
                .items_center()
                .justify_center()
                .size(px(20.0))
                .rounded(px(3.0))
                .bg(theme.control)
                .border_1()
                .border_color(theme.text_muted)
                .child(icon(icon_path, 13.0)),
        )
        .when(item.masked, |this| {
            this.child(
                div()
                    .mt(px(10.0))
                    .ml(px(-7.0))
                    .size(px(10.0))
                    .rounded(px(2.0))
                    .bg(theme.text)
                    .border_1()
                    .border_color(theme.panel),
            )
        })
}

fn remove_button(theme: Theme, group_name: SharedString) -> Div {
    div()
        .flex()
        .items_center()
        .justify_center()
        .size(px(22.0))
        .rounded(px(5.0))
        .opacity(0.0)
        .text_color(theme.danger)
        .group_hover(group_name, |style| style.opacity(1.0))
        .hover(move |style| style.bg(theme.danger.opacity(0.16)))
        .child(icon("icons/x.svg", 12.0))
}

fn layer_row(theme: Theme, item: LayerItem, index: usize, removable: bool) -> Div {
    let group_name: SharedString = format!("layer-row-{index}-{}", item.name).into();
    let row_bg = if item.mapped {
        theme.mapped
    } else {
        theme.panel
    };

    div()
        .group(group_name.clone())
        .flex()
        .items_center()
        .h(px(34.0))
        .ml(px(24.0))
        .px(px(8.0))
        .gap(px(10.0))
        .rounded(px(6.0))
        .bg(row_bg)
        .cursor_move()
        .when(item.mapped, |this| {
            this.border_l_2().border_color(theme.text)
        })
        .hover(move |style| style.bg(theme.control_hover))
        .child(layer_icon(theme, item))
        .child(div().flex_1().text_color(theme.text).child(item.name))
        .when(removable, |this| {
            this.child(remove_button(theme, group_name))
        })
}

pub fn host_panel(
    theme: Theme,
    data: &HostPanelData,
    expansion: f32,
    panel_id: &'static str,
    on_toggle: impl Fn(&ClickEvent, &mut Window, &mut App) + 'static,
) -> Div {
    let group_name: SharedString = format!("{panel_id}-group").into();
    let title = data.title;
    let subtitle = data.subtitle;
    let group_title = data.group_name;
    let group_subtitle = data.group_subtitle;
    let helper_height = if panel_id == "target" { 24.0 } else { 0.0 };
    let expanded_height = data.items.len() as f32 * 34.0 + helper_height;

    div()
        .flex()
        .flex_col()
        .flex_1()
        .min_w(px(0.0))
        .h_full()
        .rounded(px(8.0))
        .bg(theme.panel)
        .shadow_md()
        .child(
            div()
                .flex()
                .flex_col()
                .gap(px(2.0))
                .px(px(16.0))
                .pt(px(12.0))
                .pb(px(10.0))
                .child(
                    div()
                        .text_size(px(12.0))
                        .font_weight(BODY_WEIGHT)
                        .text_color(theme.text)
                        .child(title),
                )
                .child(
                    div()
                        .text_size(px(SUB_SIZE))
                        .font_weight(BODY_WEIGHT)
                        .text_color(theme.text_faint)
                        .child(subtitle),
                ),
        )
        .child(inset_separator(theme, 12.0))
        .child(
            div().flex().flex_col().flex_1().m(px(8.0)).child(
                div()
                    .group(group_name.clone())
                    .flex()
                    .flex_col()
                    .p(px(4.0))
                    .rounded(px(8.0))
                    .hover(move |style| style.bg(theme.group_hover))
                    .child(
                        div()
                            .flex()
                            .items_center()
                            .h(px(34.0))
                            .px(px(8.0))
                            .gap(px(9.0))
                            .cursor_pointer()
                            .id(if panel_id == "source" {
                                "source-group-toggle"
                            } else {
                                "target-group-toggle"
                            })
                            .on_click(on_toggle)
                            .child(transformed_icon(
                                "icons/chevron-right.svg",
                                12.0,
                                1.0,
                                1.0,
                                FRAC_PI_2 * expansion,
                            ))
                            .child(icon("icons/folder-filled.svg", 14.0))
                            .child(
                                div()
                                    .flex()
                                    .flex_col()
                                    .flex_1()
                                    .child(
                                        div()
                                            .text_color(theme.text)
                                            .font_weight(BODY_WEIGHT)
                                            .child(group_title),
                                    )
                                    .when(!group_subtitle.is_empty(), |this| {
                                        this.child(
                                            div()
                                                .text_size(px(SUB_SIZE))
                                                .text_color(theme.text_faint)
                                                .child(group_subtitle),
                                        )
                                    }),
                            ),
                    )
                    .child(
                        div()
                            .flex()
                            .flex_col()
                            .h(px(expanded_height * expansion))
                            .opacity(expansion)
                            .overflow_hidden()
                            .children(
                                data.items.iter().copied().enumerate().map(|(index, item)| {
                                    layer_row(theme, item, index, data.removable)
                                }),
                            )
                            .when(panel_id == "target", |this| {
                                this.child(
                                    div()
                                        .mt(px(4.0))
                                        .ml(px(34.0))
                                        .text_size(px(SUB_SIZE))
                                        .text_color(theme.text_faint)
                                        .child("Drop Photoshop layers here to map"),
                                )
                            }),
                    ),
            ),
        )
}

pub fn app_text_style(theme: Theme) -> Div {
    div()
        .font_family(FONT_FAMILY)
        .font_weight(FontWeight::NORMAL)
        .text_size(px(BODY_SIZE))
        .text_color(theme.text)
}
