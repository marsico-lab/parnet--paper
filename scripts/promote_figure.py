"""Copy the latest build of one figure into its tracked final/ folder, with the deliverables.

    pixi run promote main_mutations                          # Overleaf folder figures/<name>/
    pixi run promote main_mutations Figures/Figure_7/        # another Overleaf folder

Run it when the figure is the version you want to share; then commit final/.
The build writes its files into figures/<name>/output/, which git ignores.

figures/<name>/final/
  page.pdf/png/svg        the figure on its A4 page (PNG at 600 dpi)
  panels/                 one PDF, SVG and PNG per panel
  <name>.pdf              the figure in one vector file (plotplate export)
  <name>.svg              the same figure as one SVG file, text kept as text
  overleaf/               files to upload to the figure folder in Overleaf
  promoted.yaml           when, from which commit and which layout

Refuses to promote a figure whose check reports errors.
While panels are still missing (work in progress), it promotes the page view and the panels,
skips the deliverables (<name>.pdf, <name>.svg, overleaf/), and says so in promoted.yaml.
"""

import datetime
import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pymupdf
from page_png import render

REPO = Path(__file__).resolve().parents[1]
COPIED = ["page.pdf", "page.png", "page.svg"]  # in the figure's output/ folder


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True, cwd=REPO).stdout


def main(name: str, overleaf_dir: str = "") -> None:
    figure = REPO / "figures" / name
    layout = figure / "layout.yaml"
    if not layout.exists():
        sys.exit(f"No figures/{name}/layout.yaml.")
    output = figure / "output"
    missing = [f for f in COPIED if not (output / f).exists()]
    if missing:
        sys.exit(f"Build the figure first (pixi run figure {name}); missing: {', '.join(missing)}")
    check = subprocess.run(
        ["plotplate", "check", str(figure)], cwd=REPO, text=True, capture_output=True, check=False
    )
    if check.returncode != 0:
        sys.exit(f"plotplate check reports errors; not promoted.\n{check.stdout}")

    # Before final/ is rewritten: its own new files are not uncommitted changes of the figure.
    dirty = run(
        "git", "status", "--porcelain", "--untracked-files=no", "--", f"figures/{name}"
    ).strip()
    final = figure / "final"
    shutil.rmtree(final, ignore_errors=True)
    final.mkdir()
    for f in COPIED:
        shutil.copy2(output / f, final / f)
    render(final / "page.pdf", final / "page.png")  # 600 dpi, whatever the build wrote
    shutil.copytree(output / "panels", final / "panels")

    missing_panels = sorted(
        line.split("panel ")[1].split(":")[0]
        for line in check.stdout.splitlines()
        if "panel-missing" in line
    )
    if not missing_panels:
        pdf = final / f"{name}.pdf"
        run("plotplate", "export", str(figure), "-o", str(pdf))
        with pymupdf.open(pdf) as doc:
            if doc.page_count != 1:
                sys.exit(f"{pdf.name} has {doc.page_count} pages; expected 1.")
            (final / f"{name}.svg").write_text(doc[0].get_svg_image(text_as_path=False))
        prefix = ["--prefix", overleaf_dir.rstrip("/") + "/"] if overleaf_dir else []
        run("plotplate", "latex", str(figure), str(final / "overleaf"), *prefix)

    (final / "promoted.yaml").write_text(
        f"date: {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}\n"
        f"commit: {run('git', 'rev-parse', '--short', 'HEAD').strip()}\n"
        f"uncommitted_changes: {'true' if dirty else 'false'}\n"
        f"layout: {layout.resolve().name}\n"
        f"plotplate: {version('plotplate')}\n"
        f"overleaf_dir: {overleaf_dir or f'figures/{name}/'}\n"
        f"missing_panels: [{', '.join(missing_panels)}]\n"
        f"deliverables: {'false' if missing_panels else 'true'}\n"
    )
    note = (
        f"; panels {', '.join(missing_panels)} missing, no PDF/SVG/Overleaf yet"
        if missing_panels
        else ""
    )
    print(
        f"Promoted figures/{name}/final/ (layout {layout.resolve().name}{note}). Commit it to share it."
    )


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
