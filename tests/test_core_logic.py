"""Core logic tests for local processing helpers.

These tests cover the most stable and important pure-function / local parts
of the codebase.  They do NOT touch the network or any external service.
"""

from pathlib import Path
import tempfile

from cleaners.format_cleaner import FormatCleaner
from cleaners.frontmatter_doctor import FrontmatterDoctor
from cleaners.markdown import MarkdownCleaner
from cleaners.text import TextCleaner
from cleaners.wechat_article import WechatArticleCleaner
from utils.dedup import DedupManager
from utils.hash import calculate_file_hash, calculate_hash


# ---------------------------------------------------------------------------
# utils/hash
# ---------------------------------------------------------------------------

def test_calculate_hash_empty_string():
    assert calculate_hash("") == ""


def test_calculate_hash_is_stable():
    assert calculate_hash("hello") == calculate_hash("hello")
    assert calculate_hash("hello") != calculate_hash("world")


def test_calculate_file_hash_matches_content(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("abc", encoding="utf-8")
    h1 = calculate_file_hash(str(p))
    assert h1
    assert calculate_file_hash(str(p)) == h1


# ---------------------------------------------------------------------------
# utils/dedup
# ---------------------------------------------------------------------------

def test_dedup_new_record_is_not_duplicate(tmp_path):
    state = tmp_path / "state.json"
    mgr = DedupManager(str(state))
    assert mgr.is_duplicate("doc-1", "hash-a") is False


def test_dedup_records_and_detects(tmp_path):
    state = tmp_path / "state.json"
    mgr = DedupManager(str(state))
    mgr.update_record("doc-1", "hash-a", {"type": "file"})
    assert mgr.is_duplicate("doc-1", "hash-a") is True
    assert mgr.is_duplicate("doc-1", "hash-b") is False
    assert mgr.get_record("doc-1")["metadata"]["type"] == "file"


def test_dedup_clear_all(tmp_path):
    state = tmp_path / "state.json"
    mgr = DedupManager(str(state))
    mgr.update_record("doc-1", "hash-a", {"type": "file"})
    mgr.clear_all()
    assert mgr.is_duplicate("doc-1", "hash-a") is False


# ---------------------------------------------------------------------------
# cleaners/format_cleaner
# ---------------------------------------------------------------------------

def test_format_cleaner_removes_css_noise():
    cleaner = FormatCleaner()
    content = "<style>.x{color:red}</style>\n正文内容"
    cleaned, stats = cleaner.clean(content)
    assert "style" not in cleaned
    assert "正文内容" in cleaned


def test_format_cleaner_fixes_heading_levels():
    cleaner = FormatCleaner()
    content = "####### Bad Heading\n正文"
    cleaned, stats = cleaner.clean(content)
    assert "Bad Heading" in cleaned
    assert "####### " not in cleaned


def test_format_cleaner_stats_lines_processed():
    cleaner = FormatCleaner()
    content = "line1\nline2\nline3"
    cleaned, stats = cleaner.clean(content)
    assert stats["lines_processed"] >= 1


# ---------------------------------------------------------------------------
# cleaners/frontmatter_doctor
# ---------------------------------------------------------------------------

def test_frontmatter_doctor_standardizes_fields_and_extracts_url():
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
    cleaned, fm, stats = doctor.standardize(
        content, {"title": "新标题", "tags": ["x", "y"]}
    )
    assert fm["title"] == "新标题"
    assert fm["author"] == "旧作者"
    assert fm["tags"] == ["x", "y"]
    assert fm["original_url"] == "https://example.com/post/1"
    assert stats["url_extracted"] is True
    assert cleaned.startswith("---\n")
    assert "原文地址" not in cleaned


def test_frontmatter_doctor_rebuilds_frontmatter():
    doctor = FrontmatterDoctor()
    content = "---\ntitle: x\n---\n正文"
    cleaned, fm, stats = doctor.standardize(content, {})
    assert cleaned.startswith("---\n")
    assert cleaned.count("---") >= 2


# ---------------------------------------------------------------------------
# cleaners/markdown
# ---------------------------------------------------------------------------

def test_markdown_cleaner_removes_front_matter():
    cleaner = MarkdownCleaner()
    content = "---\ntitle: x\n---\n正文"
    cleaned = cleaner.clean(content)
    assert "title:" not in cleaned
    assert "正文" in cleaned


def test_markdown_cleaner_normalizes_headings():
    cleaner = MarkdownCleaner()
    content = "##标题\n正文"
    cleaned = cleaner.clean(content)
    assert "## 标题" in cleaned or "# 标题" in cleaned


def test_markdown_cleaner_removes_html_comments():
    cleaner = MarkdownCleaner()
    content = "<!-- note -->正文"
    cleaned = cleaner.clean(content)
    assert "note" not in cleaned
    assert "正文" in cleaned


# ---------------------------------------------------------------------------
# cleaners/text
# ---------------------------------------------------------------------------

def test_text_cleaner_removes_marketing_and_editor_info():
    cleaner = TextCleaner()
    content = "编辑：张三\n发布时间：2026-06-16\n正文内容\n长按识别二维码关注我们"
    cleaned = cleaner.clean(content)
    assert "张三" not in cleaned
    assert "二维码" not in cleaned
    assert "正文内容" in cleaned


# ---------------------------------------------------------------------------
# cleaners/wechat_article
# ---------------------------------------------------------------------------

def test_wechat_article_cleaner_extracts_main_content():
    cleaner = WechatArticleCleaner()
    html = """<html>
      <body>
        <div id="js_content">
          <p>第一段</p>
          <p>第二段</p>
        </div>
        <div class="article_comment">评论区</div>
      </body>
    </html>"""
    cleaned = cleaner.clean(html)
    assert "第一段" in cleaned
    assert "第二段" in cleaned
    assert "评论区" not in cleaned
