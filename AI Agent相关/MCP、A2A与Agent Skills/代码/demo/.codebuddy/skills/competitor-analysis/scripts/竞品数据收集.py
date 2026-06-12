#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞品数据收集脚本
用于自动收集竞品的基本信息和市场数据
"""

import json
import sys
from typing import Dict, List, Optional
from datetime import datetime


class CompetitorDataCollector:
    """竞品数据收集器"""
    
    def __init__(self, output_file: str = "competitor_data.json"):
        self.output_file = output_file
        self.competitor_data = {}
        
    def collect_competitor_info(self, competitor_name: str) -> Dict:
        """
        收集单个竞品的信息
        返回包含竞品基本信息的字典
        """
        competitor = {
            "name": competitor_name,
            "collected_at": datetime.now().isoformat(),
            "basic_info": {
                "company_name": "",
                "website": "",
                "founded_date": "",
                "headquarters": "",
                "description": ""
            },
            "product_info": {
                "main_products": [],
                "key_features": [],
                "pricing_model": "",
                "target_market": ""
            },
            "market_data": {
                "market_share": "",
                "user_count": "",
                "growth_rate": "",
                "revenue": ""
            },
            "technology": {
                "tech_stack": [],
                "key_capabilities": [],
                "patents": []
            },
            "business_model": {
                "revenue_streams": [],
                "distribution_channels": [],
                "partners": []
            },
            "social_presence": {
                "social_media": {},
                "user_reviews": "",
                "rating": ""
            }
        }
        
        return competitor
    
    def add_competitor(self, competitor_name: str) -> None:
        """添加竞品到数据集"""
        self.competitor_data[competitor_name] = self.collect_competitor_info(competitor_name)
        print(f"✓ 已添加竞品: {competitor_name}")
    
    def update_field(self, competitor_name: str, category: str, 
                     field: str, value) -> None:
        """更新竞品的特定字段"""
        if competitor_name in self.competitor_data:
            self.competitor_data[competitor_name][category][field] = value
            print(f"✓ 已更新 {competitor_name}.{category}.{field}")
        else:
            print(f"✗ 未找到竞品: {competitor_name}")
    
    def export_data(self) -> None:
        """导出数据到JSON文件"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.competitor_data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 数据已导出到: {self.output_file}")
    
    def import_data(self, file_path: str) -> None:
        """从JSON文件导入数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.competitor_data = json.load(f)
            print(f"✓ 已从 {file_path} 导入数据")
        except Exception as e:
            print(f"✗ 导入失败: {e}")
    
    def print_summary(self) -> None:
        """打印竞品数据摘要"""
        print("\n" + "="*50)
        print("竞品数据摘要")
        print("="*50)
        for name, data in self.competitor_data.items():
            print(f"\n📊 {name}")
            print(f"  描述: {data['basic_info']['description']}")
            print(f"  网站: {data['basic_info']['website']}")
            print(f"  主要产品: {', '.join(data['product_info']['main_products'][:3])}")


def main():
    """主函数 - 交互式使用"""
    collector = CompetitorDataCollector()
    
    print("="*50)
    print("竞品数据收集工具")
    print("="*50)
    
    while True:
        print("\n选项:")
        print("1. 添加竞品")
        print("2. 更新竞品信息")
        print("3. 查看摘要")
        print("4. 导出数据")
        print("5. 导入数据")
        print("6. 退出")
        
        choice = input("\n请选择操作 (1-6): ").strip()
        
        if choice == "1":
            name = input("输入竞品名称: ").strip()
            if name:
                collector.add_competitor(name)
                
        elif choice == "2":
            name = input("输入竞品名称: ").strip()
            category = input("输入分类 (basic_info/product_info/market_data等): ").strip()
            field = input("输入字段名: ").strip()
            value = input("输入值: ").strip()
            collector.update_field(name, category, field, value)
            
        elif choice == "3":
            collector.print_summary()
            
        elif choice == "4":
            file_name = input("输出文件名 (默认: competitor_data.json): ").strip()
            if file_name:
                collector.output_file = file_name
            collector.export_data()
            
        elif choice == "5":
            file_path = input("输入要导入的文件路径: ").strip()
            collector.import_data(file_path)
            
        elif choice == "6":
            print("退出程序")
            break
            
        else:
            print("无效选择,请重试")


if __name__ == "__main__":
    main()
