import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS_PATH = ROOT / "design-system" / "tokens.css"
MASTER_PATH = ROOT / "design-system" / "MASTER.md"

TEXT_MIN = 4.5
NON_TEXT_MIN = 3.0

SECTION_PROJECTS = "#F1F5F9"
SECTION_FOOTER = "#020617"
GHOST_HOVER_BG = "#EFF6FF"

TEXT_PAIRS = (
    ("--color-foreground", "--color-background", "Texto base"),
    ("--color-card-foreground", "--color-card", "Texto en card"),
    ("--color-primary", "--color-background", "Botón secundario (hover)"),
    ("--color-on-primary", "--color-primary", "Texto en sección navy"),
    ("--color-on-secondary", "--color-secondary", "Texto en secondary"),
    ("--color-on-accent", "--color-accent", "Botón primario"),
    ("--color-on-accent", "--color-accent-hover", "Botón primario (hover)"),
    ("--color-muted-foreground", "--color-background", "Texto secundario"),
    ("--color-muted-foreground", "--color-card", "Texto secundario en card"),
    ("--color-muted-foreground", "--color-muted", "Texto secundario en muted"),
    ("--color-muted-foreground", SECTION_PROJECTS, "Texto secundario en sección Proyectos"),
    ("--color-accent", "--color-background", "Link"),
    ("--color-accent", "--color-card", "Link en card"),
    ("--color-accent", SECTION_PROJECTS, "Link en sección Proyectos"),
    ("--color-accent", GHOST_HOVER_BG, "Botón ghost (hover)"),
    ("--color-accent-on-dark", "--color-primary", "Link en sección navy"),
    ("--color-accent-on-dark", SECTION_FOOTER, "Link en footer"),
    ("--color-destructive", "--color-background", "Texto de error"),
    ("--color-destructive", "--color-card", "Texto de error en card"),
)

NON_TEXT_PAIRS = (
    ("--color-input-border", "--color-card", "Borde de input"),
    ("--color-input-border", "--color-background", "Borde de input sobre fondo"),
    ("--color-input-border", SECTION_PROJECTS, "Borde de input en sección Proyectos"),
    ("--color-accent", "--color-card", "Borde de input (focus)"),
    ("--color-destructive", "--color-card", "Borde de input (error)"),
    ("--color-ring", "--color-background", "Focus ring en Servicios"),
    ("--color-ring", "--color-card", "Focus ring en Confianza / cards"),
    ("--color-ring", SECTION_PROJECTS, "Focus ring en Proyectos"),
    ("--color-accent-on-dark", "--color-primary", "Focus ring en Hero / Contacto"),
    ("--color-accent-on-dark", SECTION_FOOTER, "Focus ring en Footer"),
    ("--color-accent-on-dark", "--color-accent", "Focus ring en banner CTA"),
)

TOKEN_PATTERN = re.compile(r"(--[\w-]+)\s*:\s*(#[0-9A-Fa-f]{6})\s*;")


def parse_tokens(css_text):
    return {name: value.upper() for name, value in TOKEN_PATTERN.findall(css_text)}


def resolve_color(ref, tokens):
    if ref.startswith("#"):
        return ref.upper()
    return tokens[ref]


def channel_to_linear(channel):
    srgb = channel / 255
    if srgb <= 0.04045:
        return srgb / 12.92
    return ((srgb + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color):
    red, green, blue = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return (
        0.2126 * channel_to_linear(red)
        + 0.7152 * channel_to_linear(green)
        + 0.0722 * channel_to_linear(blue)
    )


def contrast_ratio(color_a, color_b):
    lighter, darker = sorted((relative_luminance(color_a), relative_luminance(color_b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def evaluate_pair(pair, minimum, tokens):
    foreground, background, label = pair
    ratio = contrast_ratio(resolve_color(foreground, tokens), resolve_color(background, tokens))
    return {
        "label": label,
        "foreground": foreground,
        "background": background,
        "ratio": ratio,
        "minimum": minimum,
        "passes": ratio >= minimum,
    }


def evaluate_all(tokens):
    text_results = [evaluate_pair(pair, TEXT_MIN, tokens) for pair in TEXT_PAIRS]
    non_text_results = [evaluate_pair(pair, NON_TEXT_MIN, tokens) for pair in NON_TEXT_PAIRS]
    return text_results + non_text_results


def find_undocumented_tokens(tokens, master_text):
    return [
        name for name, value in tokens.items()
        if not re.search(rf"`{re.escape(value)}`\s*\|\s*`{re.escape(name)}`", master_text, re.IGNORECASE)
    ]


def find_unknown_refs(tokens):
    refs = {ref for pair in TEXT_PAIRS + NON_TEXT_PAIRS for ref in pair[:2]}
    return sorted(ref for ref in refs if ref.startswith("--") and ref not in tokens)


def format_result(result):
    status = "OK  " if result["passes"] else "FAIL"
    return "{} {:5.2f}:1 (min {}) {} | {} sobre {}".format(
        status, result["ratio"], result["minimum"], result["label"],
        result["foreground"], result["background"],
    )


def main():
    tokens = parse_tokens(TOKENS_PATH.read_text(encoding="utf-8"))
    unknown = find_unknown_refs(tokens)
    if unknown:
        print("Tokens referenciados que no existen en tokens.css: " + ", ".join(unknown))
        return 1
    results = evaluate_all(tokens)
    for result in results:
        print(format_result(result))
    undocumented = find_undocumented_tokens(tokens, MASTER_PATH.read_text(encoding="utf-8"))
    for name in undocumented:
        print("FAIL {} ({}) no coincide con la tabla de MASTER.md".format(name, tokens[name]))
    failures = sum(not result["passes"] for result in results) + len(undocumented)
    print("{} pares verificados, {} fallas".format(len(results), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
