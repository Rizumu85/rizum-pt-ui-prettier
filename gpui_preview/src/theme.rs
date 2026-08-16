use gpui::{FontWeight, Hsla, rgb};

#[derive(Clone, Copy)]
pub struct Theme {
    pub app: Hsla,
    pub panel: Hsla,
    pub control: Hsla,
    pub control_hover: Hsla,
    pub group_hover: Hsla,
    pub mapped: Hsla,
    pub line: Hsla,
    pub text: Hsla,
    pub text_muted: Hsla,
    pub text_faint: Hsla,
    pub danger: Hsla,
}

impl Theme {
    pub fn painter_dark() -> Self {
        Self {
            app: rgb(0x1b1b1b).into(),
            panel: rgb(0x222222).into(),
            control: rgb(0x2b2b2b).into(),
            control_hover: rgb(0x363636).into(),
            group_hover: rgb(0x2a2a2a).into(),
            mapped: rgb(0x303030).into(),
            line: rgb(0x353535).into(),
            text: rgb(0xe0e0e0).into(),
            text_muted: rgb(0x9e9e9e).into(),
            text_faint: rgb(0x666666).into(),
            danger: rgb(0xff453a).into(),
        }
    }
}

pub const FONT_FAMILY: &str = "MiSans";
pub const BODY_SIZE: f32 = 13.0;
pub const SUB_SIZE: f32 = 11.0;
pub const BODY_WEIGHT: FontWeight = FontWeight::NORMAL;
