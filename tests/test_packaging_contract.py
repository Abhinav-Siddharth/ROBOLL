from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_editable_install_declares_execution_and_analysis_dependencies():
    config = tomllib.loads((ROOT/'pyproject.toml').read_text())
    deps = config['project'].get('dependencies', [])
    names = {d.split('>')[0].split('=')[0].split('[')[0].lower() for d in deps}
    assert {'ollama', 'pydantic', 'pyyaml', 'tqdm', 'numpy', 'pandas',
            'matplotlib', 'jsonschema'} <= names


def test_readme_distinguishes_stage_one_pilot_from_archived_pilot():
    readme = (ROOT/'README.md').read_text()
    assert 'stage 1 only' in readme
    assert '165' in readme and '330' in readme
