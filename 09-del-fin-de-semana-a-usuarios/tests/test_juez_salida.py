"""Tests for the exit judge pieces that do not need a real project: secret scanner and the README check."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "salida"))
import buscar_secretos  # noqa: E402
import juez_salida  # noqa: E402


def git_init(folder: Path):
    subprocess.run(["git", "init", "-q"], cwd=folder, check=True)


def test_scanner_passes_a_clean_folder(tmp_path):
    git_init(tmp_path)
    (tmp_path / ".gitignore").write_text(".env\n")
    (tmp_path / "app.py").write_text("print('hola')\n")
    assert buscar_secretos.scan(tmp_path)["hallazgos"] == []


def test_scanner_finds_a_google_key(tmp_path):
    git_init(tmp_path)
    (tmp_path / ".gitignore").write_text(".env\n")
    (tmp_path / "config.ts").write_text('const k = "AIza' + "x" * 35 + '";\n')
    found = buscar_secretos.scan(tmp_path)["hallazgos"]
    assert found and found[0]["archivo"] == "config.ts"


def test_scanner_flags_a_missing_env_ignore(tmp_path):
    git_init(tmp_path)
    (tmp_path / ".gitignore").write_text("node_modules\n")
    assert buscar_secretos.scan(tmp_path)["env_ignorado"] is False


def test_scanner_flags_a_versionable_env_file(tmp_path):
    git_init(tmp_path)
    (tmp_path / ".env").write_text("FOO=bar\n")
    assert ".env" in buscar_secretos.scan(tmp_path)["env_versionado"]


def test_rollback_section_needs_a_command(tmp_path):
    (tmp_path / "README.md").write_text("# App\n\n## Cómo volver atrás\n\nSe vuelve a la versión anterior.\n")
    assert juez_salida.check_7({}, tmp_path)[0] is False
    (tmp_path / "README.md").write_text("# App\n\n## Cómo volver atrás\n\n```bash\ngit revert HEAD\n```\n")
    assert juez_salida.check_7({}, tmp_path)[0] is True


def test_rollback_section_missing(tmp_path):
    (tmp_path / "README.md").write_text("# App\n")
    assert juez_salida.check_7({}, tmp_path)[0] is False
