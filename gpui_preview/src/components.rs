use gpui::{Div, FontWeight, SharedString, div, prelude::*, px, rgb, svg};

use crate::model::{HostPanelData, LayerItem, LayerKind};
use crate::theme::{BODY_SIZE, BODY_WEIGHT, FONT_FAMILY, SUB_SIZE, Theme};

fn icon(path: &'static str, size: f32) -> impl IntoElement {
    svg().path(path).size(px(size)).text_color(rgb(0x9e9e9e))
}

pub fn inset_separator(theme: Theme, inset: f32) -> Div {
    div()
        .w_full()
        .h(px(1.0))
        .px(px(inset))
        .child(div().w_full().h(px(1.0)).bg(theme.line))
}

pub fn combo(theme: Theme, label: &'static str, value: &'static str, width: f32) -> Div {
    div()
        .flex()
        .items_center()
        .justify_between()
        .w(px(width))
        .h(px(26.0))
        .px(px(9.0))
        .rounded(px(6.0))
        .bg(theme.control)
        .cursor_pointer()
        .hover(move |style| style.bg(theme.control_hover))
        .child(
            div()
                .flex()
                .items_center()
                .gap(px(4.0))
                .child(div().text_color(theme.text_faint).child(label))
                .child(div().text_color(theme.text).child(value)),
        )
        .child(icon("icons/chevron-down.svg", 12.0))
}

pub fn icon_button(theme: Theme, id: &'static str, path: &'static str) -> impl IntoElement {
    div()
        .id(id)
        .flex()
        .items_center()
        .justify_center()
        .size(px(28.0))
        .rounded(px(6.0))
        .cursor_pointer()
        .hover(move |style| style.bg(theme.control_hover))
        .child(icon(path, 15.0))
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
    expanded: bool,
    panel_id: &'static str,
) -> Div {
    let group_name: SharedString = format!("{panel_id}-group").into();
    let title = data.title;
    let subtitle = data.subtitle;
    let group_title = data.group_name;
    let group_subtitle = data.group_subtitle;

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
            div()
                .flex()
                .flex_col()
                .flex_1()
                .m(px(8.0))
                .p(px(4.0))
                .rounded(px(8.0))
                .group(group_name.clone())
                .hover(move |style| style.bg(theme.group_hover))
                .child(
                    div()
                        .flex()
                        .items_center()
                        .h(px(34.0))
                        .px(px(8.0))
                        .gap(px(9.0))
                        .cursor_pointer()
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
                .when(expanded, |this| {
                    this.children(
                        data.items
                            .iter()
                            .copied()
                            .enumerate()
                            .map(|(index, item)| layer_row(theme, item, index, data.removable)),
                    )
                })
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
        )
}

pub fn app_text_style(theme: Theme) -> Div {
    div()
        .font_family(FONT_FAMILY)
        .font_weight(FontWeight::NORMAL)
        .text_size(px(BODY_SIZE))
        .text_color(theme.text)
}
