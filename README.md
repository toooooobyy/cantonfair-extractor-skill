# Canton Fair New Enterprise Contact Extractor Skill

> 广交会线上平台新企业联系方式采集技能
> 经过10个分类、1191家企业的实战验证

## 什么是这个Skill？

这是一个完整的工作流技能，用于从广交会线上平台 (365.cantonfair.org.cn) 采集特定分类下"新企业"的联系方式，并生成可搜索、可排序、可导出的交互式HTML表格。

## 文件结构

```
cantonfair-extractor-skill/
├── SKILL.md                          # 主工作流文档（核心）
├── README.md                         # 本文件
├── scripts/
│   ├── 01_intercept_api.js           # API拦截器注入脚本
│   ├── 02_extract_codes.js           # 企业编码提取脚本
│   ├── 03_batch_fetch.js             # 批量获取联系方式脚本
│   ├── 04_process_data.py            # 数据清洗脚本（参数化）
│   └── 05_generate_html.py           # HTML表格生成脚本（参数化）
└── references/
    ├── troubleshooting.md            # 故障排查指南
    ├── data-cleaning-rules.md        # 数据清洗规则详解
    └── category-colors.md            # 分类配色方案
```

## 快速开始

### 输入

一个广交会分类URL：
```
https://365.cantonfair.org.cn/zh-CN/search?queryType=1&fCategoryId={ID}&categoryId={ID}
```

### 输出

一个交互式HTML表格，包含6个字段：
- 企业名称
- 企业网站（可点击链接）
- 业务联系人
- 办公电话
- 手机
- 邮箱（可点击发送邮件）

### 执行流程（5个阶段）

```
阶段1: 导航到分类URL → 切换供应商视图 → 勾选"新企业" → 记录总数
阶段2: 注入API拦截器 → 翻页 → 提取企业编码 → 保存编码
阶段3: 导航到www域名 → 分批获取联系方式（每批50个）
阶段4: 运行Python清洗脚本 → 生成结构化JSON
阶段5: 运行Python HTML生成脚本 → 输出HTML表格
```

详细操作步骤见 [SKILL.md](SKILL.md)。

## 脚本使用说明

### JS脚本（在浏览器中执行）

通过 `browser_evaluate` 工具执行，需要按顺序操作：

1. **01_intercept_api.js** — 在365域名页面注入，拦截API响应
2. **02_extract_codes.js** — 翻完所有页后执行，提取企业编码
   - **必须修改** `EXPECTED_TOTAL` 为实际新企业总数
3. **03_batch_fetch.js** — 在www域名页面执行，获取联系方式
   - **必须替换** `codes` 数组为实际企业编码
   - 每批最多50个，超过需分多次执行

### Python脚本（在终端中执行）

4. **04_process_data.py** — 数据清洗
   - **必须修改** `LOG_FILE` 和 `OUTPUT_PATH`
   ```python
   LOG_FILE = '/tmp/browser-use/evaluate_script-YYYY-MM-DDTHH-MM-SS-FFF.log'
   OUTPUT_PATH = '/data/user/work/xx_companies_data.json'
   ```
   - 运行：`python3 04_process_data.py`

5. **05_generate_html.py** — HTML生成
   - **必须修改** `INPUT_PATH`、`OUTPUT_PATH`、`CATEGORY_NAME`、`COLOR_THEME`
   ```python
   INPUT_PATH = '/data/user/work/xx_companies_data.json'
   OUTPUT_PATH = '/workspace/广交会XX新企业联系方式.html'
   CATEGORY_NAME = '餐厨用具'
   COLOR_THEME = 'orange'  # blue, green, purple, orange, teal, red
   ```
   - 运行：`python3 05_generate_html.py`

## 实战战绩

| 分类 | 企业数 | 网站 | 联系人 | 电话 | 手机 | 邮箱 |
|------|--------|------|--------|------|------|------|
| 电子电气 | 71 | 52% | 99% | 37% | 99% | 77% |
| 体育食品医药个护 | 217 | 34% | 100% | 40% | 100% | 84% |
| 家用纺织品地毯 | 47 | 26% | 100% | 38% | 100% | 72% |
| 工具五金 | 135 | 41% | 99% | 36% | 100% | 76% |
| 建材家具卫浴 | 211 | 46% | 100% | 40% | 100% | 76% |
| 文具 | 20 | 70% | 100% | 60% | 100% | 95% |
| 时尚 | 158 | 34% | 100% | 36% | 100% | 84% |
| 玩具孕婴童 | 57 | 35% | 100% | 39% | 100% | 77% |
| 礼品及装饰品 | 140 | 34% | 100% | 33% | 100% | 79% |
| 餐厨用具 | 135 | 36% | 99% | 29% | 100% | 73% |
| **合计** | **1191** | **38%** | **99.7%** | **37%** | **99.9%** | **79%** |

## 关键技术要点

1. **双域名架构**：365域名用于筛选浏览，www域名用于API获取联系方式
2. **API拦截**：同时覆盖 `fetch` 和 `XMLHttpRequest`，确保所有请求都被捕获
3. **totalCount过滤**：排除筛选前的全量数据响应
4. **双重JSON解码**：日志文件格式为 `Result: "{JSON字符串}"`，需要两次解码
5. **批量并发控制**：每批10个并发请求，批间300ms间隔，避免频率限制

## 参考文档

- [SKILL.md](SKILL.md) — 完整工作流指南
- [故障排查](references/troubleshooting.md) — 11个常见问题与解决方案
- [数据清洗规则](references/data-cleaning-rules.md) — 详细的清洗逻辑
- [配色方案](references/category-colors.md) — 6种HTML配色主题
