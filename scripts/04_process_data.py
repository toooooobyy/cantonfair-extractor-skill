#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_process_data.py
数据清洗脚本 - 解析日志文件，清洗脏数据，生成结构化JSON

使用方法：
  1. 修改下方 CONFIG 区域的参数
  2. 运行: python3 04_process_data.py

参数说明：
  LOG_FILE    - browser_evaluate 返回的日志文件路径
                格式: /tmp/browser-use/evaluate_script-{timestamp}.log
  OUTPUT_PATH - 清洗后的JSON输出路径
                命名规范: /data/user/work/{prefix}_companies_data.json
"""

import json
import re
import os

# ==================== CONFIG ====================
# ★★★ 修改这两个参数 ★★★
LOG_FILE = '/tmp/browser-use/evaluate_script-YYYY-MM-DDTHH-MM-SS-FFF.log'
OUTPUT_PATH = '/data/user/work/xx_companies_data.json'
# ================================================

# ==================== 非企业网站过滤列表 ====================
non_website_patterns = [
    'gsxtgov.cn',           # 工商注册网站
    'globalsources.com/domei',  # 环球资源平台
    'shuidi.cn',             # 水滴信用
    '1688.com',              # 阿里巴巴1688
    '无', '暂无', '没有', '不需', '未知',  # 中文占位符
]

# ==================== 清洗函数 ====================

def clean_website(val):
    """清洗企业网站字段"""
    if not val or val == '-':
        return '-'
    val = val.strip()
    # 去除所有空白字符
    val = re.sub(r'\s+', '', val)
    # 修复中文冒号 (http：// -> http://)
    val = val.replace('：', ':')
    # 处理 "/" 或 "\" 等无效值
    if val in ['/', '\\', '.', '-']:
        return '-'
    # 检查非企业网站模式（不区分大小写）
    for pattern in non_website_patterns:
        if pattern.lower() in val.lower():
            return '-'
    # 检查邮箱误填到网站字段
    if '@' in val:
        return '-'
    # 检查公司名误填到网站字段（含中文字符）
    if re.search(r'[\u4e00-\u9fff]', val):
        return '-'
    # 补全 http:// 前缀
    if not val.startswith('http://') and not val.startswith('https://'):
        if not val.startswith('www.') and '.' in val:
            val = 'http://' + val
        elif not val.startswith('www.') and '.' not in val:
            return '-'
        elif val.startswith('www.'):
            val = 'http://' + val
    # 域名部分小写化，去除尾部斜杠
    if val.startswith('http://') or val.startswith('https://'):
        parts = val.split('://')
        if len(parts) == 2:
            domain_and_path = parts[1]
            if '/' in domain_and_path:
                domain, path = domain_and_path.split('/', 1)
                path = path.rstrip('/')
                if path:
                    val = parts[0] + '://' + domain.lower() + '/' + path
                else:
                    val = parts[0] + '://' + domain.lower()
            else:
                val = parts[0] + '://' + domain_and_path.lower()
    return val


def clean_phone(val):
    """清洗办公电话字段"""
    if not val or val == '-':
        return '-'
    val = val.strip()
    # 去除国际区号前缀
    val = re.sub(r'^\+86\s*', '', val)
    val = re.sub(r'^0086\s*', '', val)
    val = re.sub(r'^86[-\s]*', '', val)
    # 如果是11位纯数字（手机号格式），去除空格和横线
    if len(val.replace('-', '').replace(' ', '')) == 11 and val.replace('-', '').replace(' ', '').isdigit():
        val = val.replace('-', '').replace(' ', '')
    return val


def clean_mobile(val):
    """清洗手机字段"""
    if not val or val == '-':
        return '-'
    val = val.strip()
    # 处理多号码字段 (如 "国内销售：13893750608 \n国际销售：13651813459")
    if '\n' in val or '国内' in val or '国际' in val:
        numbers = re.findall(r'1[3-9]\d{9}', val)
        if numbers:
            val = numbers[0]
        else:
            return '-'
    # 去除国际区号前缀
    val = re.sub(r'^\+86\s*', '', val)
    val = re.sub(r'^0086\s*', '', val)
    # 去除所有非数字字符
    val = re.sub(r'[^\d]', '', val)
    # 校验手机号格式
    if re.match(r'^1[3-9]\d{9}$', val):
        return val
    # 非11位但全是数字
    if len(val) == 11 and val.isdigit():
        return val
    return val if val else '-'


def clean_email(val):
    """清洗邮箱字段"""
    if not val or val == '-':
        return '-'
    val = val.strip()
    # 修复 .cm 拼写错误
    val = val.replace('.cm', '.com')
    # 去除空白字符
    val = re.sub(r'\s+', '', val)
    # 邮箱格式校验
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', val):
        return '-'
    return val


def clean_contact(val):
    """清洗业务联系人字段"""
    if not val or val == '-':
        return '-'
    return val.strip()


# ==================== 主流程 ====================

def parse_log_file(log_file):
    """解析日志文件，支持双重JSON解码"""
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    if content.startswith('Result: '):
        # 日志格式: Result: "{JSON编码的字符串}"
        # 需要双重解码
        json_encoded = content[len('Result: '):]
        inner_json = json.loads(json_encoded)      # 第一次解码：外层JSON字符串
        raw_data = json.loads(inner_json)           # 第二次解码：内层数据
    else:
        raw_data = json.loads(content)

    return raw_data


def main():
    # 1. 解析日志文件
    print(f"读取日志文件: {LOG_FILE}")
    raw_data = parse_log_file(LOG_FILE)
    print(f"总记录数: {len(raw_data)}")

    # 2. 清洗所有记录
    cleaned_data = []
    for record in raw_data:
        if record.get('error'):
            print(f"  跳过错误记录: {record['code']} - {record['error']}")
            continue
        cleaned = {
            'code': record.get('code', ''),
            '企业名称': record.get('企业名称', '-'),
            '企业网站': clean_website(record.get('企业网站', '-')),
            '业务联系人': clean_contact(record.get('业务联系人', '-')),
            '办公电话': clean_phone(record.get('办公电话', '-')),
            '手机': clean_mobile(record.get('手机', '-')),
            '邮箱': clean_email(record.get('邮箱', '-'))
        }
        cleaned_data.append(cleaned)

    # 3. 保存清洗后的数据
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    # 4. 统计输出
    total = len(cleaned_data)
    stats = {
        '企业名称': sum(1 for r in cleaned_data if r['企业名称'] != '-'),
        '企业网站': sum(1 for r in cleaned_data if r['企业网站'] != '-'),
        '业务联系人': sum(1 for r in cleaned_data if r['业务联系人'] != '-'),
        '办公电话': sum(1 for r in cleaned_data if r['办公电话'] != '-'),
        '手机': sum(1 for r in cleaned_data if r['手机'] != '-'),
        '邮箱': sum(1 for r in cleaned_data if r['邮箱'] != '-'),
    }

    print(f"\n{'='*50}")
    print(f"数据统计 (共 {total} 家企业)")
    print(f"{'='*50}")
    for field, count in stats.items():
        pct = count * 100 // total if total > 0 else 0
        print(f"  {field}: {count} ({pct}%)")
    print(f"{'='*50}")
    print(f"清洗数据已保存: {OUTPUT_PATH}")

    # 5. 打印抽样检查
    print(f"\n{'='*50}")
    print("抽样检查")
    print(f"{'='*50}")
    sample_indices = [0, total // 4, total // 2, total * 3 // 4, total - 1]
    for i in sample_indices:
        if i < len(cleaned_data):
            r = cleaned_data[i]
            print(f"\n[{i+1}] {r['企业名称']}")
            print(f"  网站: {r['企业网站']}")
            print(f"  联系人: {r['业务联系人']}")
            print(f"  电话: {r['办公电话']}")
            print(f"  手机: {r['手机']}")
            print(f"  邮箱: {r['邮箱']}")


if __name__ == '__main__':
    main()
