/* 个股排雷扫描仪 - 前端交互逻辑 */
(function () {
  'use strict';

  var pageInput = document.getElementById('page-input');
  var pageReport = document.getElementById('page-report');
  var searchInput = document.getElementById('search-input');
  var searchBtn = document.getElementById('search-btn');
  var errorMsg = document.getElementById('error-msg');
  var backBtn = document.getElementById('back-btn');

  /* ---------------- 页面切换 ---------------- */
  function showInputPage() {
    pageReport.classList.add('hidden');
    pageInput.classList.remove('hidden');
    document.getElementById('dimensions-wrap').innerHTML = '';
    errorMsg.textContent = '';
    searchInput.focus();
  }

  function showReportPage() {
    pageInput.classList.add('hidden');
    pageReport.classList.remove('hidden');
    window.scrollTo(0, 0);
  }

  /* ---------------- 雷数徽章 ---------------- */
  function badgeClass(mines) {
    if (mines === null || mines === undefined) return 'badge-gray';
    if (mines === 0) return 'badge-green';
    if (mines <= 2) return 'badge-orange';
    return 'badge-red';
  }

  function badgeText(mines) {
    return (mines === null || mines === undefined) ? '—' : String(mines);
  }

  /* ---------------- 构建指标卡片 ---------------- */
  function buildIndicatorCard(ind) {
    var card = document.createElement('div');
    card.className = 'indicator-card';

    var head = document.createElement('div');
    head.className = 'card-head';

    var nameEl = document.createElement('span');
    nameEl.className = 'ind-name';
    nameEl.textContent = ind.name;

    var badge = document.createElement('span');
    badge.className = 'mine-badge ' + badgeClass(ind.mines);
    badge.textContent = badgeText(ind.mines);
    if (ind.mines === null || ind.mines === undefined) badge.title = '数据暂缺';

    head.appendChild(nameEl);
    head.appendChild(badge);

    var valueEl = document.createElement('div');
    var hasValue = ind.display !== null && ind.display !== undefined;
    valueEl.className = 'ind-value' + (hasValue ? '' : ' na');
    valueEl.textContent = hasValue ? ind.display : '—';

    var sourceEl = document.createElement('div');
    sourceEl.className = 'ind-source';
    sourceEl.textContent = '来源：' + (ind.source || '数据暂缺');

    var toggle = document.createElement('div');
    toggle.className = 'explain-toggle';
    toggle.textContent = '点击查看解释 >';

    var panel = document.createElement('div');
    panel.className = 'explain-panel';
    var text = document.createElement('div');
    text.className = 'explain-text';
    text.textContent = ind.explain || '暂无解释。';
    panel.appendChild(text);

    toggle.addEventListener('click', function () {
      var open = panel.classList.toggle('open');
      toggle.textContent = open ? '收起解释 ∧' : '点击查看解释 >';
    });

    card.appendChild(head);
    card.appendChild(valueEl);
    card.appendChild(sourceEl);
    card.appendChild(toggle);
    card.appendChild(panel);
    return card;
  }

  /* ---------------- 渲染报告 ---------------- */
  function renderReport(data) {
    document.getElementById('report-stock-title').textContent =
      (data.stock_name || '') + '（' + (data.stock_code || '') + '）';

    var stars = data.stars || 0;
    var starStr = '';
    for (var i = 0; i < 5; i++) starStr += i < stars ? '★' : '☆';
    document.getElementById('rating-stars').textContent = starStr;

    document.getElementById('rating-desc').textContent =
      '综合雷量评级：' + starStr + ' (' + stars + '星，' + (data.star_desc || '无数据') + ')';

    document.getElementById('rating-mines').textContent =
      '总雷数：' + (data.total_mines || 0) + ' / ' + (data.max_mines || 0);
    document.getElementById('rating-date').textContent =
      '数据日期：' + (data.report_date || '未知');

    var wrap = document.getElementById('dimensions-wrap');
    wrap.innerHTML = '';

    (data.dimensions || []).forEach(function (dim) {
      var title = document.createElement('h2');
      title.className = 'dimension-title';
      title.textContent = dim.name;
      wrap.appendChild(title);

      var grid = document.createElement('div');
      grid.className = 'indicator-grid';
      (dim.indicators || []).forEach(function (ind) {
        grid.appendChild(buildIndicatorCard(ind));
      });
      wrap.appendChild(grid);
    });

    showReportPage();
  }

  /* ---------------- 扫描请求 ---------------- */
  var scanning = false;

  function doScan(query) {
    query = (query || '').trim();
    if (!query) {
      errorMsg.textContent = '请输入股票代码或名称';
      return;
    }
    if (scanning) return;
    scanning = true;
    errorMsg.textContent = '';
    searchBtn.disabled = true;
    searchBtn.textContent = '扫描中...';

    fetch('/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    })
      .then(function (res) { return res.json(); })
      .then(function (json) {
        if (json.code === 200 && json.data) {
          renderReport(json.data);
        } else if (json.code === 404) {
          errorMsg.textContent = json.msg || '未找到该股票';
        } else {
          errorMsg.textContent = json.msg || '扫描失败，请稍后重试';
        }
      })
      .catch(function () {
        errorMsg.textContent = '网络异常，请检查服务是否正常运行';
      })
      .finally(function () {
        scanning = false;
        searchBtn.disabled = false;
        searchBtn.textContent = '开始扫描';
      });
  }

  /* ---------------- 事件绑定 ---------------- */
  searchBtn.addEventListener('click', function () { doScan(searchInput.value); });

  searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') doScan(searchInput.value);
  });

  document.querySelectorAll('.example-card').forEach(function (card) {
    card.addEventListener('click', function () {
      var code = card.getAttribute('data-code') || '';
      searchInput.value = code;
      doScan(code);
    });
  });

  backBtn.addEventListener('click', showInputPage);

  /* ---------------- 初始化 ---------------- */
  showInputPage();
})();
