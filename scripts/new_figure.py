"""Create figures/<name>/ as a copy of figures/_example/ that builds immediately.

    pixi run new-figure main_mutations

Then replace the example panels, data and assets with the real ones (figures/README.md).
"""

import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "figures" / "_example"
GENERATED = ["panels", "preview.pdf", "preview.png", "preview.svg", "_example.tex"]
TEXT_SUFFIXES = {".md", ".py", ".smk", ".tex", ".yaml"}


def main(name: str) -> None:
    if not re.fullmatch(r"(main|supp)_[a-z0-9_]+", name):
        sys.exit(f"Name must look like main_<topic> or supp_<topic> (lowercase, digits, _): {name!r}")
    target = REPO / "figures" / name
    if target.exists():
        sys.exit(f"{target.relative_to(REPO)} already exists.")
    shutil.copytree(EXAMPLE, target, ignore=shutil.ignore_patterns(*GENERATED, "__pycache__"))
    for path in sorted(target.rglob("*")):
        if "_example" in path.name:  # _example-figure.tex -> <name>-figure.tex
            path = path.rename(path.with_name(path.name.replace("_example", name)))
        if path.suffix in TEXT_SUFFIXES:
            text = path.read_text()
            text = text.replace("example_scores", f"{name}_scores").replace("_example", name)
            text = text.replace("# Example figure", f"# {name}").replace("Example figure", name)
            path.write_text(text)
    branch = "figure/" + name.replace("_", "-")
    print(f"Created figures/{name}/ (a copy of the example).")
    print(f"Branch for this figure: {branch}")
    print(f"Build it now: pixi run figure {name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
