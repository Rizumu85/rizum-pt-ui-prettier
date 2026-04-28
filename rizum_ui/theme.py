"""Design tokens for the Rizum Painter UI kit."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str = "Rizum Dark"
    font_family: str = "MiSans"
    font_size: int = 10
    radius: int = 7
    radius_small: int = 5
    space_1: int = 4
    space_2: int = 8
    space_3: int = 12
    space_4: int = 16
    bg: str = "#17181b"
    surface: str = "#202226"
    surface_raised: str = "#292c31"
    surface_sunken: str = "#121316"
    border: str = "#3a3f46"
    border_soft: str = "#2e333a"
    text: str = "#f4f6f8"
    text_muted: str = "#b3bac4"
    text_faint: str = "#7c8591"
    accent: str = "#54d6a2"
    accent_hover: str = "#65e4b3"
    accent_pressed: str = "#34b985"
    blue: str = "#6aa8ff"
    warning: str = "#f2b85b"
    danger: str = "#ff6f7d"
    shadow: str = "rgba(0, 0, 0, 110)"
    duration_fast: int = 120
    duration_normal: int = 180


default_theme = Theme()
