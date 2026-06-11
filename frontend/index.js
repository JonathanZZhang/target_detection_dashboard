// ══════════════════════════════════════════════════════
// 图表配置（等价于 templates/*.toml）
// ══════════════════════════════════════════════════════
const CONFIG = {
    heatmap: {
        container: { width: null, height: 200 },
        title: { text: "单轴时间热力图" },
        visualmap: {
            orient: "horizontal", itemWidth: 20, itemHeight: 200,
            rangeColor: ["green", "yellow", "orange", "red"],
            posLeft: "right", posTop: "top",
        },
        xAxis: { axisLabel: { rotate: -45, fontSize: 10 } },
        dataZoom: { type: "slider", start: 0, end: 100 },
    },
    scatter: {
        container: { width: null, height: 200 },
        title: { text: "单轴时间散点图" },
        visualmap: {
            orient: "horizontal", posLeft: "right", posTop: "top",
            rangeSize: [3, 40], sizeBase: 10,
        },
        dataZoom: { type: "slider", start: 0, end: 100 },
    },
    scatter_density: {
        container: { width: null, height: 540 },
        title: { text: "二维散点密度图" },
        symbol: { sizeBase: 20, scaleSize: true, rangeSize: [10, 70] },
        visualmapColor: { orient: "vertical", posLeft: "left", posTop: "center",
            rangeColor: ["blue", "cyan", "yellow", "red"] },
        visualmapSize: { show: true, orient: "vertical", posRight: "right", posTop: "center",
            rangeSize: [10, 70] },
        xAxis: { name: "目标频次" },
        yAxis: { name: "目标多样性" },
        grid: { show: true },
    },
    bbox: {
        canvas: { width: 1920, height: 1080 },
        container: { width: null, height: 540 },
        title: { text: "二维矩形覆盖图" },
        rectStyle: { fill: "rgba(200,40,40,0.12)", stroke: "rgba(180,30,30,0.30)", lineWidth: 0.5 },
        xAxis: { name: "X (px)" },
        yAxis: { name: "Y (px)" },
    },
};

// ══════════════════════════════════════════════════════
// ECharts option 构建器
// ══════════════════════════════════════════════════════
function buildHeatmapOption(data, cfg) {
    var v = cfg.visualmap;
    var max = data.counts.length ? Math.max.apply(null, data.counts) : 100;
    return {
        title: [{ text: cfg.title.text, left: "center" }],
        xAxis: [{ type: "category", data: data.times, axisLabel: cfg.xAxis.axisLabel }],
        yAxis: [{ show: false, data: [""] }],
        visualMap: {
            show: true, type: "continuous", calculable: true,
            min: 0, max: max,
            orient: v.orient, itemWidth: v.itemWidth, itemHeight: v.itemHeight,
            left: v.posLeft, top: v.posTop,
            inRange: { color: v.rangeColor },
        },
        dataZoom: [{ type: cfg.dataZoom.type, start: cfg.dataZoom.start, end: cfg.dataZoom.end }],
        series: [{ type: "heatmap", data: data.counts.map(function(c, i) { return [i, 0, c]; }) }],
        tooltip: { show: true },
    };
}

function buildScatterOption(data, cfg) {
    var v = cfg.visualmap;
    var max = data.counts.length ? Math.max.apply(null, data.counts) : 100;
    return {
        title: [{ text: cfg.title.text, left: "center" }],
        xAxis: [{ type: "category", data: data.times, boundaryGap: false,
                    axisLabel: { rotate: -45, fontSize: 10 } }],
        yAxis: [{ show: false, data: [""] }],
        visualMap: {
            show: true, type: "continuous", calculable: true, dimension: 2,
            min: 0, max: max,
            orient: v.orient, left: v.posLeft, top: v.posTop,
            inRange: { symbolSize: v.rangeSize },
        },
        dataZoom: [{ type: cfg.dataZoom.type, start: cfg.dataZoom.start, end: cfg.dataZoom.end }],
        series: [{
            type: "scatter",
            data: data.counts.map(function(c, i) { return [i, 0, c, data.times[i]]; }),
            symbolSize: function(d) { return Math.max(3, d[2] * (v.sizeBase / 10)); },
        }],
        tooltip: {
            show: true,
            formatter: function(p) { return '时间: ' + p.data[3] + '<br/>数量: ' + p.data[2]; },
        },
    };
}

