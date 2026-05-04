# Style Study: Gemini HTML Mockups

## Source Files

- `references/html/export_dialogue_animated-gemini.html`
- `references/html/pt-bridge_drag_drop-animated-gemini.html`

## Visual Personality

The target style is a restrained professional production-tool UI. It should feel closer to a polished Adobe panel than a web SaaS dashboard.

Core qualities:

- Deep neutral black/gray foundation.
- Unified background fields unless separation is truly needed.
- No outlines by default unless the control requires them for state or clarity.
- Thin inset separators are preferred over bordered boxes.
- Compact 40px header/action rows.
- Rounded but not bubbly containers.
- High-contrast white primary actions for export/confirm flows.
- Blue accent reserved for bridge/apply/selection meaning.
- Hover states use subtle translucent overlays or rounded outlines, not permanent boxes.
- Controls need breathing room: larger click targets, comfortable padding, and clear icon spacing.
- Motion is smooth and calm, using a soft cubic easing.

## North Star Summary

This style is built through subtraction and tiny spacing corrections. The UI should feel quiet, precise, and industrial, with a hard-core professional tool temperament.

Principles:

- Backgrounds should be consistent and unified unless a split is necessary.
- Do not add outlines by default. Use space, inset separators, and hover-only rounded outlines instead.
- Give controls breathing room: buttons, icons, labels, and checkboxes should never feel like default cramped Painter controls.
- Hover should reveal affordances without shifting layout. No translate/slide motion for tree rows or professional tool lists.
- Keep interaction targets aligned. Right-side checkboxes, handles, and actions must not jitter.
- Prefer blocks and spacing over tree connector lines or permanent borders.
- Hide secondary actions until needed, especially drag handles and remove buttons.
- Use pure white for the most important command and selection states in dark mode. Blue is reserved for bridge/apply semantics and occasional information accents.

## Color System

Important dark tokens extracted from the mockups:

- App background: `#111111`
- Window background: `#1b1b1b`
- Column/card background: `#222222`
- Control/cancel background: `#343434`
- Border/separator when necessary: `#414141`
- Primary text: `#E0E0E0`
- Secondary text: `#9E9E9E`
- Tertiary text: `#666666`
- Bridge blue accent: `#1473E6`
- Confirm/export button background: `#FFFFFF`
- Confirm/export button text: `#1b1b1b`
- Selected checkbox fill: `#FFFFFF`
- Selected checkbox mark/inner contrast: `#1b1b1b`
- Hover overlays: `rgba(255, 255, 255, 0.05)` and `rgba(255, 255, 255, 0.08)`

The UI should not default to green as the main action color. Green can be kept for status only. The default selected/export action language is white, not blue or green.

## Layout Rules

- Header and action bars are around 40px high.
- Footers are about 48px high.
- Horizontal separators are inset by 12px instead of full-width.
- Main dialog padding is usually 16px.
- Tree/list inner padding is 8px.
- Tree item padding is around 8px 10px.
- Child rows indent by 24px.
- Action icon buttons are 30-32px square when space allows.
- Buttons should feel breathable: 30-34px high, pill-shaped for commands.
- Icons and labels need visible spacing, never cramped like default Painter controls.

## Shape Language

- Window radius: 10px.
- Group/card radius: 8px.
- Item radius: 6px.
- Icon button radius: 4-6px.
- Primary and footer buttons use pill radius (`100px` in CSS, large Qt radius in practice).
- Outlines should be absent at rest for most surfaces; hover/focus may reveal a rounded border.

## Typography

- System sans stack in HTML; PySide should prefer MiSans, then Segoe UI.
- Panel title: 13-14px/600.
- Section or column title: 12px/700, uppercase with light letter spacing when used as a column label.
- Item name: 13px/500.
- Meta/subtitle text: 11-12px/500.
- Avoid tiny default Painter text. The UI can be compact without feeling pinched.
- Secondary text should stay visibly dim, not blue-tinted.

## Components To Recreate In PySide6

- Dialog/window shell with deep, consistent background.
- Header/action rows with inset separator lines.
- Pill primary buttons: white background, dark text.
- Secondary buttons: dark gray background.
- Ghost icon/action buttons: transparent until hover.
- Tree groups with hover background and no shifting transform.
- Checkboxes should behave more like larger filled selection tiles, not tiny classic checkboxes.
- Status pills should be low-saturation and compact.
- Hover-only layer actions should be supported later for drag handles and remove buttons.

## PySide6 Translation Notes

Qt stylesheets cannot reproduce every web detail, especially grid accordion animation and SVG icon rendering. The PySide implementation should prioritize:

- Matching color and density.
- Consistent row heights and alignment.
- Inset separators via `QFrame` helpers or local component composition.
- Object-name based styling for custom components.
- Optional component classes for header bars and tree rows later.
- Prefer margin/inset separators over permanent outlines in default component states.
