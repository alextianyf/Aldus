"""
converter.py
Core markdown → HTML pipeline for Aldus.

Pipeline:
  1. Read markdown
  2. Strip banner block (replaced by UI-controlled banner)
  3. Protect LaTeX math from markdown parser
  4. Convert markdown → HTML
  5. Restore LaTeX math
  6. Embed images as base64
  7. Apply glyph map (special Unicode → HTML)
  8. Load theme CSS
  9. Assemble full HTML document
  10. Write temp HTML file (for Puppeteer to load via file://)
"""

import os
import re
import base64
import subprocess
import tempfile
import markdown

from banner import banner_to_html, image_to_html


# ── Glyph map ────────────────────────────────────────────────────────────────
# Characters that some fonts don't support → safe HTML equivalents
GLYPH_MAP = {
    '\u211d': '<i>R</i>',                            # ℝ
    '\u2115': '<i>N</i>',                            # ℕ
    '\u2124': '<i>Z</i>',                            # ℤ
    '\u2153': '<sup>1</sup>/<sub>3</sub>',           # ⅓
    '\u2154': '<sup>2</sup>/<sub>3</sub>',           # ⅔
    '\u00bc': '<sup>1</sup>/<sub>4</sub>',           # ¼
    '\u00bd': '<sup>1</sup>/<sub>2</sub>',           # ½
    '\u00be': '<sup>3</sup>/<sub>4</sub>',           # ¾
    '\u215b': '<sup>1</sup>/<sub>8</sub>',           # ⅛
}

# ── KaTeX CDN ─────────────────────────────────────────────────────────────────
KATEX_VERSION = '0.16.11'
KATEX_CSS = f'https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css'
KATEX_JS  = f'https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js'
KATEX_AR  = f'https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js'


def _protect_math(text: str) -> tuple[str, list[str]]:
    """
    Replace LaTeX math blocks with safe placeholders so the markdown
    parser doesn't corrupt underscores/asterisks inside equations.
    Returns (protected_text, math_store).
    """
    store = []

    def stash(m):
        store.append(m.group(0))
        return f'MATHPLACEHOLDER{len(store) - 1}END'

    # Display math first ($$...$$), then inline ($...$)
    text = re.sub(r'\$\$[\s\S]*?\$\$', stash, text)
    text = re.sub(r'\$[^\n$]+?\$', stash, text)
    return text, store


def _restore_math(html: str, store: list[str]) -> str:
    return re.sub(
        r'MATHPLACEHOLDER(\d+)END',
        lambda m: store[int(m.group(1))],
        html
    )


def _embed_images(html: str, img_dir: str) -> str:
    """Replace local image src paths with base64-embedded data URIs."""
    def replacer(m):
        src = m.group(1)
        if src.startswith('data:') or src.startswith('http'):
            return m.group(0)
        abs_path = os.path.join(img_dir, os.path.basename(src))
        if os.path.isfile(abs_path):
            data = base64.b64encode(open(abs_path, 'rb').read()).decode()
            ext = abs_path.rsplit('.', 1)[-1].lower()
            mime = 'image/png' if ext == 'png' else 'image/jpeg'
            return f'src="data:{mime};base64,{data}"'
        return m.group(0)
    return re.sub(r'src="([^"]+)"', replacer, html)


def _apply_glyph_map(html: str) -> str:
    for char, repl in GLYPH_MAP.items():
        html = html.replace(char, repl)
    return html


def _strip_banner_block(text: str) -> str:
    """Remove the HTML banner block (table+pre or img) from the markdown."""
    # Match <table align="center">...</table> at the top
    text = re.sub(r'<table align="center">.*?</table>\s*', '', text, flags=re.DOTALL)
    return text


