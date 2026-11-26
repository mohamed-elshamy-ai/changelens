# changelens design system

Read this before changing the site's UI. Do not introduce a new direction; extend this one. English only. Values below come from `docs/index.html` as of this commit.

## Concept

A redline: old text struck through, new text underlined, every change tagged with a severity and a reason.

Theme: light.

## Color tokens

| Token | Value | Role |
|---|---|---|
| `--bg` | `#fdfcf8` | page background |
| `--fg` | `#16202f` | body text |
| `--mut` | `#5d6677` | secondary text (AA on bg) |
| `--card` | `#ffffff` | card and panel surface |
| `--line` | `#d9d4c5` | borders and dividers |
| `--acc` | `#16202f` | primary action, links, focus ring |
| `--accfg` | `#fdfcf8` | text on accent |
| `--red` | `#c4251a` | removed or high severity |
| `--ins` | `#137a4b` | added text |
| `--code` | `#f4f1e8` | code block background |
| `--codefg` | `#16202f` | code block text |
| `--warn` | `#c4251a` | warning border and limits |
| `--ease-spring` | `cubic-bezier(.22,1.36,.32,1)` | see CSS |
| `--ease-out` | `cubic-bezier(.16,1,.3,1)` | see CSS |

Contrast: every text node on the page is checked against WCAG AA (4.5:1, 3:1 for large text) with a script in the repo owner's QA harness. Keep it passing when you change a color.

## Type

| Token | Stack | Role |
|---|---|---|
| `--arabic` | `'IBM Plex Sans Arabic',sans-serif` | Arabic font stack |
| `--body` | `'Source Sans 3','IBM Plex Sans Arabic',system-ui,sans-serif` | body font stack |
| `--head` | `'Newsreader','IBM Plex Sans Arabic',Georgia,serif` | heading font stack |

Font sizes in use: `.82rem`, `1.9rem`, `1.15rem`, `1.05rem`, `.92rem`, `clamp(2.5rem,7.5vw,4.6rem)`, `1.25rem`, `.9rem`, `.97rem`.

## Spacing, radius, elevation

- Spacing values in use: `2px`, `3px`, `4px`, `6px`, `8px`, `9px`, `10px`, `12px`, `13px`, `14px`, `16px`, `22px`. Prefer these; do not add new ones.
- Radius: `--r` (2px). Use the token, not literals.
- Elevation: `4px 4px 0 var(--red)`, `5px 5px 0 var(--fg)`, `6px 6px 0 var(--line)`

## Motion

- Durations in use: `.08s`, `.16s`, `.24s`, `.25s`, `.2s`, `.3s`, `.5s`, `.7s`, `.8s`, `.9s`, `1.15s`.
- Curves: `cubic-bezier(.16,1,.3,1)`, `cubic-bezier(.22,1.36,.32,1)`.
- Every animation sits behind `prefers-reduced-motion: reduce`, which turns animation and transition off.
- Motion shows state or order. It is never decoration.

## Components and states

- Button `.btn` (filled) and `.btn.alt` (outline): min height 44px, visible `:focus-visible` outline (2px accent), hover and active states.
- Card `.card`, warning card `.card.warn` (left border in `--warn`).
- Language toggle `.langtoggle` with `aria-pressed`.
- Code block `pre`: always LTR, monospace.
- Status words use `.ok b` and `.no b` colors (AA checked).

## RTL rules

- The language toggle sets `dir` and `lang` on `<html>`. Arabic text uses the `--arabic` font and line-height 1.75.
- Use logical CSS (`margin-inline`, `inset-inline-start`, `text-align:start`). No `left` or `right` for layout.
- Letter-spacing is 0 and text-transform none in Arabic.
- Code, terminal output and demo panels stay LTR (`direction:ltr`). Install and demo output stay English.
- Arabic is Egyptian-leaning plain language. Brand names and commands stay Latin.

## Microcopy voice

Plain, specific, honest about limits. Say what it does and what it does not. No hype, no invented numbers.

Examples from the site:

1. Someone sent the edited version.
2. See what actually changed, and which changes matter.
3. Number changed, paragraph 5
4. Severity is a rule-based guess, not legal advice.
5. Live demo

## Do / Don't

| Do | Don't |
|---|---|
| Strike old, underline new | Color-code with many hues |
| State the reason for each severity | Show a bare diff |
| Square corners (2px) | Round the paper |
| Red for HIGH and removal only | Red for decoration |
| Say it is not legal advice | Imply certainty |

## Known hard-coded values (should become tokens)

These literal colors appear in the CSS outside `:root`: `#3a4558`, `#8a5300`, `#fff`.
Also: status colors in `.ok b` and `.no b`, and several literal pixel sizes in component CSS. Move them into tokens next time that block is touched.
