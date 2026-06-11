# 项目背景

## Milestone 1 Plan

1. 检验pyechart几个特定图表的所有可能的视觉效果和互动功能接口
    - 单x轴无y轴热力图
        - 热力渐变颜色列表
        - VisualMap(坐标,宽高)
    - 单x轴散点图
        - VisualMap(坐标,宽高)
    - 二维热力散点图
    - 二维矩形热力图
2. 设计传给st_echart的数据格式(SQL Table/CSV), 放进Schema.xlsx里
    - 坐标点 (top_left,top_right,bottom_left,bottom_right) 原点是哪个？
    - target
    - time_stamp (格式为00:00, 用什么数据类型？)

## Milestone 1 Result

### 架构

```md
浏览器 (index.html)  ←Fetch→  FastAPI (main.py)  →  charts/ builder  →  pyecharts  →  ECharts option JSON
     ↑ 筛选器 + 事件                                     ↑ 读取 templates/*.toml
```

### 图表 1：单轴时间热力图 (heatmap.toml)

| 分类 | 配置项 | 可选值 | 默认值 | 说明 |
| ------ | ------ | ------ | ------ | ------ |
| 容器 | `container.width` | px | `"1920px"` | 图表宽度 |
| 容器 | `container.height` | px | `"200px"` | 图表高度 |
| 标题 | `title.text` | 任意 | `"单轴时间热力图"` | 图表标题 |
| 颜色 | `visualmap.orient` | horizontal / vertical | `"horizontal"` | 图例方向 |
| 颜色 | `visualmap.range_color` | 颜色列表 | `["green","yellow","orange","red"]` | 渐变颜色 |
| 颜色 | `visualmap.min` | 整数（0=自动） | `0` | 数值下限 |
| 颜色 | `visualmap.max` | 整数（0=自动） | `0` | 数值上限 |
| 颜色 | `visualmap.item_width` | px | `20` | 颜色条宽度 |
| 颜色 | `visualmap.item_height` | px | `200` | 颜色条高度 |
| 颜色 | `visualmap.pos_left` | left/center/right/% | `"right"` | 水平位置 |
| 颜色 | `visualmap.pos_top` | top/middle/bottom/% | `"top"` | 垂直位置 |
| X 轴 | `x_axis.axislabel_rotate` | 角度 | `-45` | 标签旋转 |
| X 轴 | `x_axis.font_size` | px | `10` | 标签字号 |
| Y 轴 | `y_axis.show` | true / false | `false` | 是否显示 Y 轴 |
| 缩放 | `datazoom.type` | slider / inside / both | `"slider"` | 缩放控件类型 |
| 缩放 | `datazoom.range_start` | 0–100 | `0` | 初始起始 % |
| 缩放 | `datazoom.range_end` | 0–100 | `100` | 初始结束 % |
| 提示 | `tooltip.show` | true / false | `true` | 悬浮提示 |
| 图例 | `legend.show` | true / false | `false` | 是否显示图例 |

### 图表 2：单轴时间散点图 (scatter.toml)

| 分类 | 配置项 | 可选值 | 默认值 | 说明 |
| ------ | ------ | ------ | ------ | ------ |
| 容器 | `container.width` | px | `"1920px"` | 图表宽度 |
| 容器 | `container.height` | px | `"50px"` | 图表高度 |
| 标题 | `title.text` | 任意 | `"单轴时间散点图"` | 图表标题 |
| 符号 | `symbol.size_base` | 整数 | `10` | 缩放系数 |
| 大小 | `visualmap.orient` | horizontal / vertical | `"horizontal"` | 图例方向 |
| 大小 | `visualmap.pos_left` | left/center/right/% | `"right"` | 水平位置 |
| 大小 | `visualmap.pos_top` | top/middle/bottom/% | `"top"` | 垂直位置 |
| 大小 | `visualmap.min` | 整数（0=自动） | `0` | 数值下限 |
| 大小 | `visualmap.max` | 整数（0=自动） | `0` | 数值上限 |
| 大小 | `visualmap.range_size` | [最小, 最大] | `[3, 40]` | 符号大小范围 |
| 缩放 | `datazoom.type` | slider / inside / both | `"slider"` | 缩放控件类型 |
| 缩放 | `datazoom.range_start` | 0–100 | `0` | 初始起始 % |
| 缩放 | `datazoom.range_end` | 0–100 | `100` | 初始结束 % |
| 提示 | `tooltip.show` | true / false | `true` | 悬浮提示 |
| 图例 | `legend.show` | true / false | `false` | 是否显示图例 |

