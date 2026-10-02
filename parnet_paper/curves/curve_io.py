"""Load exported ROC/PRC curves (plain JSON) and plot them with matplotlib.

Standalone on purpose: depends only on numpy + matplotlib, not on ``pylbsr`` or
``mutations_analyses_libs`` (those pull in the whole analysis environment). The JSON
files are produced by the ``export_roc_prc_curves`` Snakemake rule in
parnet--analyses--mutations (``workflow/rules/roc_prc_export.smk``), one file per
dataset, schema::

    {"schema_version": 1, "dataset": str, "display_name": str, "build_date": str,
     "n_points": 101, "label_source": {...}, "missing_methods": [str, ...],
     "methods": [{"name": str, "family": str, "window": str | null, "variant": str,
                  "auroc": float, "auprc": float, "n_pos": int, "n_neg": int,
                  "random_clf": float,      # PRC no-skill baseline, n_pos / (n_pos + n_neg)
                  "fpr": [101 floats], "tpr": [101 floats],
                  "precision": [101 floats], "recall": [101 floats]}, ...]}

Curves are already on a fixed 101-point interpolation grid (fpr for ROC, recall for
PRC) and already oriented so that AUROC >= 0.5 (scorers with AUROC < 0.5 were inverted
at export time). AUROC/AUPRC values are the exported ones, not recomputed here.

Plotting mirrors ``pylbsr.ml_stats.roc_prc.ROCresults.plot(ax=, plot_params=)``:
``ax=None`` creates a new 7x7 figure, otherwise the curve is drawn onto the given axes
(so several curves overlay on one shared axes), and the call returns ``(fig, ax)`` with
``fig=None`` when an axes was passed in.

Usage::

    import matplotlib.pyplot as plt
    from parnet_paper.curves.curve_io import CurveSet, format_roc_axes, format_prc_axes

    cs = CurveSet.from_json("data/roc_prc/mutsplicedb.json")
    print(cs.names)                                  # every exported method
    c = cs.get("OpenSpliceAI DS_max (d5)")
    print(c.auroc, c.auprc, c.n_pos, c.n_neg)

    # Overlay several curves on shared axes.
    fig, (ax_roc, ax_prc) = plt.subplots(1, 2, figsize=(10, 5))
    for name, color in [("PARNET JSD center11", "#d6609a"),
                        ("RiNALMo cosine-dist CLS", "#3f8fd1")]:
        curve = cs.get(name)
        curve.plot_roc(ax=ax_roc, color=color, label=f"{name} ({curve.auroc:.3f})")
        curve.plot_prc(ax=ax_prc, plot_params={"color": color, "lw": 2})
    format_roc_axes(ax_roc)            # diagonal, labels, limits, equal aspect
    format_prc_axes(ax_prc, baseline=cs.get("PARNET JSD center11").random_clf)
    ax_roc.legend(loc="lower right")

    # Selecting by metadata instead of by name.
    for c in cs.filter(family="openspliceai"):
        print(c.window, round(c.auroc, 3))

Styling: ``plot_params`` (a dict, pylbsr-style) and ``**plot_kwargs`` are both passed
to ``Axes.plot``; explicit keyword arguments win over ``plot_params`` on conflict.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

_DEFAULT_ROC_PARAMS = {"alpha": 1.0, "color": "#6a0019"}  # same defaults as pylbsr
_BASELINE_STYLE = {"linestyle": "--", "color": "#888888", "lw": 1.0}


def _new_axes(ax: Axes | None) -> tuple[Figure | None, Axes]:
    if ax is not None:
        return None, ax
    fig = plt.figure(figsize=(7, 7))
    return fig, fig.add_subplot(1, 1, 1)


@dataclass(frozen=True)
class Curve:
    """One method's exported ROC + PRC curve and its metadata."""

    name: str
    family: str | None
    window: str | None
    variant: str | None
    auroc: float
    auprc: float
    n_pos: int
    n_neg: int
    random_clf: float
    fpr: np.ndarray = field(repr=False)
    tpr: np.ndarray = field(repr=False)
    precision: np.ndarray = field(repr=False)
    recall: np.ndarray = field(repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Curve:
        arrays = {
            k: np.asarray(d[k], dtype=np.float64) for k in ("fpr", "tpr", "precision", "recall")
        }
        return cls(
            name=d["name"],
            family=d.get("family"),
            window=d.get("window"),
            variant=d.get("variant"),
            auroc=float(d["auroc"]),
            auprc=float(d["auprc"]),
            n_pos=int(d["n_pos"]),
            n_neg=int(d["n_neg"]),
            random_clf=float(d["random_clf"]),
            **arrays,
        )

    def plot_roc(
        self, ax: Axes | None = None, plot_params: dict[str, Any] | None = None, **plot_kwargs
    ) -> tuple[Figure | None, Axes]:
        """Draw the ROC curve (fpr vs tpr). Returns ``(fig, ax)``; ``fig`` is None when
        ``ax`` was given. Does not touch labels/limits -- see ``format_roc_axes``."""
        fig, ax = _new_axes(ax)
        params = {**_DEFAULT_ROC_PARAMS, **(plot_params or {}), **plot_kwargs}
        ax.plot(self.fpr, self.tpr, **params)
        return fig, ax

    def plot_prc(
        self,
        ax: Axes | None = None,
        plot_params: dict[str, Any] | None = None,
        baseline: bool = False,
        **plot_kwargs,
    ) -> tuple[Figure | None, Axes]:
        """Draw the precision-recall curve (recall vs precision). ``baseline=True`` also
        draws this curve's no-skill line (``random_clf``), as pylbsr's
        ``PRCresults.plot`` always does; off by default here because overlays of many
        curves on one dataset share one baseline (see ``format_prc_axes``)."""
        fig, ax = _new_axes(ax)
        params = {**_DEFAULT_ROC_PARAMS, **(plot_params or {}), **plot_kwargs}
        ax.plot(self.recall, self.precision, **params)
        if baseline:
            ax.axhline(self.random_clf, **_BASELINE_STYLE)
        return fig, ax


@dataclass
class CurveSet:
    """All exported curves of one dataset, in export order."""

    dataset: str
    display_name: str
    build_date: str
    curves: list[Curve]
    missing_methods: list[str] = field(default_factory=list)
    label_source: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: str | Path) -> CurveSet:
        with open(path) as f:
            d = json.load(f)
        if d.get("schema_version", 1) != 1:
            raise ValueError(f"{path}: unsupported schema_version {d.get('schema_version')!r}")
        return cls(
            dataset=d["dataset"],
            display_name=d.get("display_name", d["dataset"]),
            build_date=d["build_date"],
            curves=[Curve.from_dict(m) for m in d["methods"]],
            missing_methods=list(d.get("missing_methods", [])),
            label_source=d.get("label_source", {}),
        )

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.curves]

    def get(self, name: str) -> Curve:
        for c in self.curves:
            if c.name == name:
                return c
        hint = " (exported with no data)" if name in self.missing_methods else ""
        raise KeyError(f"{name!r} not in {self.dataset!r}{hint}")

    def filter(self, family: str | None = None, window: str | None = None) -> list[Curve]:
        """Curves matching every given metadata field (None = no constraint)."""
        return [
            c
            for c in self.curves
            if (family is None or c.family == family) and (window is None or c.window == window)
        ]

    def __iter__(self) -> Iterator[Curve]:
        return iter(self.curves)

    def __len__(self) -> int:
        return len(self.curves)

    @property
    def n_pos(self) -> int:
        """Positives of the largest-coverage method (methods can differ when a scorer
        has missing values for some variants)."""
        return max(c.n_pos for c in self.curves)

    @property
    def n_neg(self) -> int:
        return max(c.n_neg for c in self.curves)


def format_roc_axes(ax: Axes, diagonal: bool = True, equal_aspect: bool = True) -> Axes:
    """Standard ROC axes: chance diagonal, [0, 1] limits, labels, equal aspect.

    Pass ``equal_aspect=False`` for axes placed by plotplate: forcing the aspect shrinks
    the axes out of their layout box (``axes-moved`` check). Make the box square in
    ``layout.yaml`` instead."""
    if diagonal:
        ax.plot([0, 1], [0, 1], **_BASELINE_STYLE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.01)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    return ax


def format_prc_axes(ax: Axes, baseline: float | None = None, equal_aspect: bool = True) -> Axes:
    """Standard PRC axes: optional no-skill line at ``baseline``, [0, 1] limits,
    labels, equal aspect (see ``format_roc_axes`` for ``equal_aspect``)."""
    if baseline is not None:
        ax.axhline(baseline, **_BASELINE_STYLE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.01)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    return ax
