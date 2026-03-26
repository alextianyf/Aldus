"""
banner.py
Renders a banner (ASCII art or plain text) as a centered PNG using matplotlib.
Returns the PNG as a base64-encoded string for embedding in HTML.
"""

import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# Path to DejaVuSansMono — bundled with matplotlib, always available
_MONO_FONT = fm.findfont(fm.FontProperties(family='DejaVu Sans Mono'))


def render_banner_b64(lines: list[str], bg_color='#e8eaf6', text_color='#1a237e', fontsize=9) -> str:
    """
    Render a list of text lines as a centered PNG banner.
    Returns a base64-encoded PNG string.
    """
    fp = fm.FontProperties(fname=_MONO_FONT)
    text = '\n'.join(lines)

    fig, ax = plt.subplots(figsize=(11, 2.1))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.axis('off')
    ax.text(
        0.5, 0.5, text,
        transform=ax.transAxes,
        ha='center', va='center',
        fontproperties=fp,
        fontsize=fontsize,
        color=text_color,
        linespacing=1.45,
    )

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=220, bbox_inches='tight', facecolor=bg_color)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def banner_to_html(lines: list[str], width_px=680, **kwargs) -> str:
    """
    Render banner lines as an HTML <img> tag with base64-embedded PNG.
    """
    b64 = render_banner_b64(lines, **kwargs)
    return (
        f'<p style="text-align:center">'
        f'<img src="data:image/png;base64,{b64}" style="width:{width_px}px"/>'
        f'</p>'
    )


def image_to_html(image_path: str, width_px=680) -> str:
    """
    Embed an existing image file as a base64 HTML <img> tag.
    """
    with open(image_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    ext = image_path.rsplit('.', 1)[-1].lower()
    mime = 'image/png' if ext == 'png' else 'image/jpeg'
    return (
        f'<p style="text-align:center">'
        f'<img src="data:{mime};base64,{data}" style="width:{width_px}px"/>'
        f'</p>'
    )
