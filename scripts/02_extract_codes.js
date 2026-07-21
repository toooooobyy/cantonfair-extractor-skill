/**
 * 02_extract_codes.js
 * 编码提取与去重 - 从拦截到的API响应中提取企业编码
 *
 * 使用方法：通过 browser_evaluate 执行
 * 执行时机：翻完所有页之后执行
 *
 * 重要：必须修改 EXPECTED_TOTAL 为实际的新企业总数
 *       此值用于过滤掉筛选前的API响应（totalCount不匹配的会被排除）
 *
 * 返回：JSON编码的企业code数组字符串
 */

// ★★★ 必须修改为实际的新企业总数 ★★★
var EXPECTED_TOTAL = 135;  // 例如：135、140、158等

var cap = window._capShop || [];
var codes = [];
var seen = {};

cap.forEach(function(resp) {
  if (resp && resp.result && resp.result.itemList) {
    var total = resp.result.totalCount || resp.result.totalElements;
    // 按 totalCount 过滤，排除筛选前的数据
    if (total === String(EXPECTED_TOTAL) || total === EXPECTED_TOTAL) {
      resp.result.itemList.forEach(function(item) {
        if (item.code && !seen[item.code]) {
          seen[item.code] = true;
          codes.push(item.code);
        }
      });
    }
  }
});

// 返回JSON编码的字符串（browser_evaluate 返回值会被保存到日志）
JSON.stringify(codes);
