use std::time::{Duration, Instant};

pub const ICON_PRESS: Duration = Duration::from_millis(80);
pub const ICON_RELEASE: Duration = Duration::from_millis(180);
pub const POPUP_FADE: Duration = Duration::from_millis(140);
pub const POPUP_SLIDE: Duration = Duration::from_millis(180);
pub const GROUP_TOGGLE: Duration = Duration::from_millis(300);
pub const WINDOW_FADE: Duration = Duration::from_millis(220);

pub struct MotionValue {
    value: f32,
    start: f32,
    target: f32,
    started_at: Instant,
    duration: Duration,
}

impl MotionValue {
    pub fn new(value: f32) -> Self {
        Self {
            value,
            start: value,
            target: value,
            started_at: Instant::now(),
            duration: Duration::ZERO,
        }
    }

    pub fn value(&self) -> f32 {
        self.value
    }

    pub fn animate_to(&mut self, target: f32, duration: Duration) {
        if (self.target - target).abs() < f32::EPSILON {
            return;
        }
        self.start = self.value;
        self.target = target;
        self.started_at = Instant::now();
        self.duration = duration;
    }

    pub fn advance(&mut self, now: Instant) -> bool {
        if (self.value - self.target).abs() < 0.0001 {
            self.value = self.target;
            return false;
        }

        let elapsed = now.saturating_duration_since(self.started_at);
        let linear = if self.duration.is_zero() {
            1.0
        } else {
            (elapsed.as_secs_f32() / self.duration.as_secs_f32()).clamp(0.0, 1.0)
        };
        // The PySide preview uses OutCubic for compact controls; keeping one curve
        // here prevents the GPUI port from drifting into a different motion language.
        let eased = 1.0 - (1.0 - linear).powi(3);
        self.value = self.start + (self.target - self.start) * eased;
        if linear >= 1.0 {
            self.value = self.target;
            false
        } else {
            true
        }
    }
}

pub struct IconMotion {
    pub scale: MotionValue,
    pub opacity: MotionValue,
}

impl IconMotion {
    pub fn new() -> Self {
        Self {
            scale: MotionValue::new(1.0),
            opacity: MotionValue::new(1.0),
        }
    }

    pub fn set_pressed(&mut self, pressed: bool) {
        let (scale, opacity, duration) = if pressed {
            (0.85, 0.7, ICON_PRESS)
        } else {
            (1.0, 1.0, ICON_RELEASE)
        };
        self.scale.animate_to(scale, duration);
        self.opacity.animate_to(opacity, duration);
    }

    pub fn advance(&mut self, now: Instant) -> bool {
        self.scale.advance(now) | self.opacity.advance(now)
    }
}

pub struct PopupMotion {
    pub open: bool,
    pub fade: MotionValue,
    pub slide: MotionValue,
}

impl PopupMotion {
    pub fn new() -> Self {
        Self {
            open: false,
            fade: MotionValue::new(0.0),
            slide: MotionValue::new(0.0),
        }
    }

    pub fn set_open(&mut self, open: bool) {
        self.open = open;
        let target = if open { 1.0 } else { 0.0 };
        self.fade.animate_to(target, POPUP_FADE);
        self.slide.animate_to(target, POPUP_SLIDE);
    }

    pub fn advance(&mut self, now: Instant) -> bool {
        self.fade.advance(now) | self.slide.advance(now)
    }
}
