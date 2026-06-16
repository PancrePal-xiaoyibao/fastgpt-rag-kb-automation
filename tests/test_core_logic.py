"""Core logic tests for local processing helpers."""

from pathlib import Path
import tempfile

from cleaners.format_cleaner import FormatCleaner
from cleaners.frontmatter_doctor import FrontmatterDoctor
from cleaners.markdown import MarkdownCleaner
from cleaners.text import TextCleaner
from cleaners.wechat_article import WechatArticleCleaner
from utils.dedup import DedupManager
from utils.hash import calculate_file_hash, calculate_hash


def test_calculate_hash_is_stable_and_handles_empty_input():
    assert calculate_hash("") == ""
    assert calculate_hash("hello") == calculate_hash("hello")
    assert calculate_hash("hello") != calculate_hash("world")


def test_calculate_file_hash_matches_file_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sample.txt"
        path.write_text("abc", encoding="utf-8")

        assert calculate_file_hash(str(path))
        assert calculate_file_hash(str(path)) == calculate_file_hash(str(path))


def test_dedup_manager_records_and_detects_duplicates():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.json"
        manager = DedupManager(str(state_file))

        assert manager.is_duplicate("doc-1", "hash-a") is False
        manager.update_record("doc-1", "hash-a", {"type": "file"})
        assert manager.is_duplicate("doc-1", "hash-a") is True
        assert manager.is_duplicate("doc-1", "hash-b") is False
        assert manager.get_record("doc-1")["metadata"]["type"] == "file"

        manager.clear_all()
        assert manager.is_duplicate("doc-1", "hash-a") is False


def test_format_cleaner_removes_noise_and_fixes_heading_levels():
    cleaner = FormatCleaner()
    content = """<style>.x{color:red}</style>
####### Bad Heading
普通内容
\n\n![img](data:image/png;base64,abc)
"""
    cleaned, stats = cleaner.clean(content)

    assert "style" not in cleaned
    assert "Bad Heading" in cleaned or "# Bad Heading" in cleaned
    assert stats["lines_processed"] >= 1


def test_frontmatter_doctor_standardizes_core_fields_and_extracts_url():
    doctor = FrontmatterDoctor()
    content = """---
title: 原标题
author: 旧作者
summary: 旧摘要
description: <p>旧描述</p>
tags:
  - a
---

# 标题
正文内容
原文地址：https://example.com/post/1
"""

    cleaned, fm, stats = doctor.standardize(content, {"title": "新标题", "tags": ["x", "y"]})

    assert fm["title"] == "新标题"
    assert fm["author"] == "旧作者"
    assert fm["tags"] == ["x", "y"]
    assert fm["original_url"] == "https://example.com/post/1"
    assert stats["url_extracted"] is True
    assert cleaned.startswith("---\n")
    assert "原文地址" not in cleaned


def test_markdown_cleaner_removes_front_matter_and_normalizes_headings():
    cleaner = MarkdownCleaner()
    content = """---
title: x
---

##标题
<!-- note -->
正文
"""
    cleaned = cleaner.clean(content)

    assert "title:" not in cleaned
    assert "## 标题" in cleaned or "# 标题" in cleaned
    assert "note" not in cleaned


def test_text_cleaner_removes_marketing_and_editor_info():
    cleaner = TextCleaner()
    content = """编辑：张三
发布时间：2026-06-16
正文内容
长按识别二维码关注我们
"""
    cleaned = cleaner.clean(content)

    assert "张三" not in cleaned
    assert "二维码" not in cleaned
    assert "正文内容" in cleaned


def test_wechat_article_cleaner_extracts_main_content_from_html():
    cleaner = WechatArticleCleaner()
    html = """
    <html>
      <body>
        <div id="js_content">
          <p>第一段</p>
          <p>第二段</p>
        </div>
        <div class="article_comment">评论区</div>
      </body>
    </html>
    """

    cleaned = cleaner.clean(html)
    assert "第一段" in cleaned
    assert "第二段" in cleaned
    assert "评论区" not in cleaned
