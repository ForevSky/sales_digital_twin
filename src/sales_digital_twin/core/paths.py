"""项目路径工具：避免 CLI 依赖当前工作目录。"""

from pathlib import Path


def project_root() -> Path:
    """返回仓库根目录（含 examples/、outputs/ 的目录）。"""

    # core/paths.py → core → sales_digital_twin → src → 项目根

    return Path(__file__).resolve().parents[3]


def examples_dir() -> Path:

    return project_root() / "examples"


def outputs_dir() -> Path:

    return project_root() / "outputs"
