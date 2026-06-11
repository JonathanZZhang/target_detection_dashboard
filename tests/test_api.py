"""测试 API 端点 —— 端到端验证响应格式和筛选逻辑。

注意：这些测试直接调用真实 CSV（data/sample_data.csv），
共 36,000 行数据，已验证约 0.1s 跑完全部。
"""

import pytest
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════
# GET /api/filters
# ═══════════════════════════════════════════════════

class TestFiltersEndpoint:
    """GET /api/filters"""

    def test_returns_200(self, client):
        r = client.get("/api/filters")
        assert r.status_code == 200

    def test_returns_json_keys(self, client):
        r = client.get("/api/filters")
        data = r.json()
        assert "targets" in data
        assert "time_min" in data
        assert "time_max" in data

    def test_targets_is_non_empty_list(self, client):
        r = client.get("/api/filters")
        data = r.json()
        assert isinstance(data["targets"], list)
        assert len(data["targets"]) >= 1

    def test_targets_are_sorted(self, client):
        r = client.get("/api/filters")
        targets = r.json()["targets"]
        assert targets == sorted(targets)

    def test_time_range_is_valid(self, client):
        r = client.get("/api/filters")
        data = r.json()
        assert data["time_min"] <= data["time_max"]


# ═══════════════════════════════════════════════════
# GET /api/heatmap
# ═══════════════════════════════════════════════════

class TestHeatmapEndpoint:
    """GET /api/heatmap"""

    def test_returns_200_with_default_params(self, client):
        r = client.get("/api/heatmap")
        assert r.status_code == 200

    def test_response_format(self, client):
        r = client.get("/api/heatmap")
        data = r.json()
        assert "times" in data
        assert "counts" in data
        assert isinstance(data["times"], list)
        assert isinstance(data["counts"], list)
        assert len(data["times"]) == len(data["counts"])

    def test_times_and_counts_same_length(self, client):
        r = client.get("/api/heatmap")
        data = r.json()
        assert len(data["times"]) == len(data["counts"])

    def test_counts_are_positive(self, client):
        r = client.get("/api/heatmap")
        data = r.json()
        assert all(c > 0 for c in data["counts"])

    def test_target_filter_works(self, client):
        r = client.get("/api/heatmap?targets=Target_A&targets=Target_B")
        data = r.json()
        # 有数据时应返回非空 array
        assert len(data["times"]) > 0
        assert sum(data["counts"]) > 0

    def test_time_bucket_coarser_gives_fewer_bins(self, client):
        """10s 桶应比 1s 桶更少分箱。"""
        r1 = client.get("/api/heatmap?time_bucket=1s")
        r60 = client.get("/api/heatmap?time_bucket=60s")
        assert len(r1.json()["times"]) > len(r60.json()["times"])

    def test_returns_empty_for_empty_target(self, client):
        r = client.get("/api/heatmap?targets=NoSuchTarget")
        data = r.json()
        assert data["times"] == []
        assert data["counts"] == []


# ═══════════════════════════════════════════════════
# GET /api/scatter
# ═══════════════════════════════════════════════════

class TestScatterEndpoint:
    """GET /api/scatter"""

    def test_returns_200(self, client):
        r = client.get("/api/scatter")
        assert r.status_code == 200

    def test_response_format(self, client):
        r = client.get("/api/scatter")
        data = r.json()
        assert "times" in data
        assert "counts" in data
        assert len(data["times"]) == len(data["counts"])


# ═══════════════════════════════════════════════════
# GET /api/scatter_density
# ═══════════════════════════════════════════════════

class TestScatterDensityEndpoint:
    """GET /api/scatter_density"""

    def test_returns_200(self, client):
        r = client.get("/api/scatter_density")
        assert r.status_code == 200

    def test_response_format(self, client):
        r = client.get("/api/scatter_density")
        data = r.json()
        assert "points" in data
        assert isinstance(data["points"], list)
        # 每个 point 是 [total, unique, total, time_bin]
        if data["points"]:
            p = data["points"][0]
            assert len(p) == 4
            assert isinstance(p[0], int)  # total
            assert isinstance(p[1], int)  # unique
            assert isinstance(p[2], int)  # total
            assert isinstance(p[3], str)  # time_bin

    def test_unique_le_total(self, client):
        """unique 数量 ≤ total 数量。"""
        r = client.get("/api/scatter_density")
        for p in r.json()["points"]:
            assert p[1] <= p[0], f"unique({p[1]}) > total({p[0]}) at {p[3]}"


# ═══════════════════════════════════════════════════
# GET /api/bbox_heatmap
# ═══════════════════════════════════════════════════

class TestBboxHeatmapEndpoint:
    """GET /api/bbox_heatmap"""

    def test_returns_200(self, client):
        r = client.get("/api/bbox_heatmap")
        assert r.status_code == 200

    def test_response_format(self, client):
        r = client.get("/api/bbox_heatmap")
        data = r.json()
        assert "rects" in data
        assert isinstance(data["rects"], list)
        if data["rects"]:
            rct = data["rects"][0]
            assert len(rct) == 6  # x1, y1, x2, y2, target, time_stamp
            assert all(isinstance(v, int) for v in rct[:4])  # 坐标是 int
            assert isinstance(rct[4], str)  # target
            assert isinstance(rct[5], str)  # time_stamp

    def test_coordinates_in_range(self, client):
        """坐标在画布范围内。"""
        r = client.get("/api/bbox_heatmap")
        for rct in r.json()["rects"][:100]:  # 抽检 100 条
            assert 0 <= rct[0] <= 1920, f"x1={rct[0]} out of range"
            assert 0 <= rct[1] <= 1080, f"y1={rct[1]} out of range"

    def test_target_filter_reduces_results(self, client):
        r_all = client.get("/api/bbox_heatmap")
        r_filtered = client.get("/api/bbox_heatmap?targets=Target_A")
        assert len(r_filtered.json()["rects"]) < len(r_all.json()["rects"])

    def test_time_range_filters_results(self, client):
        r_all = client.get("/api/bbox_heatmap")
        r_time = client.get("/api/bbox_heatmap?time_start=00:30:00&time_end=00:31:00")
        assert len(r_time.json()["rects"]) <= len(r_all.json()["rects"])


# ═══════════════════════════════════════════════════
# 快速冒烟 —— 所有端点可访问
# ═══════════════════════════════════════════════════

@pytest.mark.parametrize("path", [
    "/api/filters",
    "/api/heatmap",
    "/api/scatter",
    "/api/scatter_density",
    "/api/bbox_heatmap",
])
def test_all_endpoints_200(client, path):
    """冒烟：全部端点返回 200。"""
    assert client.get(path).status_code == 200