### 图表 3：二维散点密度图 (scatter_density.toml)

| 分类 | 配置项 | 可选值 | 默认值 | 说明 |
| ------ | ------ | ------ | ------ | ------ |
| 容器 | `container.width` | px | `"960px"` | 图表宽度 |
| 容器 | `container.height` | px | `"540px"` | 图表高度 |
| 标题 | `title.text` | 任意 | `"二维散点密度图"` | 图表标题 |
| 符号 | `symbol.size_base` | 整数 | `20` | 基础大小 |
| 符号 | `symbol.scale_size` | true / false | `true` | 点大小是否随频次缩放 |
| 符号 | `symbol.range_size` | [最小, 最大] | `[10, 70]` | 大小范围 |
| 颜色 | `visualmap_color.orient` | horizontal / vertical | `"vertical"` | 颜色图例方向 |
| 颜色 | `visualmap_color.pos_left` | left/center/right/% | `"left"` | 颜色图例水平位置 |
| 颜色 | `visualmap_color.pos_top` | top/middle/bottom/% | `"center"` | 颜色图例垂直位置 |
| 颜色 | `visualmap_color.range_color` | 颜色列表 | `["blue","cyan","yellow","red"]` | 渐变颜色 |
| 大小 | `visualmap_size.show` | true / false | `true` | 是否显示大小 VisualMap |
| 大小 | `visualmap_size.range_size` | [最小, 最大] | `[10, 70]` | 大小范围 |
| X 轴 | `x_axis.name` | 任意 | `"目标频次"` | X 轴名称 |
| Y 轴 | `y_axis.name` | 任意 | `"目标多样性"` | Y 轴名称 |
| 网格 | `grid.show` | true / false | `true` | 是否显示网格 |
| 提示 | `tooltip.show` | true / false | `true` | 悬浮提示 |

### 图表 4：二维矩形覆盖图 (bbox_heatmap.toml)

| 分类 | 配置项 | 可选值 | 默认值 | 说明 |
| ------ | ------ | ------ | ------ | ------ |
| 画布 | `canvas.width` | px | `1920` | 逻辑画布宽度 |
| 画布 | `canvas.height` | px | `1080` | 逻辑画布高度 |
| 容器 | `container.width` | px | `"960px"` | 图表宽度 |
| 容器 | `container.height` | px | `"540px"` | 图表高度 |
| 标题 | `title.text` | 任意 | `"二维矩形覆盖图"` | 图表标题 |
| X 轴 | `x_axis.name` | 任意 | `"X (px)"` | X 轴名称 |
| Y 轴 | `y_axis.name` | 任意 | `"Y (px)"` | Y 轴名称 |
| 颜色 | `rect_style.fill` | RGBA | `"rgba(200,40,40,0.12)"` | 矩形填充色 |
| 颜色 | `rect_style.stroke` | RGBA | `"rgba(180,30,30,0.30)"` | 矩形描边色 |
| 颜色 | `rect_style.line_width` | px | `0.5` | 描边宽度 |
| 提示 | `tooltip.show` | true / false | `true` | 悬浮提示 |

## Milestone 1 Limit and Questions

1. build不同图表传的数据仅仅对行做了处理，没有对列做处理。
2. _dump_options_safe为什么有必要 - 没必要
3. 起始时间和结束时间为什么是文本输入框
4. 如何检查聚合粒度有没有分析意义
5. 如何检查单轴时间散点图的visualmap handle

## Milestone 2

1. 考虑生产环境下的性能问题(千万点集初始渲染、交互渲染响应时间)
2. 考虑与现有项目的集成问题
