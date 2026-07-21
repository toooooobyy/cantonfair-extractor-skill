/**
 * 01_intercept_api.js
 * API拦截器 - 捕获 queryshop 请求的响应
 *
 * 使用方法：通过 browser_evaluate 在 365.cantonfair.org.cn 页面执行
 * 执行时机：在切换供应商视图、勾选新企业之前注入
 *
 * 拦截器会捕获所有包含 "queryshop" 的请求响应，保存到 window._capShop 数组
 * 同时覆盖 fetch 和 XMLHttpRequest，确保两种请求方式都被拦截
 */

// ========== 拦截 fetch ==========
var origFetch = window.fetch;
window._capShop = [];
window.fetch = function() {
  var url = arguments[0];
  if (typeof url === 'string' && url.indexOf('queryshop') !== -1) {
    return origFetch.apply(this, arguments).then(function(response) {
      var cloned = response.clone();
      cloned.json().then(function(data) {
        window._capShop.push(data);
      }).catch(function(e) {});
      return response;
    });
  }
  return origFetch.apply(this, arguments);
};

// ========== 拦截 XMLHttpRequest ==========
var origXHROpen = XMLHttpRequest.prototype.open;
var origXHRSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function(method, url) {
  this._cfUrl = url;
  return origXHROpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function() {
  var self = this;
  if (this._cfUrl && this._cfUrl.indexOf('queryshop') !== -1) {
    this.addEventListener('load', function() {
      try {
        var data = JSON.parse(self.responseText);
        window._capShop.push(data);
      } catch (e) {}
    });
  }
  return origXHRSend.apply(this, arguments);
};

'API拦截器已注入。window._capShop 将捕获所有 queryshop 响应。';
