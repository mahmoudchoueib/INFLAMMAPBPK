"""Render dashboard figures as PNG without a browser or a JavaScript chart engine."""

from io import BytesIO
from threading import RLock

import numpy as np
from matplotlib.figure import Figure

_RENDER_LOCK = RLock()


def chart_png(figure) -> bytes:
    """Preserve the data, labels and error bars of supported dashboard traces."""
    with _RENDER_LOCK:
        canvas = Figure(figsize=(10, 4.8), layout="constrained")
        axes = canvas.subplots()
        for trace in figure.data:
            label = trace.name or None
            x = np.asarray(trace.x) if trace.x is not None else np.array([])
            y = np.asarray(trace.y) if getattr(trace, "y", None) is not None else np.array([])
            if trace.type == "histogram":
                axes.hist(x.astype(float), bins=40, label=label, color="#176c80", alpha=0.85)
            elif trace.type == "bar":
                errors = trace.error_y.array if trace.error_y is not None else None
                axes.bar(x, y, yerr=errors, capsize=4, label=label, color="#176c80")
            elif trace.type == "scatter":
                if trace.mode and "lines" in trace.mode:
                    axes.plot(x, y, label=label, linewidth=2)
                else:
                    axes.scatter(x, y, label=label, color="#176c80")
            else:
                raise ValueError(f"Static rendering is not implemented for {trace.type}")
        axes.set_title(figure.layout.title.text or "")
        axes.set_xlabel(figure.layout.xaxis.title.text or "")
        axes.set_ylabel(figure.layout.yaxis.title.text or "")
        axes.grid(alpha=0.2)
        if any(trace.name for trace in figure.data):
            axes.legend(loc="best", fontsize="small")
        if any(trace.type == "bar" for trace in figure.data):
            axes.tick_params(axis="x", labelrotation=25)
        output = BytesIO()
        canvas.savefig(output, format="png", dpi=150)
        return output.getvalue()
