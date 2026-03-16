#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hello World - OpenClaw Tools Demo
"""

import datetime
import socket

def main():
    """主函数"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()
    
    print("=" * 50)
    print("🚀 OpenClaw Tools - Hello World")
    print("=" * 50)
    print(f"📅 时间: {now}")
    print(f"🖥️  主机: {hostname}")
    print("-" * 50)
    print("✅ 部署成功！")
    print("=" * 50)

if __name__ == "__main__":
    main()