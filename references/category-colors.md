# 分类配色方案

## 配色方案列表

HTML生成脚本 (`scripts/05_generate_html.py`) 内置6种配色方案，通过 `COLOR_THEME` 参数选择。

### 可用配色

| 配色名 | 渐变色 | 主色调 | 适用场景 |
|--------|--------|--------|---------|
| `blue` | `#1a5276 → #2e86c1` | 蓝色 | 通用、科技类 |
| `green` | `#1e8449 → #27ae60` | 绿色 | 环保、农业类 |
| `purple` | `#6c3483 → #8e44ad` | 紫色 | 礼品、装饰类 |
| `orange` | `#b3541e → #e67e22` | 橙色 | 餐厨、家居类 |
| `teal` | `#117a65 → #16a085` | 青色 | 医药、健康类 |
| `red` | `#922b21 → #c0392b` | 红色 | 食品、节日类 |

### 已使用配色

| 分类 | 配色 | 效果 |
|------|------|------|
| 电子电气 | blue | 蓝色科技感 |
| 体育食品医药个护 | teal | 青色健康感 |
| 家用纺织品地毯 | purple | 紫色品质感 |
| 工具五金 | blue | 蓝色工业感 |
| 建材家具卫浴 | teal | 青色家居感 |
| 文具 | green | 绿色清新感 |
| 时尚 | blue | 蓝色时尚感 |
| 玩具孕婴童 | green | 绿色童趣感 |
| 礼品及装饰品 | purple | 紫色精致感 |
| 餐厨用具 | orange | 橙色温暖感 |

### 使用方法

在 `05_generate_html.py` 的 CONFIG 区域设置：
```python
COLOR_THEME = 'orange'  # 从上方表格中选择
```

### 添加新配色

在 `05_generate_html.py` 的 `COLOR_THEMES` 字典中添加：
```python
COLOR_THEMES = {
    ...,
    'amber': {
        'gradient': '#9c640c, #f39c12',
        'accent': '#f39c12',
        'accent_dark': '#9c640c',
        'hover_bg': '#fef9e7',
    },
}
```

配色属性说明：
- `gradient`：头部渐变背景色（两个色值，逗号分隔）
- `accent`：主强调色（按钮、链接、搜索框聚焦边框）
- `accent_dark`：深色变体（按钮 hover 状态）
- `hover_bg`：表格行 hover 背景色（浅色）