function buildDensityOption(data, cfg) {
    var s = cfg.symbol;
    var max = 0;
    data.points.forEach(function(p) { if (p[2] > max) max = p[2]; });
    var vmList = [{
        show: true, type: "continuous", calculable: true, dimension: 2,
        min: 1, max: max,
        orient: cfg.visualmapColor.orient,
        left: cfg.visualmapColor.posLeft, top: cfg.visualmapColor.posTop,
        inRange: { color: cfg.visualmapColor.rangeColor },
    }];
    if (cfg.visualmapSize.show && s.scaleSize) {
        vmList.push({
            show: true, type: "continuous", calculable: true, dimension: 2,
            min: 1, max: max,
            orient: cfg.visualmapSize.orient,
            right: cfg.visualmapSize.posRight, top: cfg.visualmapSize.posTop,
            inRange: { symbolSize: cfg.visualmapSize.rangeSize },
        });
    }
    return {
        title: [{ text: cfg.title.text, left: "center" }],
        xAxis: [{ type: "value", name: cfg.xAxis.name,
                    splitLine: { show: cfg.grid.show, lineStyle: { color: "#e0e0e0", type: "dashed" } } }],
        yAxis: [{ type: "value", name: cfg.yAxis.name,
                    splitLine: { show: cfg.grid.show, lineStyle: { color: "#e0e0e0", type: "dashed" } } }],
        visualMap: vmList,
        series: [{
            type: "scatter", data: data.points,
            symbolSize: s.scaleSize ? s.sizeBase : s.sizeBase,
            label: { show: false },
        }],
        tooltip: {
            show: true,
            formatter: function(p) { return '总次数: ' + p.data[0] + '<br/>去重目标: ' + p.data[1] + '<br/>频次: ' + p.data[2]; },
        },
    };
}

function buildBboxOption(data, cfg) {
    var c = cfg.canvas;
    var rs = cfg.rectStyle;
    return {
        title: [{ text: cfg.title.text, left: "center" }],
        xAxis: { type: "value", min: 0, max: c.width, name: cfg.xAxis.name,
                    splitLine: { show: true, lineStyle: { color: "#e0e0e0", type: "dashed" } } },
        yAxis: { type: "value", min: 0, max: c.height, name: cfg.yAxis.name,
                    splitLine: { show: true, lineStyle: { color: "#e0e0e0", type: "dashed" } } },
        series: [{
            type: "custom", coordinateSystem: "cartesian2d", clip: true,
            data: data.rects,
            renderItem: function(params, api) {
                var x1 = api.coord([api.value(0), api.value(1)])[0];
                var y1 = api.coord([api.value(0), api.value(1)])[1];
                var x2 = api.coord([api.value(2), api.value(3)])[0];
                var y2 = api.coord([api.value(2), api.value(3)])[1];
                return {
                    type: "rect",
                    shape: { x: Math.min(x1, x2), y: Math.min(y1, y2),
                                width: Math.abs(x2 - x1) || 1, height: Math.abs(y2 - y1) || 1 },
                    style: { fill: rs.fill, stroke: rs.stroke, lineWidth: rs.lineWidth },
                };
            },
        }],
        tooltip: {
            show: true,
            formatter: function(p) { return '目标: ' + p.data[4] + '<br/>时间: ' + p.data[5]
                + '<br/>x1=' + p.data[0] + ', y1=' + p.data[1] + ', x2=' + p.data[2] + ', y2=' + p.data[3]; },
        },
    };
}

// ══════════════════════════════════════════════════════
// 全局状态 & 初始化
// ══════════════════════════════════════════════════════
const charts = {};
const API = ""; //有必要吗？

