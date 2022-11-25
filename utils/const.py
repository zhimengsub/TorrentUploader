from pathlib import Path

from httpx import URL

__all__ = ["BANGUMI_MOE_HOST", "PROJECT_ROOT"]

BANGUMI_MOE_HOST = URL("https://bangumi.moe/")
"""萌番组的 host"""

PROJECT_ROOT = Path(__file__).joinpath("../../").resolve()
"""项目根路径"""
