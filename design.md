# Design

## Project Goal

Create a modern, fluid, beautiful PySide6 component library that Rizum Painter plugins can share while still feeling native inside Substance 3D Painter.

## Visual Direction

- Dark professional UI that fits Painter, but with clearer hierarchy and smoother interaction.
- Subtle depth, crisp borders, compact spacing, and readable typography.
- Motion should be quick and useful: hover fades, button press feedback, progress motion, and optional collapsible panels.
- Avoid decorative excess; the UI should feel like a high-end production tool.

## Interaction Principles

- Use compact controls for repeated production workflows.
- Make primary actions visually clear without turning every button into a large CTA.
- Keep previews close to real plugin layouts so visual decisions transfer into Painter.
- Provide theme application as a reversible layer.

## UI Font Reference Match

- Treat `pt-ui-font-gemini.html` as the current north-star for the UI Font panel.
- Use the same dark surfaces, inset dividers, pill buttons, line SVG icons, and filled checkbox mark.
- Keep divider lines visually present but non-structural: they should not add extra layout height.
- Prefer mock visual controls in the preview when native Qt controls add unwanted platform chrome.
- For screenshot tests, compare against 1x output so font sharpness and icon strokes are judged fairly.
