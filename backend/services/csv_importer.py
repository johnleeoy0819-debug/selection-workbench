"""
CSV 导入服务
支持 eRank 两种 CSV 格式：关键词列表 + Top Listings
"""

import csv
import io
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class CSVFormat(Enum):
    """CSV 格式类型"""
    KEYWORD_LIST = "keyword_list"
    TOP_LISTINGS = "top_listings"
    UNKNOWN = "unknown"


@dataclass
class ImportResult:
    """导入结果"""
    imported: int = 0
    skipped: int = 0
    errors: List[str] = None
    keywords: List[Dict[str, Any]] = None
    listings: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.keywords is None:
            self.keywords = []
        if self.listings is None:
            self.listings = []


class CSVImporter:
    """CSV 导入器"""
    
    # 关键词列表格式的必需列
    KEYWORD_LIST_COLUMNS = [
        "Keywords", "Average Searches", "Average Clicks", 
        "CTR", "Competition", "KD"
    ]
    
    # Top Listings 格式的必需列
    TOP_LISTINGS_COLUMNS = [
        "Keywords", "Age (Days)", "Views", "Daily Views",
        "Est. Sales", "Price", "Est. Revenue", "Hearts"
    ]
    
    def detect_format(self, file_obj: io.StringIO) -> CSVFormat:
        """
        检测 CSV 格式类型
        
        Args:
            file_obj: CSV 文件对象
            
        Returns:
            CSVFormat 枚举值
        """
        # 重置文件指针
        file_obj.seek(0)
        
        try:
            reader = csv.reader(file_obj)
            header = next(reader)
            header = [h.strip().strip('"') for h in header]
        except (StopIteration, csv.Error):
            return CSVFormat.UNKNOWN
        
        # 检查关键词列表格式
        if all(col in header for col in self.KEYWORD_LIST_COLUMNS):
            return CSVFormat.KEYWORD_LIST
        
        # 检查 Top Listings 格式
        if all(col in header for col in self.TOP_LISTINGS_COLUMNS):
            return CSVFormat.TOP_LISTINGS
        
        return CSVFormat.UNKNOWN
    
    def parse(self, file_obj: io.StringIO) -> ImportResult:
        """
        解析 CSV 文件
        
        Args:
            file_obj: CSV 文件对象
            
        Returns:
            ImportResult 导入结果
            
        Raises:
            ValueError: 无法识别的 CSV 格式
        """
        format_type = self.detect_format(file_obj)
        
        if format_type == CSVFormat.UNKNOWN:
            raise ValueError("无法识别的 CSV 格式，请检查文件是否为 eRank 导出")
        
        if format_type == CSVFormat.KEYWORD_LIST:
            return self._parse_keyword_list(file_obj)
        else:
            return self._parse_top_listings(file_obj)
    
    def _parse_keyword_list(self, file_obj: io.StringIO) -> ImportResult:
        """解析关键词列表格式"""
        file_obj.seek(0)
        reader = csv.DictReader(file_obj)
        
        result = ImportResult()
        seen_keywords = set()
        
        for row_num, row in enumerate(reader, start=2):
            try:
                keyword = row.get("Keywords", "").strip().strip('"')
                if not keyword:
                    continue
                
                # 去重
                if keyword.lower() in seen_keywords:
                    result.skipped += 1
                    continue
                seen_keywords.add(keyword.lower())
                
                # 解析数据
                keyword_data = {
                    "keyword": keyword,
                    "avg_searches": self._parse_int(row.get("Average Searches")),
                    "avg_clicks": self._parse_int(row.get("Average Clicks")),
                    "ctr": self._parse_int(row.get("CTR")),
                    "competition": self._parse_int(row.get("Competition")),
                    "kd": self._parse_kd(row.get("KD")),
                    "tag_occurrences": self._parse_int(row.get("Tag Occurrences", 0)),
                    "char_count": self._parse_int(row.get("Character Count", 0)),
                    "google_searches": self._parse_int(row.get("Google Searches", 0)),
                }
                
                result.keywords.append(keyword_data)
                result.imported += 1
                
            except Exception as e:
                result.errors.append(f"第 {row_num} 行: {str(e)}")
        
        return result
    
    def _parse_top_listings(self, file_obj: io.StringIO) -> ImportResult:
        """解析 Top Listings 格式"""
        file_obj.seek(0)
        reader = csv.DictReader(file_obj)
        
        result = ImportResult()
        
        for row_num, row in enumerate(reader, start=2):
            try:
                title = row.get("Keywords", "").strip().strip('"')
                if not title:
                    continue
                
                listing_data = {
                    "title": title,
                    "age_days": self._parse_int(row.get("Age (Days)")),
                    "views": self._parse_int(row.get("Views")),
                    "daily_views": self._parse_int(row.get("Daily Views")),
                    "est_sales": self._parse_int(row.get("Est. Sales")),
                    "price": self._parse_float(row.get("Price")),
                    "est_revenue": self._parse_float(row.get("Est. Revenue")),
                    "hearts": self._parse_int(row.get("Hearts")),
                }
                
                result.listings.append(listing_data)
                result.imported += 1
                
            except Exception as e:
                result.errors.append(f"第 {row_num} 行: {str(e)}")
        
        return result
    
    @staticmethod
    def _parse_int(value: Any) -> Optional[int]:
        """安全解析整数"""
        if value is None:
            return 0
        value = str(value).strip().strip('"').replace(",", "")
        if value == "" or value == "N/A":
            return 0
        try:
            return int(float(value))
        except ValueError:
            return 0
    
    @staticmethod
    def _parse_float(value: Any) -> Optional[float]:
        """安全解析浮点数"""
        if value is None:
            return 0.0
        value = str(value).strip().strip('"').replace(",", "")
        if value == "" or value == "N/A":
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    @staticmethod
    def _parse_kd(value: Any) -> Optional[int]:
        """解析 KD 值（可能带引号）"""
        if value is None:
            return 0
        value = str(value).strip().strip('"')
        try:
            return int(value)
        except ValueError:
            return 0
