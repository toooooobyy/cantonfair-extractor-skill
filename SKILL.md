# Canton Fair New Enterprise Contact Extractor

> 广交会线上平台新企业联系方式采集工作流
> 经过10个分类、1191家企业的实战验证

## 适用场景

当用户需要从广交会线上平台 (365.cantonfair.org.cn) 采集某个分类下"新企业"的联系方式时，使用此工作流。

**采集字段**：企业名称、企业网站、业务联系人、办公电话、手机、邮箱

**输入**：广交会分类URL（如 `https://365.cantonfair.org.cn/zh-CN/search?queryType=1&fCategoryId=xxx&categoryId=xxx`）

**输出**：交互式HTML表格（支持搜索/排序/导出CSV/复制）

## 前置条件

- 浏览器MCP工具可用（integrated_browser）
- Python 3 运行环境
- 用户已登录广交会平台（或页面可公开访问）

## 工作流总览

```
分类URL → 导航筛选 → API拦截获取编码 → 批量获取联系方式 → 数据清洗 → HTML生成
```

共5个阶段，每个阶段有对应的脚本模板（见 `scripts/` 目录）。

---

## 阶段1：导航与筛选

### 目标
打开分类页面，切换到供应商视图，筛选"新企业"，记录新企业总数。

### 操作步骤

1. **导航到分类URL**
   ```
   browser_navigate → https://365.cantonfair.org.cn/zh-CN/search?queryType=1&fCategoryId={categoryId}&categoryId={categoryId}
   ```

2. **等待页面加载完成**
   - 使用 `browser_snapshot` 检查页面结构
   - 查找"供应商"tab和"新企业"复选框

3. **切换到供应商视图**
   - 点击"供应商"tab（通常是第二个tab）
   - 等待页面刷新

4. **勾选"新企业"筛选条件**
   - 找到"新企业"复选框（el-checkbox）
   - 点击勾选
   - 等待筛选结果加载

5. **记录新企业总数**
   - 页面会显示"共XXX家"或类似文字
   - 记录此数字，后续用于：
     - 计算翻页次数（每页20条）
     - 校验API拦截的响应是否为筛选后的数据
   - **重要**：页面显示数与API返回数可能差1（如页面136，API返回135），以API返回为准

### 注意事项
- 如果页面未登录，可能需要用户手动登录后再继续
- 页面是Vue.js SPA，操作后需要等待异步加载
- 使用增量等待策略：2秒 → snapshot → 检查 → 2秒 → snapshot

---

## 阶段2：API拦截获取企业编码

### 目标
通过拦截 `queryshop` API响应，提取所有新企业的唯一编码（code）。

### 操作步骤

1. **注入API拦截器**
   - 执行 `scripts/01_intercept_api.js` 的内容
   - 拦截器会捕获所有 `queryshop` 请求的响应到 `window._capShop` 数组

2. **逐页翻页触发API请求**
   - 每页20条，翻页直到最后一页
   - 使用 `browser_click` 点击分页按钮（el-pager中的数字按钮）
   - 每次翻页后等待1-2秒确保API响应被捕获
   - 翻页次数 = ceil(新企业总数 / 20)

3. **提取去重后的编码列表**
   - 执行 `scripts/02_extract_codes.js` 的内容
   - **关键**：必须按 `totalCount` 过滤响应，排除筛选前的数据
   - 将 `totalCount` 替换为实际的新企业总数（从阶段1获得）

4. **保存编码列表**
   - 将编码数组保存到 `/data/user/work/{prefix}_codes.json`
   - **重要**：跨域导航会丢失所有JS变量，必须先保存！

### 注意事项
- API拦截器同时拦截 `fetch` 和 `XMLHttpRequest`
- 有些页面可能使用XHR而非fetch，两种都要覆盖
- 翻页时可能触发多次API请求，拦截器会全部捕获，去重在提取阶段处理
- 如果 `window._capShop` 为空，说明拦截器注入时机太晚，需要刷新页面重新注入

---

## 阶段3：批量获取联系方式

### 目标
在 `www.cantonfair.org.cn` 域名上，通过 shopExt API 批量获取每家企业的联系方式。

### 操作步骤

1. **导航到 www.cantonfair.org.cn**
   ```
   browser_navigate → https://www.cantonfair.org.cn
   ```
   - **重要**：shopExt API 只在此域名可用，365域名不行
   - 导航后所有JS变量丢失，所以阶段2必须先保存编码

2. **分批获取数据**
   - 执行 `scripts/03_batch_fetch.js` 的内容
   - 将编码数组分成每批50个
   - 每批内部使用 Promise.all 并发10个请求，间隔300ms
   - API端点：`/b2bshop/api/themeRos/public/shopExt/searchByVariables`

3. **获取返回的数据**
   - 脚本返回JSON数组，每个元素包含6个字段
   - 数据会保存在浏览器的 evaluate_script 日志中
   - 日志路径格式：`/tmp/browser-use/evaluate_script-{timestamp}.log`

### API参数说明

```
GET /b2bshop/api/themeRos/public/shopExt/searchByVariables
  ?shopCode={企业编码}
  &industrySiteId=461110967833538560    # 固定值
  &unbox=true
  &_nc=1
  &filter=salesInfo.status eq 'ACTIVE'
```

### 数据字段映射

| API字段路径 | 输出字段 |
|-------------|---------|
| `siteTrader.name` | 企业名称 |
| `contact.companyWebsite` / `udfs.companyWebsite` | 企业网站 |
| `udfs.contactPerson` / `contact.contactName` | 业务联系人 |
| `udfs.telephone` / `contact.companyTelephone` | 办公电话 |
| `udfs.mobilePhone` / `contact.mobileNum` | 手机 |
| `udfs.email` / `contact.email` | 邮箱 |

