#!/usr/bin/env python3
import urllib.request
import urllib.parse
import urllib.error
import re
import sys
import argparse
import time
import random
import ssl  

def query_arxiv(query, max_papers=10):
    """
    在 arXiv 预印本库中搜索论文。
    包含：重试机制、User-Agent伪装、SSL证书忽略（适配 Windows）。
    """
    base_url = "http://export.arxiv.org/api/query"
    
    # URL 编码
    encoded_query = urllib.parse.quote(query)
    # 按相关性排序
    url = f"{base_url}?search_query=all:{encoded_query}&start=0&max_results={max_papers}&sortBy=relevance&sortOrder=descending"

    # 模拟浏览器 Header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    # 创建一个不验证 SSL 证书的上下文
    # 解决 Windows 上常见的 CERTIFICATE_VERIFY_FAILED 报错
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # 重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            
            # 在 urlopen 中传入 context=ctx
            with urllib.request.urlopen(req, timeout=20, context=ctx) as response:
                if response.getcode() != 200:
                    return f"Error: arXiv API returned status {response.getcode()}"
                xml_content = response.read().decode('utf-8')

            # 解析 XML
            entries = re.findall(r'<entry>(.*?)</entry>', xml_content, re.DOTALL)
            
            results = []
            for entry in entries:
                title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                id_match = re.search(r'<id>(.*?)</id>', entry, re.DOTALL)
                published_match = re.search(r'<published>(.*?)</published>', entry, re.DOTALL)

                if title_match and summary_match:
                    # 清洗数据：去换行符和多余空格
                    title = re.sub(r'\s+', ' ', title_match.group(1).strip())
                    summary = re.sub(r'\s+', ' ', summary_match.group(1).strip())
                    link = id_match.group(1).strip() if id_match else "N/A"
                    date = published_match.group(1)[:10] if published_match else "N/A"
                    
                    results.append(f"Title: {title}\nDate: {date}\nLink: {link}\nSummary: {summary}")

            if not results:
                return "No papers found matching the query."

            return "\n\n" + "="*50 + "\n\n".join(results)

        except urllib.error.HTTPError as e:
            if e.code == 429: # Too Many Requests
                wait_time = (attempt + 1) * 3  # 增加一点等待时间
                print(f"Warning: Rate limited (429). Retrying in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            else:
                return f"HTTP Error querying arXiv: {e}"
        except Exception as e:
            return f"Error querying arXiv: {e}"

    return "Error: Failed to query arXiv after multiple retries."

def main():
    # 强制让标准输出使用 utf-8，防止 Windows 控制台中文乱码
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="arXiv Search Skill (Windows Robust)")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--max-papers", type=int, default=5, help="Max papers (default: 5)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    print(query_arxiv(args.query, args.max_papers))

if __name__ == "__main__":
    main()