async function init() {
    var res = await fetch(API + "/api/filters");
    var filters = await res.json();

    var chipsEl = document.getElementById("target-chips");
    filters.targets.forEach(function(target, i) {
        var label = document.createElement("label");
        label.className = "target-chip inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border " +
            (i < 4 ? "bg-blue-50 border-blue-300 text-blue-700" : "bg-white border-slate-300 text-slate-500");
        var cb = document.createElement("input");
        cb.type = "checkbox"; cb.value = target; cb.checked = i < 4; cb.className = "sr-only peer";
        cb.addEventListener("change", function() {
            label.classList.toggle("bg-blue-50"); label.classList.toggle("border-blue-300");
            label.classList.toggle("text-blue-700"); label.classList.toggle("bg-white");
            label.classList.toggle("border-slate-300"); label.classList.toggle("text-slate-500");
        });
        label.appendChild(cb);
        label.appendChild(document.createTextNode(target));
        chipsEl.appendChild(label);
    });
    document.getElementById("time-start").value = filters.time_min;
    document.getElementById("time-end").value = filters.time_max;

    initChart("chart-heatmap");
    initChart("chart-scatter");
    initChart("chart-density");
    initChart("chart-bbox");
    await refreshAll();
    window.addEventListener("resize", function() { Object.values(charts).forEach(function(c) { c.resize(); }); });
}

function initChart(domId) {
    var chart = echarts.init(document.getElementById(domId));
    chart.on("click", function(params) { showEventDetail(domId, params); });
    charts[domId] = chart;
}

function getSelectedTargets() {
    var cbs = document.querySelectorAll("#target-chips input[type=checkbox]");
    return Array.from(cbs).filter(function(cb) { return cb.checked; }).map(function(cb) { return cb.value; });
}

async function refreshAll() {
    var targets = getSelectedTargets();
    var t0 = document.getElementById("time-start").value;
    var t1 = document.getElementById("time-end").value;
    var bucket = document.getElementById("time-bucket").value;
    var loader = document.getElementById("loading-indicator");
    loader.classList.remove("hidden");

    var bp = new URLSearchParams();
    if (targets.length) targets.forEach(function(b) { bp.append("targets", b); });
    if (t0) bp.set("time_start", t0);
    if (t1) bp.set("time_end", t1);

    var tasks = [];

    var hp = new URLSearchParams(bp); hp.set("time_bucket", bucket);
    tasks.push(fetch(API + "/api/heatmap?" + hp).then(function(r) { return r.json(); }).then(function(d) {
        charts["chart-heatmap"].setOption(buildHeatmapOption(d, CONFIG.heatmap), true);
    }));

    var sp = new URLSearchParams(bp); sp.set("time_bucket", bucket);
    tasks.push(fetch(API + "/api/scatter?" + sp).then(function(r) { return r.json(); }).then(function(d) {
        charts["chart-scatter"].setOption(buildScatterOption(d, CONFIG.scatter), true);
    }));

    var dp = new URLSearchParams(bp); dp.set("time_bucket", bucket);
    tasks.push(fetch(API + "/api/scatter_density?" + dp).then(function(r) { return r.json(); }).then(function(d) {
        charts["chart-density"].setOption(buildDensityOption(d, CONFIG.scatter_density), true);
    }));

    tasks.push(fetch(API + "/api/bbox_heatmap?" + bp).then(function(r) { return r.json(); }).then(function(d) {
        charts["chart-bbox"].setOption(buildBboxOption(d, CONFIG.bbox), true);
    }));

    await Promise.all(tasks);
    loader.classList.add("hidden");
}

function showEventDetail(chartId, params) {
    var content = document.getElementById("event-content");
    if (!params || !params.data) {
        content.innerHTML = '<span class="text-slate-400">点击了空白区域</span>';
        return;
    }
    var d = params.data;
    var name = { "chart-heatmap": "时间热力图", "chart-scatter": "时间散点图",
                    "chart-density": "二维散点密度图", "chart-bbox": "二维矩形覆盖图" }[chartId] || chartId;
    var html = '<span class="font-medium text-slate-700">' + name + '</span> &rarr; ';
    if (chartId === "chart-bbox" && Array.isArray(d) && d.length >= 6) {
        html += "目标: " + d[4] + " | 时间: " + d[5] + " | x1=" + d[0] + ", y1=" + d[1] + ", x2=" + d[2] + ", y2=" + d[3];
    } else if (Array.isArray(d)) {
        html += "数据: [" + d.join(", ") + "]";
    } else {
        html += "名称: " + (params.name || "-") + " | 值: " + (params.value || JSON.stringify(d));
    }
    if (params.seriesName) html += " | 系列: " + params.seriesName;
    content.innerHTML = html;
}

init();