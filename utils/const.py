from pathlib import Path

from httpx import URL

__all__ = ["BANGUMI_MOE_HOST", "PROJECT_ROOT"]

BANGUMI_MOE_HOST = URL("https://bangumi.moe/")
"""萌番组的 host"""

PROJECT_ROOT = Path(__file__).joinpath("../../").resolve()
"""项目根路径"""

PAPER_URL_LIST = [
    "https://img30.360buyimg.com/imgzone/jfs/t1/141321/32/30637/399120/635daaaeE1c14939e/d56dc1fb1c06bed4.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/194323/15/29098/455067/63617fb5E79492895/be71c93b2b842968.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/116049/9/31514/504922/636b06eeEd16a427c/7b3ec2475ad9ee0d.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/201963/39/28559/466297/636b07c8E7b4b82ad/e899ca88376f1867.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/145383/23/31455/448895/636b5937E54ba77cf/17ae3799c6b9f78c.png",
]
"""字幕组海报的链接"""
