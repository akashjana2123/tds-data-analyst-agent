# app/tasks/plotter.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64
from PIL import Image
import os

def scatter_with_regression(x, y, xlabel="x", ylabel="y", title=None, dotted_red=True, max_bytes=100000):
    """
    Creates a scatterplot with dotted red regression line.
    Returns datauri: data:image/png;base64,...
    Ensures final PNG is below max_bytes by iterative downscaling and DPI reduction.
    """
    import numpy as np
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    if mask.sum() < 2:
        raise ValueError("Not enough points to plot")

    x = x[mask]; y = y[mask]
    # compute regression
    slope, intercept = np.polyfit(x, y, 1)
    line_x = np.linspace(x.min(), x.max(), 100)
    line_y = slope * line_x + intercept

    fig, ax = plt.subplots(figsize=(6,4))
    ax.scatter(x, y)
    # dotted red regression
    if dotted_red:
        ax.plot(line_x, line_y, linestyle=':', linewidth=1.5, color='red')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(False)
    fig.tight_layout()

    # iterative save to buffer reducing DPI/size until under max_bytes
    dpi = 150
    scale_factor = 1.0
    img_bytes = None
    for attempt in range(8):
        buf = io.BytesIO()
        fig.set_size_inches(6*scale_factor, 4*scale_factor)
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0)
        img = Image.open(buf)
        out_buf = io.BytesIO()
        # try saving PNG (lossless). If too big, convert to PNG with optimized settings or to WEBP if allowed.
        try:
            img.save(out_buf, format="PNG", optimize=True)
        except Exception:
            img.save(out_buf, format="PNG")
        size = out_buf.tell()
        if size <= max_bytes:
            img_bytes = out_buf.getvalue()
            break
        # if too big, reduce dpi and scale down
        dpi = max(30, int(dpi * 0.7))
        scale_factor = max(0.4, scale_factor * 0.8)
    plt.close(fig)
    if img_bytes is None:
        # final fallback: convert to WEBP (smaller) but keep data URI mime type as PNG per spec? We'll prefer PNG but if too large, use webp
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=60, method=6)
        img_bytes = buf.getvalue()
        mime = "image/webp"
    else:
        mime = "image/png"

    b64 = base64.b64encode(img_bytes).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"
    return data_uri, len(img_bytes)
