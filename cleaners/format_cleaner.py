"""
Stage 1: Format Cleaner (参考 baoyu-format-markdown)

职责：
- 清理残留的 CSS 样式
- 修复混乱的标题层级
- 移除各种格式噪音
- 清理空链接和图片
"""

import re
from typing import List, Tuple


class FormatCleaner:
    """第一阶段：格式清理器"""
    
    # CSS 残留模式
    CSS_PATTERNS = [
        (r'\{[^}]*\}', 'CSS 块'),  # {property: value}
        (r'<!--\s*[\w\s:;#-]+-->', 'CSS 注释'),  # <!-- CSS comments -->
        (r'<style[^>]*>.*?</style>', 'style 标签'),  # <style> blocks
        (r'class="[^"]*"', 'class 属性'),  # class attributes
        (r'style="[^"]*"', 'style 属性'),  # style attributes
        (r'data-[\w-]+="[^"]*"', 'data 属性'),  # data-* attributes
    ]
    
    # 格式噪音模式
    NOISE_PATTERNS = [
        (r'\*{4,}', '过多星号'),  # **** or more
        (r'_{4,}', '过多下划线'),  # ____ or more
        (r'#{7,}', '无效标题'),  # ####### or more (invalid heading)
        (r'\[.*?\]\(#\)', '空链接'),  # Empty links
        (r'!\[.*?\]\(\)', '空图片'),  # Empty images
        (r'<br\s*/?>', 'HTML 换行'),  # <br> tags
        (r'&nbsp;', 'HTML 空格'),  # &nbsp;
        (r'&lt;', '<'),  # HTML 实体
        (r'&gt;', '>'),  # HTML 实体
        (r'&amp;', '&'),  # HTML 实体
    ]
    
    # 微信特有的噪音
    WECHAT_NOISE_PATTERNS = [
        (r'!\[.*?\]\(data:image/[^)]+\)', '内联图片'),  # Inline base64 images
        (r'<img[^>]*>', 'img 标签'),  # <img> tags
        (r'<div[^>]*>', 'div 标签'),  # <div> tags
        (r'</div>', 'div 结束标签'),  # </div> tags
        (r'<span[^>]*>', 'span 标签'),  # <span> tags
        (r'</span>', 'span 结束标签'),  # </span> tags
        (r'<p[^>]*>', 'p 标签'),  # <p> tags
        (r'</p>', 'p 结束标签'),  # </p> tags
    ]
    
    def __init__(self):
        self.stats = {
            'css_removed': 0,
            'noise_removed': 0,
            'headings_fixed': 0,
            'lines_processed': 0
        }
    
    def clean(self, content: str) -> Tuple[str, dict]:
        """
        清理 Markdown 格式
        
        Args:
            content: 原始 Markdown 内容
            
        Returns:
            (清理后的内容, 统计信息)
        """
        self.stats = {
            'css_removed': 0,
            'noise_removed': 0,
            'headings_fixed': 0,
            'lines_processed': 0
        }
        
        # 按行处理
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            self.stats['lines_processed'] += 1
            
            # 跳过空行
            if not line.strip():
                cleaned_lines.append('')
                continue
            
            # 清理 CSS 残留
            cleaned_line = self._remove_css(line)
            
            # 检测并跳过格式噪音
            if self._is_noise(cleaned_line):
                self.stats['noise_removed'] += 1
                continue
            
            # 修复标题层级
            cleaned_line = self._fix_heading(cleaned_line)
            
            # 清理微信特有噪音
            cleaned_line = self._remove_wechat_noise(cleaned_line)
            
            cleaned_lines.append(cleaned_line)
        
        # 合并连续空行（最多保留 1 个）
        content = '\n'.join(cleaned_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip(), self.stats
    
    def _remove_css(self, line: str) -> str:
        """清理 CSS 残留"""
        for pattern, desc in self.CSS_PATTERNS:
            matches = re.findall(pattern, line)
            if matches:
                self.stats['css_removed'] += len(matches)
                line = re.sub(pattern, '', line)
        return line.strip()
    
    def _is_noise(self, line: str) -> bool:
        """检测格式噪音"""
        for pattern, desc in self.NOISE_PATTERNS:
            if re.search(pattern, line):
                return True
        return False
    
    def _remove_wechat_noise(self, line: str) -> str:
        """清理微信特有噪音"""
        for pattern, desc in self.WECHAT_NOISE_PATTERNS:
            matches = re.findall(pattern, line)
            if matches:
                self.stats['noise_removed'] += len(matches)
                line = re.sub(pattern, '', line)
        return line.strip()
    
    def _fix_heading(self, line: str) -> str:
        """修复标题层级"""
        # 匹配标题
        match = re.match(r'^(#{1,10})\s+(.+)$', line)
        if not match:
            return line
        
        level = len(match.group(1))
        text = match.group(2).strip()
        
        # 修复过多 # 号（限制为 1-6）
        if level > 6:
            level = 6
            self.stats['headings_fixed'] += 1
        
        # 修复标题文本中的多余空格
        text = ' '.join(text.split())
        
        return f"{'#' * level} {text}"
