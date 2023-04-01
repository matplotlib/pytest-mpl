import os
import shutil
import pathlib
import tempfile
import subprocess

from docutils import nodes
from sphinx.util.docutils import SphinxRole
from sphinx.util.osutil import canon_path

REPO_ROOT = pathlib.Path(__file__).parent.parent
TEST_FILE = REPO_ROOT / "tests" / "subtests" / "test_subtest.py"
SAMPLE_DIR = "sample"


def run_pytest(test_name):

    # Create generated samples directory
    sample_dir_abs = pathlib.Path(__file__).parent / SAMPLE_DIR
    if not sample_dir_abs.exists():
        os.mkdir(sample_dir_abs)

    # Form path to current sample
    dest = sample_dir_abs / test_name
    if dest.exists():
        return dest  # skip if already generated

    # Generate the current sample
    tmp_dir = tempfile.mkdtemp()
    command = f"python -m pytest {TEST_FILE}::{test_name} -v --mpl --basetemp={tmp_dir}"
    subprocess.run(command, shell=True, check=True)

    # Find the name of the directory the sample is within
    # (directory name is sometimes truncated)
    src = next(filter(
        lambda x: x.name[:-1] in test_name,
        pathlib.Path(tmp_dir).glob("*0")
    )) / "results"
    shutil.copytree(src, dest)

    return dest


class SummaryButtons(nodes.General, nodes.Inline, nodes.TextElement):
    pass


class SummaryRole(SphinxRole):
    def run(self):
        node = SummaryButtons(name=self.text)
        return [node], []


def move_summaries(app, *args, **kwargs):
    gen_sample_dir = pathlib.Path(__file__).parent / SAMPLE_DIR
    out_sample_dir = pathlib.Path(app.outdir) / SAMPLE_DIR
    if out_sample_dir.exists():
        shutil.rmtree(out_sample_dir)
    shutil.copytree(gen_sample_dir, out_sample_dir)


def html_visit_summary(self, node):

    test_name = str(node["name"])
    out = run_pytest(test_name)

    classes = (
        "sd-sphinx-override sd-btn sd-text-wrap sd-btn-{importance} "
        "sd-shadow-sm sd-me-2 reference internal"
    )
    button = (
        '<a class="{classes}" href="{href}" style="margin-right: 0.5rem;">{label}</a>'
    )

    summary_types = {
        "HTML": "fig_comparison.html",
        "Basic HTML": "fig_comparison_basic.html",
        "JSON": "results.json",
    }

    current_filename = self.builder.current_docname + self.builder.out_suffix
    current_dir = pathlib.PurePath(current_filename).parent
    first_button = True
    for label, file in summary_types.items():
        if (out / file).exists():
            importance = "primary" if first_button else "secondary"
            self.body.append(button.format(
                classes=classes.format(importance=importance),
                href=canon_path((current_dir / SAMPLE_DIR / test_name / file).as_posix()),
                label=label,
            ))
            first_button = False

    raise nodes.SkipNode


def skip(self, node):
    raise nodes.SkipNode


def setup(app):
    app.connect("build-finished", move_summaries)
    app.add_node(
        SummaryButtons,
        html=(html_visit_summary, None),
        latex=(skip, None),
        text=(skip, None),
        man=(skip, None),
        texinfo=(skip, None),
    )
    app.add_role("summary", SummaryRole())
    return {"parallel_read_safe": True, "parallel_write_safe": True}