### 注意事项
- 每批最多50个编码，超过会导致URL过长或超时
- 并发数控制在10个，避免触发频率限制
- 如果个别请求失败，脚本会返回 `{error: "..."}` 对象，清洗阶段会跳过
- `industrySiteId` 在所有分类中都是 `461110967833538560`

---

## 阶段4：数据清洗

### 目标
解析日志文件，清洗脏数据，生成结构化JSON。

### 操作步骤

1. **定位日志文件**
   - 路径：`/tmp/browser-use/evaluate_script-{timestamp}.log`
   - 文件格式：`Result: "{JSON编码的字符串}"`
   - 需要双重JSON解码

2. **运行清洗脚本**
   - 复制 `scripts/04_process_data.py` 到 `/data/user/work/`
   - 修改顶部参数：
     - `log_file`：日志文件路径
     - `output_path`：输出JSON路径
   - 执行：`python3 process_data.py`

3. **检查清洗结果**
   - 脚本会输出统计信息（各字段完整率）
   - 检查是否有异常低的完整率

### 清洗规则详解

详见 `references/data-cleaning-rules.md`，核心规则：

| 字段 | 清洗内容 |
|------|---------|
| 企业网站 | 过滤非企业网站（shuidi.cn/1688.com等）、修复中文冒号、检测邮箱/公司名误填、补全http://前缀、域名小写化 |
| 手机 | 提取多号码字段中的第一个、去除+86前缀、校验1[3-9]\d{9}格式 |
| 办公电话 | 去除+86/0086/86-前缀、保留座机格式（如0571-12345678） |
| 邮箱 | 修复.cm→.com拼写错误、格式校验 |
| 业务联系人 | 去除首尾空格 |

### 注意事项
- 日志文件解析必须使用双重JSON解码：`json.loads(json.loads(content[8:]))`
- 清洗规则经过10个分类的迭代积累，覆盖了各种边界情况
- 如果发现新的脏数据模式，在 `non_website_patterns` 列表和清洗函数中添加规则

---

## 阶段5：HTML生成

### 目标
生成带搜索/排序/导出功能的交互式HTML表格。

### 操作步骤

1. **运行HTML生成脚本**
   - 复制 `scripts/05_generate_html.py` 到 `/data/user/work/`
   - 修改参数：
     - `input_path`：清洗后的JSON路径
     - `output_path`：HTML输出路径（`/workspace/广交会{分类名}新企业联系方式.html`）
     - `category_name`：分类中文名
     - `color_theme`：配色方案（见 `references/category-colors.md`）
   - 执行：`python3 generate_html.py`

2. **验证HTML文件**
   - 检查文件大小是否合理
   - 用浏览器打开验证功能

### HTML功能

- **搜索**：实时搜索，支持全字段或指定字段
- **排序**：点击表头排序，支持升降序切换
- **导出CSV**：导出当前筛选结果，UTF-8 BOM编码
- **复制全部**：复制TSV格式到剪贴板
- **统计栏**：显示各字段完整数量

### 配色方案

每个分类使用不同的渐变色主题，详见 `references/category-colors.md`。

---

## 完整执行示例

以"餐厨用具"分类为例：

```
输入URL: https://365.cantonfair.org.cn/zh-CN/search?queryType=1&fCategoryId=461147108741746688&categoryId=461147108741746688

阶段1: 导航 → 切换供应商 → 勾选新企业 → 记录总数136（API返回135）
阶段2: 注入拦截器 → 翻7页 → 提取135个编码 → 保存到 cy_codes.json
阶段3: 导航到www → 分3批获取(50+50+35) → 0错误 → 日志保存
阶段4: 解析日志 → 双重JSON解码 → 清洗 → cy_companies_data.json
阶段5: 生成HTML → /workspace/广交会餐厨用具新企业联系方式.html

结果: 135家企业 | 网站48(35%) | 联系人134(99%) | 电话39(28%) | 手机135(100%) | 邮箱98(72%)
```

## 参考文档

- [故障排查指南](references/troubleshooting.md) - 常见问题与解决方案
- [数据清洗规则](references/data-cleaning-rules.md) - 详细的清洗逻辑说明
- [分类配色方案](references/category-colors.md) - 各分类的HTML配色

## 脚本清单

| 脚本 | 用途 | 执行环境 |
|------|------|---------|
| `scripts/01_intercept_api.js` | API拦截器注入 | 浏览器 (browser_evaluate) |
| `scripts/02_extract_codes.js` | 编码提取与去重 | 浏览器 (browser_evaluate) |
| `scripts/03_batch_fetch.js` | 批量获取联系方式 | 浏览器 (browser_evaluate) |
| `scripts/04_process_data.py` | 数据清洗 | Python 3 |
| `scripts/05_generate_html.py` | HTML表格生成 | Python 3 |

## 已验证分类

| 分类 | 企业数 | 采集日期 |
|------|--------|---------|
| 电子电气 | 71 | 2026-07-20 |
| 体育食品医药个护 | 217 | 2026-07-21 |
| 家用纺织品地毯 | 47 | 2026-07-21 |
| 工具五金 | 135 | 2026-07-21 |
| 建材家具卫浴 | 211 | 2026-07-21 |
| 文具 | 20 | 2026-07-21 |
| 时尚 | 158 | 2026-07-21 |
| 玩具孕婴童 | 57 | 2026-07-21 |
| 礼品及装饰品 | 140 | 2026-07-21 |
| 餐厨用具 | 135 | 2026-07-21 |
| **合计** | **1191** | |
