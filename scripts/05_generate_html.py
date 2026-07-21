#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_generate_html.py
HTML表格生成脚本 - 生成带搜索/排序/导出功能的交互式HTML

使用方法：
  1. 修改下方 CONFIG 区域的参数
  2. 运行: python3 05_generate_html.py

参数说明：
  INPUT_PATH   - 清洗后的JSON数据路径 (04_process_data.py 的输出)
  OUTPUT_PATH  - HTML输出路径 (/workspace/广交会{分类名}新企业联系方式.html)
  CATEGORY_NAME - 分类中文名 (如 "餐厨用具")
  COLOR_THEME  - 配色方案，可选值见下方 COLOR_THEMES
"""

import json
import os

# ==================== CONFIG ====================
# ★★★ 修改这四个参数 ★★★
INPUT_PATH = '/data/user/work/xx_companies_data.json'
OUTPUT_PATH = '/workspace/广交会XX新企业联系方式.html'
CATEGORY_NAME = 'XX'  # 分类中文名，如 "餐厨用具"
COLOR_THEME = 'orange'  # 配色方案: blue, green, purple, orange, teal, red
# ================================================

# ==================== 配色方案 ====================
COLOR_THEMES = {
    'blue': {
        'gradient': '#1a5276, #2e86c1',
        'accent': '#2e86c1',
        'accent_dark': '#21618c',
        'hover_bg': '#f7f9fc',
    },
    'green': {
        'gradient': '#1e8449, #27ae60',
        'accent': '#27ae60',
        'accent_dark': '#1e8449',
        'hover_bg': '#f0faf3',
    },
    'purple': {
        'gradient': '#6c3483, #8e44ad',
        'accent': '#8e44ad',
        'accent_dark': '#6c3483',
        'hover_bg': '#faf5fb',
    },
    'orange': {
        'gradient': '#b3541e, #e67e22',
        'accent': '#e67e22',
        'accent_dark': '#b3541e',
        'hover_bg': '#fef9f3',
    },
    'teal': {
        'gradient': '#117a65, #16a085',
        'accent': '#16a085',
        'accent_dark': '#117a65',
        'hover_bg': '#f0fdfa',
    },
    'red': {
        'gradient': '#922b21, #c0392b',
        'accent': '#c0392b',
        'accent_dark': '#922b21',
        'hover_bg': '#fdf2f2',
    },
}

# ==================== 主流程 ====================

def main():
    theme = COLOR_THEMES.get(COLOR_THEME, COLOR_THEMES['blue'])

    # 1. 读取清洗后的数据
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. 计算统计
    total = len(data)
    with_website = sum(1 for r in data if r['企业网站'] != '-')
    with_contact = sum(1 for r in data if r['业务联系人'] != '-')
    with_phone = sum(1 for r in data if r['办公电话'] != '-')
    with_mobile = sum(1 for r in data if r['手机'] != '-')
    with_email = sum(1 for r in data if r['邮箱'] != '-')

    # 3. 数据转JSON嵌入HTML
    data_json = json.dumps(data, ensure_ascii=False)

    # 4. 生成HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>广交会{CATEGORY_NAME}新企业联系方式</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
            background: #f0f2f5;
            color: #333;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, {theme['gradient']});
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; }}
        .header .stats {{ margin-top: 15px; display: flex; gap: 20px; flex-wrap: wrap; }}
        .header .stat-item {{
            background: rgba(255,255,255,0.15);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 13px;
        }}
        .toolbar {{
            background: white;
            padding: 15px 20px;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
            border-bottom: 1px solid #e0e0e0;
        }}
        .toolbar input[type="text"] {{
            flex: 1; min-width: 200px; padding: 8px 12px;
            border: 1px solid #ddd; border-radius: 5px; font-size: 14px;
            outline: none; transition: border-color 0.3s;
        }}
        .toolbar input[type="text"]:focus {{ border-color: {theme['accent']}; }}
        .toolbar select {{
            padding: 8px 12px; border: 1px solid #ddd; border-radius: 5px;
            font-size: 14px; background: white; cursor: pointer;
        }}
        .toolbar button {{
            padding: 8px 16px; border: none; border-radius: 5px;
            font-size: 14px; cursor: pointer; transition: all 0.3s;
        }}
        .btn-export {{ background: #27ae60; color: white; }}
        .btn-export:hover {{ background: #229954; }}
        .btn-copy {{ background: {theme['accent']}; color: white; }}
        .btn-copy:hover {{ background: {theme['accent_dark']}; }}
        .table-wrapper {{
            background: white; border-radius: 0 0 10px 10px; overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        thead {{ background: #f8f9fa; position: sticky; top: 0; z-index: 10; }}
        thead th {{
            padding: 12px 10px; text-align: left; font-weight: 600;
            color: #2c3e50; border-bottom: 2px solid #dee2e6;
            cursor: pointer; white-space: nowrap; user-select: none;
        }}
        thead th:hover {{ background: #e8eaed; }}
        thead th .sort-icon {{ margin-left: 5px; opacity: 0.5; }}
        thead th.sorted .sort-icon {{ opacity: 1; }}
        tbody tr {{ border-bottom: 1px solid #f0f0f0; transition: background 0.2s; }}
        tbody tr:hover {{ background: {theme['hover_bg']}; }}
        tbody td {{ padding: 10px; vertical-align: top; word-break: break-all; }}
        .col-idx {{ text-align: center; color: #999; width: 40px; white-space: nowrap; }}
        .col-name {{ font-weight: 500; min-width: 120px; }}
        .col-website a {{ color: {theme['accent']}; text-decoration: none; }}
        .col-website a:hover {{ text-decoration: underline; }}
        .col-contact {{ min-width: 80px; }}
        .col-phone {{ white-space: nowrap; }}
        .col-mobile {{ white-space: nowrap; color: #e74c3c; font-weight: 500; }}
        .col-email a {{ color: #8e44ad; text-decoration: none; }}
        .col-email a:hover {{ text-decoration: underline; }}
        .no-data {{ color: #ccc; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
        .result-count {{
            padding: 10px 20px; background: #fff3cd; color: #856404;
            font-size: 13px; border-bottom: 1px solid #ffeaa7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>广交会 - {CATEGORY_NAME} 新企业联系方式</h1>
            <div class="subtitle">数据来源：广交会365线上平台 (365.cantonfair.org.cn) | 筛选条件：供应商 &gt; 新企业</div>
            <div class="stats">
                <span class="stat-item">企业总数：{total}</span>
                <span class="stat-item">有网站：{with_website}</span>
                <span class="stat-item">有联系人：{with_contact}</span>
                <span class="stat-item">有办公电话：{with_phone}</span>
                <span class="stat-item">有手机：{with_mobile}</span>
                <span class="stat-item">有邮箱：{with_email}</span>
            </div>
        </div>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="搜索企业名称、联系人、电话、邮箱..." oninput="filterTable()">
            <select id="filterSelect" onchange="filterTable()">
                <option value="">全部字段</option>
                <option value="企业名称">企业名称</option>
                <option value="业务联系人">联系人</option>
                <option value="手机">手机</option>
                <option value="邮箱">邮箱</option>
                <option value="企业网站">网站</option>
            </select>
            <button class="btn-copy" onclick="copyAll()">复制全部</button>
            <button class="btn-export" onclick="exportCSV()">导出CSV</button>
        </div>
        <div class="result-count" id="resultCount">显示全部 {total} 条记录</div>
        <div class="table-wrapper">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th class="col-idx">#</th>
                        <th class="col-name" onclick="sortTable(1)">企业名称<span class="sort-icon">⇅</span></th>
                        <th class="col-website" onclick="sortTable(2)">企业网站<span class="sort-icon">⇅</span></th>
                        <th class="col-contact" onclick="sortTable(3)">业务联系人<span class="sort-icon">⇅</span></th>
                        <th class="col-phone" onclick="sortTable(4)">办公电话<span class="sort-icon">⇅</span></th>
                        <th class="col-mobile" onclick="sortTable(5)">手机<span class="sort-icon">⇅</span></th>
                        <th class="col-email" onclick="sortTable(6)">邮箱<span class="sort-icon">⇅</span></th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
        <div class="footer">数据采集时间：2026年 | 本表格仅供业务参考，请勿用于其他用途</div>
    </div>
    <script>
        var data = {data_json};
        var sortColumn = -1;
        var sortAsc = true;
        var filteredData = data.slice();

        function renderTable() {{
            var tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            filteredData.forEach(function(item, idx) {{
                var tr = document.createElement('tr');
                var websiteHtml = item['企业网站'] === '-' ?
                    '<span class="no-data">-</span>' :
                    '<a href="' + item['企业网站'] + '" target="_blank">' + item['企业网站'] + '</a>';
                var emailHtml = item['邮箱'] === '-' ?
                    '<span class="no-data">-</span>' :
                    '<a href="mailto:' + item['邮箱'] + '">' + item['邮箱'] + '</a>';
                var contactHtml = item['业务联系人'] === '-' ?
                    '<span class="no-data">-</span>' : item['业务联系人'];
                var phoneHtml = item['办公电话'] === '-' ?
                    '<span class="no-data">-</span>' : item['办公电话'];
                var mobileHtml = item['手机'] === '-' ?
                    '<span class="no-data">-</span>' : item['手机'];
                tr.innerHTML = '<td class="col-idx">' + (idx + 1) + '</td>' +
                    '<td class="col-name">' + item['企业名称'] + '</td>' +
                    '<td class="col-website">' + websiteHtml + '</td>' +
                    '<td class="col-contact">' + contactHtml + '</td>' +
                    '<td class="col-phone">' + phoneHtml + '</td>' +
                    '<td class="col-mobile">' + mobileHtml + '</td>' +
                    '<td class="col-email">' + emailHtml + '</td>';
                tbody.appendChild(tr);
            }});
            document.getElementById('resultCount').textContent = '显示 ' + filteredData.length + ' 条记录（共 ' + data.length + ' 条）';
        }}

        function filterTable() {{
            var query = document.getElementById('searchInput').value.toLowerCase().trim();
            var field = document.getElementById('filterSelect').value;
            if (!query) {{
                filteredData = data.slice();
            }} else {{
                filteredData = data.filter(function(item) {{
                    if (field) {{
                        return (item[field] || '').toLowerCase().indexOf(query) !== -1;
                    }} else {{
                        return Object.keys(item).some(function(key) {{
                            return (item[key] || '').toLowerCase().indexOf(query) !== -1;
                        }});
                    }}
                }});
            }}
            if (sortColumn >= 0) {{
                applySort();
            }}
            renderTable();
        }}

        function sortTable(colIndex) {{
            var fields = ['', '企业名称', '企业网站', '业务联系人', '办公电话', '手机', '邮箱'];
            var field = fields[colIndex];
            if (sortColumn === colIndex) {{
                sortAsc = !sortAsc;
            }} else {{
                sortColumn = colIndex;
                sortAsc = true;
            }}
            document.querySelectorAll('thead th').forEach(function(th) {{
                th.classList.remove('sorted');
            }});
            document.querySelectorAll('thead th')[colIndex].classList.add('sorted');
            applySort();
            renderTable();
        }}

        function applySort() {{
            var fields = ['', '企业名称', '企业网站', '业务联系人', '办公电话', '手机', '邮箱'];
            var field = fields[sortColumn];
            if (!field) return;
            filteredData.sort(function(a, b) {{
                var va = (a[field] || '').toString();
                var vb = (b[field] || '').toString();
                if (va === '-' && vb === '-') return 0;
                if (va === '-') return 1;
                if (vb === '-') return -1;
                if (sortAsc) {{
                    return va.localeCompare(vb, 'zh-CN');
                }} else {{
                    return vb.localeCompare(va, 'zh-CN');
                }}
            }});
        }}

        function exportCSV() {{
            var csv = '\\uFEFF序号,企业名称,企业网站,业务联系人,办公电话,手机,邮箱\\n';
            filteredData.forEach(function(item, idx) {{
                csv += (idx + 1) + ',';
                csv += '"' + (item['企业名称'] || '').replace(/"/g, '""') + '",';
                csv += '"' + (item['企业网站'] || '').replace(/"/g, '""') + '",';
                csv += '"' + (item['业务联系人'] || '').replace(/"/g, '""') + '",';
                csv += '"' + (item['办公电话'] || '').replace(/"/g, '""') + '",';
                csv += '"' + (item['手机'] || '').replace(/"/g, '""') + '",';
                csv += '"' + (item['邮箱'] || '').replace(/"/g, '""') + '"';
                csv += '\\n';
            }});
            var blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
            var link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '广交会{CATEGORY_NAME}新企业联系方式.csv';
            link.click();
        }}

        function copyAll() {{
            var text = '';
            filteredData.forEach(function(item) {{
                text += item['企业名称'] + '\\t';
                text += item['企业网站'] + '\\t';
                text += item['业务联系人'] + '\\t';
                text += item['办公电话'] + '\\t';
                text += item['手机'] + '\\t';
                text += item['邮箱'] + '\\n';
            }});
            navigator.clipboard.writeText(text).then(function() {{
                alert('已复制 ' + filteredData.length + ' 条记录到剪贴板！');
            }});
        }}

        renderTable();
    </script>
</body>
</html>'''

    # 5. 写入HTML文件
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML文件已生成: {OUTPUT_PATH}")
    print(f"企业总数: {total}")
    print(f"统计: 网站={with_website}, 联系人={with_contact}, 电话={with_phone}, 手机={with_mobile}, 邮箱={with_email}")


if __name__ == '__main__':
    main()