def _load_theme(theme_name: str) -> str:
    themes_dir = os.path.join(os.path.dirname(__file__), 'themes')
    css_path = os.path.join(themes_dir, f'{theme_name}.css')
    if not os.path.isfile(css_path):
        css_path = os.path.join(themes_dir, 'default.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        return f.read()


def _extract_title(text: str) -> str:
    """Extract the first H1 heading as the document title."""
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return re.sub(r'`[^`]*`', lambda x: x.group(0).strip('`'), m.group(1).strip())
    return ''


def build_html(
    md_path: str,
    theme: str = 'default',
    banner_lines: list[str] | None = None,
    banner_image_path: str | None = None,
    author: str = 'Alex Tian',
    include_footer: bool = True,
) -> str:
    """
    Convert a markdown file to a full HTML document string.

    Args:
        md_path:            Path to the .md file
        theme:              Theme name (matches a CSS file in themes/)
        banner_lines:       ASCII art lines to render as banner PNG (optional)
        banner_image_path:  Path to a banner image file (optional, overrides banner_lines)
        author:             Author name for the footer
        include_footer:     Whether to include the footer line

    Returns:
        Full HTML string ready for Puppeteer.
    """
    md_path = os.path.abspath(md_path)
    img_dir = os.path.join(os.path.dirname(md_path), 'images')

    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    title = _extract_title(text)

    # 1. Strip existing banner only if a replacement is provided
    if banner_lines or banner_image_path:
        text = _strip_banner_block(text)

    # 2. Protect math before markdown parsing
    text, math_store = _protect_math(text)

    # 3. Markdown → HTML (toc extension adds id attributes to headings for anchor links)
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'extra', 'sane_lists', 'toc'])
    body = md.convert(text)

    # 4. Restore math
    body = _restore_math(body, math_store)

    # 5. Embed images
    body = _embed_images(body, img_dir)

    # 6. Glyph map
    body = _apply_glyph_map(body)

    # 7. Build banner HTML
    banner_html = ''
    if banner_image_path and os.path.isfile(banner_image_path):
        banner_html = image_to_html(banner_image_path)
    elif banner_lines:
        banner_html = banner_to_html(banner_lines)

    # 8. Footer
    footer_html = ''
    if include_footer and title:
        footer_html = (
            f'<div class="aldus-footer">'
            f'{title} &middot; &copy; {author}'
            f'</div>'
        )

    # 9. Load theme CSS
    css = _load_theme(theme)

    # 10. Assemble full HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="{KATEX_CSS}">
  <script defer src="{KATEX_JS}"></script>
  <script defer src="{KATEX_AR}"
    onload="renderMathInElement(document.body, {{
      delimiters: [
        {{ left: '$$', right: '$$', display: true }},
        {{ left: '$',  right: '$',  display: false }}
      ],
      throwOnError: false
    }});"></script>
  <style>{css}</style>
</head>
<body>
{banner_html}
{body}
{footer_html}
</body>
</html>"""

    return html


def convert(
    md_path: str,
    output_path: str | None = None,
    theme: str = 'default',
    banner_lines: list[str] | None = None,
    banner_image_path: str | None = None,
    author: str = 'Alex Tian',
    renderer_dir: str | None = None,
) -> str:
    """
    Full pipeline: markdown → PDF.

    Returns the path to the generated PDF.
    """
    md_path = os.path.abspath(md_path)

    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + '.pdf'

    # Build HTML
    html = build_html(
        md_path=md_path,
        theme=theme,
        banner_lines=banner_lines,
        banner_image_path=banner_image_path,
        author=author,
    )

    # Write temp HTML next to the markdown file so relative paths resolve
    temp_html = os.path.splitext(md_path)[0] + '.tmp.html'
    try:
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html)

        # Call Puppeteer renderer
        if renderer_dir is None:
            renderer_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'renderer')

        render_script = os.path.join(renderer_dir, 'render.js')
        result = subprocess.run(
            ['node', render_script, temp_html, output_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f'Renderer failed:\n{result.stderr}')

        stdout = result.stdout.strip()
        if not stdout.startswith('OK:'):
            raise RuntimeError(f'Unexpected renderer output: {stdout}')

    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

    return output_path


# ── CLI usage ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python converter.py <file.md> [output.pdf]')
        sys.exit(1)

    md  = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    pdf = convert(md, out)
    print(f'PDF saved to: {pdf}')
