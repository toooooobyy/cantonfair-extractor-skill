/**
 * 03_batch_fetch.js
 * 批量获取联系方式 - 通过 shopExt API 获取每家企业的联系方式
 *
 * 使用方法：通过 browser_evaluate 在 www.cantonfair.org.cn 页面执行
 * 执行时机：导航到 www.cantonfair.org.cn 之后
 *
 * 重要：
 *   1. 必须在 www.cantonfair.org.cn 域名执行，365域名不行
 *   2. 将 codes 数组替换为实际的企业编码列表
 *   3. 每批最多50个编码，超过需分多次执行
 *   4. industrySiteId 固定为 461110967833538560
 *
 * 返回：JSON编码的企业联系方式数组字符串
 */

// ★★★ 将此数组替换为实际的企业编码（每批最多50个）★★★
var codes = [
  "CODE1", "CODE2", "CODE3", "CODE4", "CODE5",
  "CODE6", "CODE7", "CODE8", "CODE9", "CODE10"
  // ... 最多50个
];

var INDUSTRY_SITE_ID = '461110967833538560';

function fetchOne(code) {
  var url = '/b2bshop/api/themeRos/public/shopExt/searchByVariables?shopCode=' + code +
    '&industrySiteId=' + INDUSTRY_SITE_ID +
    '&unbox=true&_nc=1&filter=salesInfo.status%20eq%20%27ACTIVE%27';

  return fetch(url)
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var st = data.siteTrader || {};
      var tenant = st.tenant || {};
      var contact = tenant.contact || {};
      var udfs = data.udfs || {};
      var stUdfs = st.udfs || {};

      return {
        code: code,
        '企业名称': st.name || data.name || '-',
        '企业网站': contact.companyWebsite || udfs.companyWebsite || stUdfs.companyWebsite || '-',
        '业务联系人': udfs.contactPerson || contact.contactName || stUdfs.contactPerson || '-',
        '办公电话': udfs.telephone || contact.companyTelephone || stUdfs.telephone || '-',
        '手机': udfs.mobilePhone ||
                (contact.mobileNum ? contact.mobileNum.replace(/^\+86/, '') : '') ||
                stUdfs.mobilePhone || '-',
        '邮箱': udfs.email || contact.email || stUdfs.email ||
                (tenant.contact ? tenant.contact.companyEmail : '') || '-'
      };
    })
    .catch(function(e) {
      return { code: code, error: e.message };
    });
}

// 分批处理：每批10个并发，批间间隔300ms
var batchSize = 10;
var results = [];

function processBatch(startIdx) {
  if (startIdx >= codes.length) {
    return Promise.resolve();
  }
  var batch = codes.slice(startIdx, startIdx + batchSize);
  return Promise.all(batch.map(fetchOne)).then(function(batchResults) {
    results = results.concat(batchResults);
    return new Promise(function(resolve) {
      setTimeout(function() { resolve(); }, 300);
    });
  }).then(function() {
    return processBatch(startIdx + batchSize);
  });
}

processBatch(0).then(function() {
  // 输出统计信息到控制台
  var errors = results.filter(function(r) { return r.error; });
  console.log('获取完成: ' + results.length + ' 条, 错误: ' + errors.length + ' 条');
  // 返回JSON编码的字符串
  return JSON.stringify(results);
});
