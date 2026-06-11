"""测试 main.py 中的纯函数：_filter, _bin_time。"""

import pandas as pd
import pytest

from main import _filter, _bin_time


# ═══════════════════════════════════════════════════
# _filter
# ═══════════════════════════════════════════════════

class TestFilter:
    """_filter(df, targets, time_start, time_end)"""

    def test_no_filter_returns_all(self, sample_df):
        """不传任何过滤条件，返回原 DataFrame。"""
        result = _filter(sample_df, None, None, None)
        assert len(result) == len(sample_df)

    def test_filter_by_single_target(self, sample_df):
        """按单个目标过滤。"""
        result = _filter(sample_df, targets=["Target_A"], time_start=None, time_end=None)
        assert len(result) == 4
        assert (result["target"] == "Target_A").all()

    def test_filter_by_multiple_targets(self, sample_df):
        """按多个目标过滤。"""
        result = _filter(sample_df, targets=["Target_A", "Target_B"], time_start=None, time_end=None)
        assert len(result) == 7  # Target_A 4 条 + Target_B 3 条
        assert result["target"].isin(["Target_A", "Target_B"]).all()

    def test_filter_by_time_start(self, sample_df):
        """过滤起始时间。"""
        result = _filter(sample_df, targets=None, time_start="00:00:08", time_end=None)
        assert len(result) == 5  # 00:00:08 ~ 00:00:12

    def test_filter_by_time_end(self, sample_df):
        """过滤结束时间。"""
        result = _filter(sample_df, targets=None, time_start=None, time_end="00:00:03")
        assert len(result) == 3  # 00:00:01 ~ 00:00:03

    def test_filter_by_time_range(self, sample_df):
        """同时过滤起止时间。"""
        result = _filter(sample_df, targets=None, time_start="00:00:04", time_end="00:00:07")
        assert len(result) == 4  # 4,5,6,7

    def test_filter_combined_target_and_time(self, sample_df):
        """目标 + 时间组合过滤。"""
        result = _filter(sample_df, targets=["Target_C"], time_start="00:00:09", time_end=None)
        assert len(result) == 4  # 00:00:09 ~ 00:00:12 全部是 Target_C
        assert (result["target"] == "Target_C").all()

    def test_filter_empty_target_list_returns_all(self, sample_df):
        """空列表不过滤。"""
        result = _filter(sample_df, targets=[], time_start=None, time_end=None)
        assert len(result) == len(sample_df)


# ═══════════════════════════════════════════════════
# _bin_time
# ═══════════════════════════════════════════════════

class TestBinTime:
    """_bin_time(df, bucket)"""

    def test_adds_time_bin_column(self, sample_df):
        """添加 time_bin 列。"""
        result = _bin_time(sample_df.copy(), "1s")
        assert "time_bin" in result.columns

    def test_bucket_1s_keeps_original(self, sample_df):
        """1s 桶 —— 时间不变。"""
        result = _bin_time(sample_df.copy(), "1s")
        assert result["time_bin"].tolist() == sample_df["time_stamp"].tolist()

    def test_bucket_10s_floors_correctly(self):
        """10s 桶 —— 向下取整到整十秒。"""
        df = pd.DataFrame({"time_stamp": ["00:00:03", "00:00:09", "00:00:11", "00:00:18"]})
        result = _bin_time(df.copy(), "10s")
        assert result["time_bin"].tolist() == [
            "00:00:00",  # 3s floor → 0s
            "00:00:00",  # 9s floor → 0s
            "00:00:10",  # 11s floor → 10s
            "00:00:10",  # 18s floor → 10s
        ]

    def test_bucket_1min_floors_correctly(self):
        """1min 桶。"""
        df = pd.DataFrame({"time_stamp": ["00:00:30", "00:01:15", "00:02:59"]})
        result = _bin_time(df.copy(), "1min")
        assert result["time_bin"].tolist() == [
            "00:00:00",
            "00:01:00",
            "00:02:00",
        ]

    def test_does_not_mutate_original_time_stamp(self, sample_df):
        """不修改原始 time_stamp 列。"""
        original = sample_df["time_stamp"].tolist()
        _bin_time(sample_df.copy(), "60s")
        assert sample_df["time_stamp"].tolist() == original
