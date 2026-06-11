"""共享 fixtures。"""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """FastAPI TestClient —— 每个测试独立实例。"""
    return TestClient(app)


@pytest.fixture
def sample_df():
    """内存 DataFrame，模拟 sample_data.csv 的子集。

    列与 CSV 完全一致：time_stamp, target, x1, y1, x2, y2
    """
    return pd.DataFrame({
        "time_stamp": [
            "00:00:01", "00:00:02", "00:00:03", "00:00:04", "00:00:05",
            "00:00:06", "00:00:07", "00:00:08", "00:00:09", "00:00:10",
            "00:00:11", "00:00:12",
        ],
        "target": [
            "Target_A", "Target_A", "Target_B", "Target_B", "Target_C",
            "Target_A", "Target_A", "Target_B", "Target_C", "Target_C",
            "Target_C", "Target_C",
        ],
        "x1":  [100, 200, 300, 400, 500,  110, 210, 310, 510, 520, 530, 540],
        "y1":  [600, 700, 800, 900, 1000, 610, 710, 810, 1010, 1020, 1030, 1040],
        "x2":  [150, 250, 350, 450, 550,  160, 260, 360, 560, 570, 580, 590],
        "y2":  [650, 750, 850, 950, 1050, 660, 760, 860, 1060, 1070, 1080, 1090],
    })
