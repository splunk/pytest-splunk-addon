import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[2]
UNSAFE_CIM_INSTALL = re.compile(r"\bpip(?:3)?\s+install\s+splunk-cim-models(?:\s|$)")


def test_public_docs_do_not_install_cim_models_from_pypi():
    matches = []

    for documentation_file in (REPOSITORY_ROOT / "docs").rglob("*.md"):
        content = documentation_file.read_text()
        if UNSAFE_CIM_INSTALL.search(content):
            matches.append(str(documentation_file.relative_to(REPOSITORY_ROOT)))

    assert not matches, (
        "Public documentation must not install splunk-cim-models from PyPI: "
        + ", ".join(matches)
    )
