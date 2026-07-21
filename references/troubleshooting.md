# 故障排查指南

## 常见问题与解决方案

### 1. window._capShop 为空或未定义

**原因**：API拦截器注入时机太晚，页面已经发出了API请求。

**解决方案**：
1. 刷新页面 (`browser_navigate` 重新导航到分类URL)
2. 立即注入拦截器 (`scripts/01_intercept_api.js`)
3. 再执行切换供应商视图、勾选新企业等操作
4. 翻页触发新的API请求

**关键原则**：拦截器必须在任何 `queryshop` 请求发出之前注入。

---

### 2. 跨域导航丢失JS变量

**原因**：从 `365.cantonfair.org.cn` 导航到 `www.cantonfair.org.cn` 时，浏览器加载新页面，所有JS变量（包括 `window._capShop` 和编码列表）都会丢失。

**解决方案**：
- 在导航之前，通过 `browser_evaluate` 执行脚本提取编码
- 脚本返回值会保存到日志文件中
- 从日志文件中读取编码，在新的域名页面使用

**操作流程**：
```
365域名 → 注入拦截器 → 翻页 → 提取编码（返回值保存到日志）
                                                    ↓
www域名 ← 读取日志中的编码 ← 执行批量获取脚本
```

---

### 3. 预筛选API响应混入

**原因**：API拦截器会捕获所有 `queryshop` 请求，包括切换供应商视图之前发出的请求（包含全量数据）。

**症状**：提取的编码数量远大于新企业总数。

**解决方案**：
在提取编码时，按 `totalCount` 过滤响应：
```javascript
if (total === String(EXPECTED_TOTAL) || total === EXPECTED_TOTAL) {
  // 只处理匹配新企业总数的响应
}
```

`EXPECTED_TOTAL` 应设置为阶段1记录的新企业总数。

---

### 4. 页面显示数与API返回数不一致

**原因**：页面显示的"共XXX家"可能包含未激活的企业，而API返回的是激活状态的企业。

**示例**：页面显示136家，API返回135家。

**解决方案**：
- 以API返回的实际数据条数为准
- 在提取编码时，使用页面上显示的数字作为 `EXPECTED_TOTAL` 的参考
- 如果API返回的 `totalCount` 是字符串类型或数字类型，都要匹配

---

### 5. 日志文件解析失败

**原因**：`browser_evaluate` 返回的值被保存为 `Result: "{JSON字符串}"` 格式，直接 `json.loads` 会失败。

**解决方案**：使用双重JSON解码：
```python
content = f.read().strip()
if content.startswith('Result: '):
    json_encoded = content[len('Result: '):]
    inner_json = json.loads(json_encoded)    # 第一次：解码外层JSON字符串
    raw_data = json.loads(inner_json)         # 第二次：解码内层数据
```

---

### 6. 批量获取部分请求失败

**原因**：网络超时、频率限制或企业编码无效。

**解决方案**：
- 脚本已内置错误处理，失败的请求返回 `{error: "..."}`
- 清洗脚本会自动跳过含 `error` 字段的记录
- 如果错误率 >5%，检查：
  - 是否在正确的域名 (`www.cantonfair.org.cn`) 执行
  - 并发数是否过高（降低 `batchSize`）
  - 批间间隔是否太短（增加 `setTimeout` 的延迟）

---

### 7. 翻页按钮无法点击

**原因**：Vue.js SPA的分页组件可能在DOM更新后元素引用失效。

**解决方案**：
1. 每次 `browser_click` 后等待1-2秒
2. 重新执行 `browser_snapshot` 获取最新的元素引用
3. 使用 `browser_evaluate` 直接触发分页：
   ```javascript
   // 找到分页组件并触发下一页
   var pager = document.querySelector('.el-pager .active');
   var next = pager.nextElementSibling;
   if (next) next.click();
   ```

---

### 8. 浏览器锁定 (browser locked)

**原因**：长时间操作后浏览器可能被锁定。

**解决方案**：
```bash
# 通过 MCP 工具解锁
browser_unlock
```

如果解锁后状态异常，重新导航到目标页面。

---

### 9. 企业网站字段异常值

| 异常值 | 原因 | 处理方式 |
|--------|------|---------|
| `无` / `暂无` | 企业未填写 | 过滤为 `-` |
| `/` | 占位符 | 过滤为 `-` |
| `ELLIE@JOJO-JEWELRY.COM` | 邮箱误填到网站字段 | 检测 `@` 符号，过滤为 `-` |
| `台州寰骏科技有限公司` | 公司名误填到网站字段 | 检测中文字符，过滤为 `-` |
| `http：//www.xxx.com` | 中文冒号 | 替换 `：` 为 `:` |
| `https://xxx.com/ ` | 尾部空格 | `strip()` 处理 |
| `www.xxx.en.alibaba.com` | 阿里巴巴平台链接 | 根据需求决定是否保留 |
| `shuidi.cn` | 水滴信用链接 | 过滤为 `-` |
| `1688.com` | 阿里巴巴1688链接 | 过滤为 `-` |

---

### 10. 手机号字段异常值

| 异常值 | 原因 | 处理方式 |
|--------|------|---------|
| `国内销售：13893750608 \n国际销售：13651813459` | 多号码字段 | `re.findall(r'1[3-9]\d{9}', val)` 提取第一个 |
| `+86 13800138000` | 国际区号前缀 | `re.sub(r'^\+86\s*', '', val)` |
| `008613800138000` | 0086前缀 | `re.sub(r'^0086\s*', '', val)` |

---

### 11. 邮箱字段异常值

| 异常值 | 原因 | 处理方式 |
|--------|------|---------|
| `sale@eastshoes.cm` | `.com` 拼写为 `.cm` | `val.replace('.cm', '.com')` |
| `sale @ xxx.com` | 含空格 | `re.sub(r'\s+', '', val)` |
| `xxx.com`（无@） | 格式不完整 | 正则校验失败，过滤为 `-` |
