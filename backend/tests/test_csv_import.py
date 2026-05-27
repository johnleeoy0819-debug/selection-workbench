"""
CSV 导入模块测试
验证 eRank CSV 解析逻辑
"""

import pytest
from io import StringIO
from services.csv_importer import CSVImporter, CSVFormat


class TestCSVImporter:
    """测试 CSV 导入器"""

    def test_detect_keyword_list_format(self):
        """测试识别关键词列表格式"""
        csv_content = '''"Keywords","Average Searches","Average Clicks","CTR","Competition","KD","Tag Occurrences","Character Count","Google Searches"
"hook",922,1199,130,337453,"100","10","4",201000
"wall hook",2067,2204,107,61524,"74","0","9",22200'''
        
        importer = CSVImporter()
        format_type = importer.detect_format(StringIO(csv_content))
        assert format_type == CSVFormat.KEYWORD_LIST

    def test_detect_top_listings_format(self):
        """测试识别 Top Listings 格式"""
        csv_content = '''"Keywords","Age (Days)","Views","Daily Views","Est. Sales","Price","Est. Revenue","Hearts"
"Bamboo Wall Key Holder",48,4,1,0,112,0,0'''
        
        importer = CSVImporter()
        format_type = importer.detect_format(StringIO(csv_content))
        assert format_type == CSVFormat.TOP_LISTINGS

    def test_parse_keyword_list(self):
        """测试解析关键词列表"""
        csv_content = '''"Keywords","Average Searches","Average Clicks","CTR","Competition","KD","Tag Occurrences","Character Count","Google Searches"
"wall hook",2067,2204,107,61524,"74","0","9",22200
"coat hook",1135,1137,100,16636,"58","3","9",12100'''
        
        importer = CSVImporter()
        result = importer.parse(StringIO(csv_content))
        
        assert result.imported == 2
        assert result.skipped == 0
        assert len(result.keywords) == 2
        
        # 验证第一条数据
        kw = result.keywords[0]
        assert kw["keyword"] == "wall hook"
        assert kw["avg_searches"] == 2067
        assert kw["kd"] == 74

    def test_parse_top_listings(self):
        """测试解析 Top Listings"""
        csv_content = '''"Keywords","Age (Days)","Views","Daily Views","Est. Sales","Price","Est. Revenue","Hearts"
"Bamboo Wall Key Holder",48,4,1,0,112,0,0'''
        
        importer = CSVImporter()
        result = importer.parse(StringIO(csv_content))
        
        assert result.imported == 1
        assert len(result.listings) == 1
        
        listing = result.listings[0]
        assert listing["title"] == "Bamboo Wall Key Holder"
        assert listing["price"] == 112.0

    def test_skip_duplicate_keywords(self):
        """测试跳过重复关键词"""
        csv_content = '''"Keywords","Average Searches","Average Clicks","CTR","Competition","KD"
"wall hook",2067,2204,107,61524,"74"
"wall hook",2067,2204,107,61524,"74"'''
        
        importer = CSVImporter()
        result = importer.parse(StringIO(csv_content))
        
        assert result.imported == 1
        assert result.skipped == 1

    def test_handle_invalid_csv(self):
        """测试处理无效 CSV"""
        csv_content = "invalid,csv,content\n1,2,3"
        
        importer = CSVImporter()
        
        with pytest.raises(ValueError):
            importer.parse(StringIO(csv_content))

    def test_handle_empty_file(self):
        """测试处理空文件"""
        csv_content = '"Keywords","Average Searches","Average Clicks","CTR","Competition","KD"'
        
        importer = CSVImporter()
        result = importer.parse(StringIO(csv_content))
        
        assert result.imported == 0
        assert result.skipped == 0
