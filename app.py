#!/usr/bin/env python3
"""Books Database Explorer — Streamlit frontend (v2 redesign)."""

import os
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, List
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("BOOKS_DB_PATH", BASE_DIR / "database" / "books.db"))

st.set_page_config(
    page_title="Books Database Explorer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    "en": {
        "app_title": "Books Database Explorer",
        "db_caption": "Database: {path}",
        "app_subtitle": "Explore a curated collection from Goodreads — the world's largest reading community, where over 150 million readers share reviews, ratings, and recommendations.",
        "language_label": "Language / 语言",
        "lang_english": "English",
        "lang_chinese": "中文",
        "page": "Navigation",
        "page_search": "🔍  Filtered Search",
        "page_explore": "🧭  Explore",
        "page_analytics": "📊  Analytics",
        "page_reading_list": "📚  Reading List",
        "no_data": "No data found for current filters.",
        "title_keyword": "Title keyword",
        "title_keyword_placeholder": "e.g. Harry Potter",
        "google_fallback_title": "🌐  Can't find your book? Search Open Library directly",
        "google_fallback_hint": "If the local database doesn't include your book, enter a title and search in Open Library.",
        "google_fallback_input": "Book title",
        "google_fallback_placeholder": "e.g. The Name of the Wind",
        "google_fallback_author_input": "Author (optional)",
        "google_fallback_author_placeholder": "e.g. Patrick Rothfuss",
        "google_fallback_button": "Search Open Library",
        "google_fallback_empty": "Please enter a book title.",
        "google_fallback_loading": "Searching Open Library …",
        "google_fallback_no_result": "No matching book found on Open Library.",
        "openlib_import_button": "Quick Import To Local DB",
        "openlib_imported": "Imported to local database (ID {book_id}).",
        "openlib_import_exists": "This book already exists in local database (ID {book_id}).",
        "openlib_import_failed": "Import failed: {reason}",
        "close_detail_panel": "← Close details",
        "detail_panel_closed": "Details panel closed for this row. Select another row to open.",
        "publish_year": "Publish year",
        "rating": "Rating",
        "result_limit": "Result limit",
        "explore_by": "Explore by",
        "explore_author": "✍️ Author",
        "explore_publisher": "🏢 Publisher",
        "explore_author_hint": "Select an author to see all their books.",
        "explore_publisher_hint": "Select a publisher to see all books they published.",
        "select_author": "Select author",
        "select_publisher": "Select publisher",
        "author_placeholder": "Type to search authors …",
        "publisher_placeholder": "Type to search publishers …",
        "author_stats": "{count} books · avg ⭐ {rating}",
        "publisher_stats": "{count} books from this publisher",
        "metric_books": "Books",
        "metric_authors": "Authors",
        "metric_publishers": "Publishers",
        "metric_avg_rating": "Weighted Avg Rating",
        "metric_median_rating": "Median Rating",
        "top_publishers": "🏢 Top Publishers by Book Count",
        "top_authors": "Top Authors by Average Rating (≥ 5 books)",
        "books_by_year": "📈 Books by Publish Year",
        "rating_distribution": "⭐ Rating Distribution (book count)",
        "rating_volume_distribution": "🔥 Rating Distribution (rating volume)",
        "db_not_found": "Database file not found. Run load script first.",
        "nav_hint": "Pick a page, then use filters to drill down.",
        "search_hint": "Combine title, year, rating, and language filters.",
        "explore_hint": "Drill into a specific author or publisher to discover books.",
        "analytics_hint": "Use visual summaries to understand distribution, coverage, and trends.",
        "reading_list_hint": "Track your reading status, export reading progress, and maintain the book catalog.",
        "filter_panel": "⚙️  Filters",
        "results_panel": "📋  Results",
        "tab_my_reading": "📖 My Reading",
        "tab_manage_books": "🛠️ Manage Books",
        "reading_add_section": "➕ Add Or Update Reading Entry",
        "reading_export_section": "📤 Export Reading Data",
        "reading_table_section": "📋 Reading Entries",
        "reading_status": "Reading Status",
        "status_want_to_read": "Want to Read",
        "status_reading": "Reading",
        "status_completed": "Completed",
        "status_dropped": "Dropped",
        "my_rating": "My Rating (Optional)",
        "set_my_rating": "Set personal rating",
        "set_finished_date": "Set finished date",
        "finished_date": "Finished Date",
        "reading_notes": "Notes",
        "reading_search": "Book title keyword",
        "reading_search_placeholder": "Type a title to quickly find books",
        "select_book_for_reading": "Select book",
        "save_reading_entry": "Save Reading Entry",
        "delete_reading_entry": "Delete Reading Entry",
        "select_reading_entry": "Select reading entry",
        "reading_saved": "Reading entry saved.",
        "reading_deleted": "Reading entry deleted.",
        "reading_export": "Download Reading CSV",
        "reading_export_hint": "Export includes title, authors, status, personal rating, notes, and timestamps.",
        "reading_export_ready": "{count} rows ready for export",
        "status_breakdown": "Status breakdown",
        "completed_date_hint": "Completed status usually should include a finished date.",
        "book_admin_hint": "Add, edit, and delete books. Required fields are marked with * and validated before saving.",
        "book_add_section": "➕ Add Book",
        "book_edit_section": "✏️ Edit Or Delete Book",
        "book_title": "Book Title",
        "book_authors_input": "Authors",
        "book_authors_placeholder": "Use commas to separate multiple authors",
        "book_language_input": "Language",
        "book_publisher_input": "Publisher",
        "book_isbn_input": "ISBN",
        "book_isbn13_input": "ISBN13",
        "book_pages_input": "Pages",
        "book_num_ratings_input": "Ratings Count",
        "book_reviews_count_input": "Text Reviews Count",
        "book_publish_year_input": "Publish Year",
        "book_rating_input": "Rating",
        "book_search": "Book keyword",
        "book_search_placeholder": "Search title to edit or delete",
        "select_existing_book": "Select existing book",
        "add_book_btn": "Add Book",
        "update_book_btn": "Update Book",
        "delete_book_btn": "Delete Book",
        "confirm_delete_book": "I confirm deleting this book and all related records.",
        "book_added": "Book added successfully.",
        "book_updated": "Book updated successfully.",
        "book_deleted": "Book deleted.",
        "required_field_missing": "Please fill in all required fields.",
        "invalid_authors": "Please enter at least one valid author.",
        "invalid_year": "Publish year must be between 1800 and 2030.",
        "invalid_rating": "Rating must be between 0 and 5.",
        "invalid_integer": "{field} must be an integer.",
        "invalid_positive": "{field} must be greater than 0.",
        "invalid_nonnegative": "{field} must be greater than or equal to 0.",
        "invalid_isbn13": "ISBN13 must contain digits only.",
        "confirm_delete_required": "Please check the confirmation box before deleting.",
        "rows_returned": "{count} rows returned",
        "hero_badge_dataset": "11 K books",
        "hero_badge_bilingual": "Bilingual UI",
        "hero_badge_sqlite": "SQLite normalized",
        "hero_badge_charts": "Interactive charts",
        "theme_light": "☀️ Light",
        "theme_dark": "🌙 Dark",
        "language_dist": "🌐 Language Distribution (Top 10)",
        "pages_vs_rating": "📚 Pages vs Rating (sampled)",
        "top_authors_scatter": "🎯 Author Productivity vs Rating",
        "rating_weight_delta": "vs unweighted {value}",
        "books_yoy_change": "Year-over-year Change",
        "book_detail": "📖  Book Detail",
        "select_book_hint": "Select a row to view richer details from Open Library",
        "select_book": "Select a book to view details",
        "book_by": "Author: {authors}",
        "book_publisher": "Publisher",
        "book_source": "Source",
        "book_pages": "Pages",
        "book_published": "Published",
        "book_isbn": "ISBN",
        "book_categories": "Categories",
        "book_preview": "View on Open Library",
        "book_description": "Description",
        "book_no_result": "No results found on Open Library for this title.",
        "book_api_error": "Could not connect to Open Library API.",
        "book_api_error_with_reason": "Could not connect to Open Library API: {reason}",
        "book_loading": "Looking up on Open Library …",
        "rating_compare": "Rating Comparison",
        "rating_goodreads": "Goodreads",
        "rating_google": "Open Library",
        "rating_people": "{count} ratings",
        "review_sites": "Quick Links",
        "filter_language": "Language",
        "all_languages": "All",
        "unknown_author": "Unknown",
        "pages_unit_short": "p.",
        "nav_brand": "📚 Books Explorer",
        "footer_built_with": "Built with Streamlit · SQLite · Python",
    },
    "zh": {
        "app_title": "图书数据库浏览器",
        "db_caption": "数据库文件：{path}",
        "app_subtitle": "探索来自 Goodreads 的精选书库 —— 全球最大的读书社区，超过 1.5 亿读者在此分享书评、评分与推荐。",
        "language_label": "语言 / Language",
        "lang_english": "English",
        "lang_chinese": "中文",
        "page": "导航",
        "page_search": "🔍  条件查询",
        "page_explore": "🧭  探索",
        "page_analytics": "📊  统计分析",
        "page_reading_list": "📚  书单管理",
        "no_data": "当前筛选条件下没有数据。",
        "title_keyword": "书名关键词",
        "title_keyword_placeholder": "例如：哈利·波特",
        "google_fallback_title": "🌐  没有你想要的书籍？请直接输入书名在 Open Library 中搜索",
        "google_fallback_hint": "如果本地数据库里没有你想要的书，可以直接输入书名调用 Open Library 搜索。",
        "google_fallback_input": "书名",
        "google_fallback_placeholder": "例如：活着",
        "google_fallback_author_input": "作者（可选）",
        "google_fallback_author_placeholder": "例如：余华",
        "google_fallback_button": "搜索 Open Library",
        "google_fallback_empty": "请输入书名。",
        "google_fallback_loading": "正在搜索 Open Library …",
        "google_fallback_no_result": "Open Library 中未找到匹配结果。",
        "openlib_import_button": "快捷导入到本地数据库",
        "openlib_imported": "已导入本地数据库（ID {book_id}）。",
        "openlib_import_exists": "该书已存在于本地数据库（ID {book_id}）。",
        "openlib_import_failed": "导入失败：{reason}",
        "close_detail_panel": "← 关闭详情",
        "detail_panel_closed": "该行详情已关闭，选择其它行可重新打开。",
        "publish_year": "出版年份",
        "rating": "评分",
        "result_limit": "结果上限",
        "explore_by": "探索方式",
        "explore_author": "✍️ 按作者",
        "explore_publisher": "🏢 按出版社",
        "explore_author_hint": "选择一位作者，查看其所有作品。",
        "explore_publisher_hint": "选择一个出版社，查看其所有出版图书。",
        "select_author": "选择作者",
        "select_publisher": "选择出版社",
        "author_placeholder": "输入作者姓名搜索 …",
        "publisher_placeholder": "输入出版社名称搜索 …",
        "author_stats": "{count} 本书 · 平均 ⭐ {rating}",
        "publisher_stats": "该出版社共 {count} 本书",
        "metric_books": "图书数",
        "metric_authors": "作者数",
        "metric_publishers": "出版社数",
        "metric_avg_rating": "加权平均评分",
        "metric_median_rating": "评分中位数",
        "top_publishers": "🏢 热门出版社（按图书数量）",
        "top_authors": "高分作者（≥ 5 本书）",
        "books_by_year": "📈 各年份图书数量",
        "rating_distribution": "⭐ 评分分布（按书本数）",
        "rating_volume_distribution": "🔥 评分分布（按评分人数）",
        "db_not_found": "未找到数据库文件，请先运行导入脚本。",
        "nav_hint": "选择页面，再用筛选条件细化。",
        "search_hint": "可组合书名、年份、评分条件检索。",
        "explore_hint": "深入某个作者或出版社，发现更多图书。",
        "analytics_hint": "用可视化摘要理解数据分布与覆盖。",
        "reading_list_hint": "记录阅读状态、导出阅读进度，并维护图书目录。",
        "filter_panel": "⚙️  筛选条件",
        "results_panel": "📋  查询结果",
        "tab_my_reading": "📖 我的阅读",
        "tab_manage_books": "🛠️ 图书维护",
        "reading_add_section": "➕ 新增或更新阅读记录",
        "reading_export_section": "📤 导出阅读数据",
        "reading_table_section": "📋 阅读记录",
        "reading_status": "阅读状态",
        "status_want_to_read": "想读",
        "status_reading": "在读",
        "status_completed": "已读完",
        "status_dropped": "已弃读",
        "my_rating": "我的评分（可选）",
        "set_my_rating": "设置个人评分",
        "set_finished_date": "设置完成日期",
        "finished_date": "完成日期",
        "reading_notes": "备注",
        "reading_search": "书名关键词",
        "reading_search_placeholder": "输入书名快速检索",
        "select_book_for_reading": "选择图书",
        "save_reading_entry": "保存阅读记录",
        "delete_reading_entry": "删除阅读记录",
        "select_reading_entry": "选择阅读记录",
        "reading_saved": "阅读记录已保存。",
        "reading_deleted": "阅读记录已删除。",
        "reading_export": "下载阅读 CSV",
        "reading_export_hint": "导出包含书名、作者、阅读状态、个人评分、备注与更新时间。",
        "reading_export_ready": "可导出 {count} 行数据",
        "status_breakdown": "状态分布",
        "completed_date_hint": "当状态为“已读完”时，建议填写完成日期。",
        "book_admin_hint": "支持新增、编辑、删除图书。带 * 的字段为必填，保存前会做规范校验。",
        "book_add_section": "➕ 新增图书",
        "book_edit_section": "✏️ 编辑或删除图书",
        "book_title": "书名",
        "book_authors_input": "作者",
        "book_authors_placeholder": "多个作者请使用逗号分隔",
        "book_language_input": "语言",
        "book_publisher_input": "出版社",
        "book_isbn_input": "ISBN",
        "book_isbn13_input": "ISBN13",
        "book_pages_input": "页数",
        "book_num_ratings_input": "评分人数",
        "book_reviews_count_input": "评论数",
        "book_publish_year_input": "出版年份",
        "book_rating_input": "评分",
        "book_search": "图书关键词",
        "book_search_placeholder": "输入书名用于编辑或删除",
        "select_existing_book": "选择已有图书",
        "add_book_btn": "新增图书",
        "update_book_btn": "更新图书",
        "delete_book_btn": "删除图书",
        "confirm_delete_book": "我确认删除该图书及相关记录。",
        "book_added": "图书新增成功。",
        "book_updated": "图书更新成功。",
        "book_deleted": "图书已删除。",
        "required_field_missing": "请填写所有必填字段。",
        "invalid_authors": "请至少填写一位有效作者。",
        "invalid_year": "出版年份必须在 1800 到 2030 之间。",
        "invalid_rating": "评分必须在 0 到 5 之间。",
        "invalid_integer": "{field} 必须是整数。",
        "invalid_positive": "{field} 必须大于 0。",
        "invalid_nonnegative": "{field} 必须大于或等于 0。",
        "invalid_isbn13": "ISBN13 只能包含数字。",
        "confirm_delete_required": "删除前请先勾选确认。",
        "rows_returned": "返回 {count} 行",
        "hero_badge_dataset": "1.1 万本图书",
        "hero_badge_bilingual": "中英双语",
        "hero_badge_sqlite": "SQLite 规范化",
        "hero_badge_charts": "交互图表",
        "theme_light": "☀️ 浅色",
        "theme_dark": "🌙 深色",
        "language_dist": "🌐 语言分布（前 10）",
        "pages_vs_rating": "📚 页数 vs 评分（采样）",
        "top_authors_scatter": "🎯 作者产量与评分分布",
        "rating_weight_delta": "对比未加权 {value}",
        "books_yoy_change": "同比变化",
        "book_detail": "📖  图书详情",
        "select_book_hint": "点击表格中的行，即可查看来自 Open Library 的详细信息",
        "select_book": "选择一本书查看详情",
        "book_by": "作者：{authors}",
        "book_publisher": "出版社",
        "book_source": "来源",
        "book_pages": "页数",
        "book_published": "出版日期",
        "book_isbn": "ISBN",
        "book_categories": "分类",
        "book_preview": "在 Open Library 中查看",
        "book_description": "简介",
        "book_no_result": "未在 Open Library 中找到该书。",
        "book_api_error": "无法连接 Open Library API。",
        "book_api_error_with_reason": "无法连接 Open Library API：{reason}",
        "book_loading": "正在查询 Open Library …",
        "rating_compare": "评分对比",
        "rating_goodreads": "Goodreads",
        "rating_google": "Open Library",
        "rating_people": "{count} 人评分",
        "review_sites": "快捷搜索",
        "filter_language": "语言",
        "all_languages": "全部",
        "unknown_author": "未知作者",
        "pages_unit_short": "页",
        "nav_brand": "📚 图书浏览器",
        "footer_built_with": "基于 Streamlit · SQLite · Python 构建",
    },
}

COLUMN_LABELS = {
    "en": {
        "title": "Title", "publish_year": "Year", "rating": "Rating",
        "num_ratings": "Ratings", "language": "Language", "pages": "Pages",
        "book_count": "Book Count", "rating_bucket": "Rating",
        "count": "Count", "books_count": "Books",
        "publisher_name": "Publisher", "author_name": "Author",
        "avg_rating": "Avg Rating", "authors": "Authors",
        "text_reviews_count": "Reviews",
        "ratings_volume": "Rating Volume",
        "yearly_change_pct": "YoY %",
        "books_count_rolling": "5Y Avg",
        "status": "Status",
        "personal_rating": "My Rating",
        "finished_date": "Finished Date",
        "notes": "Notes",
        "updated_at": "Updated At",
    },
    "zh": {
        "title": "书名", "publish_year": "出版年份", "rating": "评分",
        "num_ratings": "评分数", "language": "语言", "pages": "页数",
        "book_count": "书籍数量", "rating_bucket": "评分区间",
        "count": "数量", "books_count": "书籍数量",
        "publisher_name": "出版社", "author_name": "作者",
        "avg_rating": "平均评分", "authors": "作者",
        "text_reviews_count": "评论数",
        "ratings_volume": "评分人数",
        "yearly_change_pct": "同比%",
        "books_count_rolling": "5年均值",
        "status": "阅读状态",
        "personal_rating": "我的评分",
        "finished_date": "完成日期",
        "notes": "备注",
        "updated_at": "更新时间",
    },
}


def _col(name: str, lang: str) -> str:
    return COLUMN_LABELS.get(lang, COLUMN_LABELS["en"]).get(name, name)


def _rename_df(df, lang: str):
    mapping = COLUMN_LABELS.get(lang, {})
    return df.rename(columns=mapping) if mapping else df


def _rename_rows(rows: List[dict], lang: str) -> List[dict]:
    mapping = COLUMN_LABELS.get(lang, {})
    if not mapping:
        return rows
    return [{mapping.get(k, k): v for k, v in row.items()} for row in rows]


READING_STATUS = ["want_to_read", "reading", "completed", "dropped"]


def reading_status_options(t) -> List[tuple[str, str]]:
    return [(code, t(f"status_{code}")) for code in READING_STATUS]


def reading_status_label(status: str, t) -> str:
    labels = dict(reading_status_options(t))
    return labels.get(status, status)


def parse_author_names(authors_text: str) -> List[str]:
    parts = re.split(r"[,/;\n]+", authors_text or "")
    clean_parts = []
    seen = set()
    for raw in parts:
        name = raw.strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        clean_parts.append(name)
    return clean_parts


OPENLIB_LANGUAGE_NAMES = {
    "eng": "English",
    "en": "English",
    "chi": "Chinese",
    "zho": "Chinese",
    "fre": "French",
    "fra": "French",
    "ger": "German",
    "deu": "German",
    "ita": "Italian",
    "jpn": "Japanese",
    "spa": "Spanish",
    "rus": "Russian",
    "por": "Portuguese",
    "ara": "Arabic",
}


def normalize_openlib_language(codes: Any) -> str | None:
    if not isinstance(codes, list) or not codes:
        return None

    def _extract_lang_code(raw: Any) -> str | None:
        if isinstance(raw, dict):
            key = raw.get("key")
            if isinstance(key, str):
                raw = key
        if not isinstance(raw, str):
            return None
        text = raw.strip().lower()
        if not text:
            return None
        # Supports formats like "eng", "/languages/eng", "http://.../languages/eng"
        if "/languages/" in text:
            text = text.split("/languages/")[-1]
        text = text.split("/")[-1]
        return text or None

    for raw in codes:
        code = _extract_lang_code(raw)
        if not code:
            continue
        if code in OPENLIB_LANGUAGE_NAMES:
            return OPENLIB_LANGUAGE_NAMES[code]
        return code
    return None


def parse_year_from_text(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    m = re.search(r"(18\d{2}|19\d{2}|20[0-2]\d|2030)", text)
    if not m:
        return None
    try:
        year = int(m.group(1))
    except ValueError:
        return None
    if 1800 <= year <= 2030:
        return year
    return None


def parse_optional_int(value: str, field_label: str, t, *, positive: bool = False, nonnegative: bool = False) -> tuple[int | None, List[str]]:
    text = (value or "").strip()
    if not text:
        return None, []
    if not re.fullmatch(r"-?\d+", text):
        return None, [t("invalid_integer", field=field_label)]
    parsed = int(text)
    if positive and parsed <= 0:
        return None, [t("invalid_positive", field=field_label)]
    if nonnegative and parsed < 0:
        return None, [t("invalid_nonnegative", field=field_label)]
    return parsed, []


def sanitize_book_payload(
    *,
    title: str,
    authors_text: str,
    publish_year: int,
    rating: float,
    language: str,
    pages_text: str,
    num_ratings_text: str,
    reviews_text: str,
    publisher: str,
    isbn: str,
    isbn13_text: str,
    t,
) -> tuple[dict | None, List[str]]:
    errors: List[str] = []

    clean_title = (title or "").strip()
    clean_language = (language or "").strip()
    clean_publisher = (publisher or "").strip() or None
    clean_isbn = (isbn or "").strip() or None

    authors = parse_author_names(authors_text)
    if not clean_title or not clean_language:
        errors.append(t("required_field_missing"))
    if not authors:
        errors.append(t("invalid_authors"))

    if publish_year < 1800 or publish_year > 2030:
        errors.append(t("invalid_year"))
    if rating < 0 or rating > 5:
        errors.append(t("invalid_rating"))

    pages, page_errors = parse_optional_int(
        pages_text, t("book_pages_input"), t, positive=True
    )
    num_ratings, ratings_errors = parse_optional_int(
        num_ratings_text, t("book_num_ratings_input"), t, nonnegative=True
    )
    text_reviews_count, review_errors = parse_optional_int(
        reviews_text, t("book_reviews_count_input"), t, nonnegative=True
    )
    errors.extend(page_errors + ratings_errors + review_errors)

    isbn13_clean = (isbn13_text or "").strip()
    if isbn13_clean and not isbn13_clean.isdigit():
        errors.append(t("invalid_isbn13"))
        isbn13 = None
    else:
        isbn13 = int(isbn13_clean) if isbn13_clean else None

    if errors:
        return None, errors

    payload = {
        "title": clean_title,
        "language": clean_language,
        "publish_year": int(publish_year),
        "rating": float(rating),
        "pages": pages,
        "num_ratings": num_ratings,
        "text_reviews_count": text_reviews_count,
        "publisher_name": clean_publisher,
        "isbn": clean_isbn,
        "isbn13": isbn13,
        "authors": authors,
    }
    return payload, []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_text_fn(lang: str):
    def t(key: str, **kwargs: Any) -> str:
        text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(
            key, TRANSLATIONS["en"].get(key, key)
        )
        return text.format(**kwargs) if kwargs else text
    return t


# ---------------------------------------------------------------------------
# Theme injection (CSS)
# ---------------------------------------------------------------------------
def inject_theme() -> None:
    vars_block = """
    --bg-0: #0a0f1a;
    --bg-1: #111927;
    --panel: rgba(17, 25, 39, 0.78);
    --panel-solid: #151f30;
    --ink: #e8f0f8;
    --ink-secondary: #a3b8cc;
    --muted: #8499ae;
    --accent: #22d3a7;
    --accent-alt: #f0a040;
    --line: #243248;
    --hero-bg: linear-gradient(135deg, rgba(34, 211, 167, 0.14) 0%, rgba(240, 160, 64, 0.12) 100%);
    --hero-border: rgba(34, 211, 167, 0.25);
    --badge-border: rgba(34, 211, 167, 0.35);
    --badge-ink: #a0f4dd;
    --badge-bg: rgba(34, 211, 167, 0.12);
    --tab-bg: rgba(17, 25, 39, 0.85);
    --input-bg: rgba(15, 22, 35, 0.9);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.18);
    --shadow: 0 8px 32px rgba(0,0,0,0.25);
    --shadow-lg: 0 16px 48px rgba(0,0,0,0.32);
    --table-bg: #131c2b;
    --table-header-bg: #1a2638;
    --table-cell-bg: #131c2b;
    --table-cell-text: #dce8f3;
    --table-border: #253448;
    --card-hover: rgba(34, 211, 167, 0.06);
    --divider: linear-gradient(90deg, transparent, var(--accent), transparent);
    """
    background_block = """
        radial-gradient(ellipse 900px 500px at 90% -5%, rgba(34, 211, 167, 0.18) 0%, transparent 70%),
        radial-gradient(ellipse 800px 500px at -5% 105%, rgba(240, 160, 64, 0.10) 0%, transparent 70%),
        linear-gradient(155deg, var(--bg-0), var(--bg-1))
        """
    sidebar_bg = "rgba(14, 22, 33, 0.88)"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:root {{
{vars_block}
}}

/* === Global === */
html, body, [data-testid="stAppViewContainer"] {{
    color: var(--ink);
    background: {background_block};
}}
[data-testid="stHeader"] {{ background: transparent; pointer-events: none; height: 0 !important; min-height: 0 !important; }}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span:not([class*="material-symbols"]):not([class*="material-icons"]):not([data-testid="stIconMaterial"]),
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] div,
[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea,
[data-testid="stAppViewContainer"] button,
[data-testid="stAppViewContainer"] select,
[data-testid="stAppViewContainer"] td,
[data-testid="stAppViewContainer"] th,
[data-testid="stAppViewContainer"] li,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([class*="material-symbols"]):not([class*="material-icons"]):not([data-testid="stIconMaterial"]),
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] select {{
    font-family: "Inter", "Noto Sans SC", -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
/* Never override Material icon fonts used by Streamlit */
[class*="material-symbols"],
[class*="material-icons"],
[data-testid="stIconMaterial"],
[data-testid="stHeader"] span,
[data-testid="collapsedControl"] span {{
    font-family: "Material Symbols Rounded", "Material Icons" !important;
}}

/* === Hide sidebar === */
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{
    display: none !important;
}}

/* === Top navbar === */
.top-navbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    margin: -0.5rem -1rem 0.8rem -1rem;
    background: rgba(14, 22, 33, 0.85);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--line);
    border-radius: 0 0 16px 16px;
    position: sticky;
    top: 0;
    z-index: 999;
}}
.nav-links {{
    display: flex;
    gap: 4px;
}}
.nav-link {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 20px;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--muted);
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    background: transparent;
}}
.nav-link:hover {{
    color: var(--ink);
    background: var(--card-hover);
}}
.nav-link.active {{
    color: var(--accent);
    background: rgba(34, 211, 167, 0.10);
    border-color: rgba(34, 211, 167, 0.25);
}}
.nav-brand {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink);
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
    padding: 6px 0;
}}

/* Top nav button overrides */
.top-navbar-row [data-testid="stHorizontalBlock"] {{
    gap: 0.3rem;
    align-items: center;
}}
/* Style nav buttons to look like nav links */
.top-navbar-row button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: var(--muted) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
.top-navbar-row button[kind="secondary"]:hover {{
    color: var(--ink) !important;
    background: var(--card-hover) !important;
}}
.top-navbar-row button[kind="primary"] {{
    background: rgba(34, 211, 167, 0.10) !important;
    border: 1px solid rgba(34, 211, 167, 0.25) !important;
    color: var(--accent) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}}

/* === Layout === */
.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}}

/* === Hero === */
.hero-wrap {{
    background: var(--hero-bg);
    border: 1px solid var(--hero-border);
    border-radius: 20px;
    padding: 28px 32px 22px;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}}
.hero-wrap::before {{
    content: '';
    position: absolute;
    top: -60%;
    right: -20%;
    width: 420px;
    height: 420px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
    opacity: 0.06;
    pointer-events: none;
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
    background: linear-gradient(135deg, var(--ink) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero-sub {{
    color: var(--ink-secondary);
    font-size: 0.92rem;
    font-weight: 400;
    line-height: 1.6;
    max-width: 680px;
    margin-bottom: 2px;
}}
.hero-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}}
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 5px 14px;
    border-radius: 999px;
    border: 1px solid var(--badge-border);
    color: var(--badge-ink);
    background: var(--badge-bg);
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.2px;
    backdrop-filter: blur(6px);
    transition: transform 0.2s, box-shadow 0.2s;
}}
.badge:hover {{
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}}

/* === Section headers === */
.section-hdr {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 1.2rem 0 0.5rem 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink);
}}
.section-hdr::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--divider);
    opacity: 0.45;
}}

/* === Page subtitle === */
.page-subtitle {{
    color: var(--muted);
    font-size: 0.88rem;
    margin: -0.3rem 0 0.9rem 0;
}}

/* === Metrics === */
[data-testid="stMetric"] {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(8px);
    transition: transform 0.2s, box-shadow 0.25s;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--muted) !important;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--ink) !important;
}}

/* === Tables === */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--table-border);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    background: var(--table-bg);
    --gdg-bg-header: var(--table-header-bg);
    --gdg-bg-cell: var(--table-cell-bg);
    --gdg-bg-cell-medium: var(--table-cell-bg);
    --gdg-color: var(--table-cell-text);
    --gdg-header-font-style: 600 12px "Inter", "Noto Sans SC", sans-serif;
    --gdg-horizontal-border-color: var(--table-border);
    --gdg-vertical-border-color: var(--table-border);
    --gdg-border-color: var(--table-border);
}}

/* === Tabs === */
button[data-baseweb="tab"] {{
    border-radius: 12px;
    border: 1px solid var(--line);
    background: var(--tab-bg);
    margin-right: 0.35rem;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 18px;
    transition: all 0.2s;
}}
button[data-baseweb="tab"]:hover {{
    border-color: var(--accent);
    background: var(--card-hover);
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    border-color: var(--accent);
    color: white;
    background: linear-gradient(135deg, var(--accent), #18a88a);
    box-shadow: 0 4px 12px rgba(34, 211, 167, 0.25);
}}

/* === Inputs === */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {{
    background: var(--input-bg);
    border-color: var(--line);
    border-radius: 10px;
    backdrop-filter: blur(6px);
}}

[data-testid="stSlider"] [role="slider"] {{
    border-color: var(--accent);
    background: var(--accent);
    box-shadow: 0 0 0 3px rgba(34, 211, 167, 0.18);
}}

/* === Footer === */
.app-footer {{
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
    font-size: 0.72rem;
    color: var(--muted);
    text-align: center;
}}

/* === Chart container override === */
[data-testid="stBarChartContainer"],
[data-testid="stAreaChartContainer"],
[data-testid="stLineChartContainer"] {{
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 6px;
    background: var(--panel);
    box-shadow: var(--shadow-sm);
}}

/* === Color overrides for text elements === */
[data-testid="stSidebar"] *,
label, p, span, div[data-testid="stCaptionContainer"] {{
    color: var(--ink);
}}
h1, h2, h3 {{
    color: var(--ink) !important;
}}

/* === Row count badge === */
.row-count {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    background: var(--badge-bg);
    color: var(--badge-ink);
    border: 1px solid var(--badge-border);
    margin-bottom: 0.5rem;
}}

/* === Expander styling === */
[data-testid="stExpander"] {{
    border: 1px solid var(--line);
    border-radius: 14px;
    background: var(--panel);
    backdrop-filter: blur(8px);
    box-shadow: var(--shadow-sm);
}}

/* === Book detail right panel === */
.book-panel-root {{
    position: relative;
    z-index: 9999;
}}
.book-panel-toggle {{
    display: none;
}}
.book-panel-toggle:checked + .book-panel-overlay {{
    display: none;
}}
.book-panel-overlay {{
    position: fixed;
    top: 0; right: 0;
    width: 420px;
    height: 100vh;
    z-index: 9999;
    background: var(--bg-1);
    border-left: 1px solid var(--line);
    box-shadow: -8px 0 40px rgba(0,0,0,0.45);
    overflow-y: auto;
    animation: slideInRight 0.3s ease-out;
    backdrop-filter: blur(20px);
}}
@keyframes slideInRight {{
    from {{ transform: translateX(100%); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}
.book-panel-overlay::-webkit-scrollbar {{ width: 5px; }}
.book-panel-overlay::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 4px; }}
.book-panel-header {{
    position: sticky;
    top: 0;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 22px;
    background: var(--bg-1);
    border-bottom: 1px solid var(--line);
}}
.book-panel-header-title {{
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--muted);
}}
.book-panel-close {{
    border: 1px solid var(--line);
    background: rgba(255,255,255,0.03);
    color: var(--ink);
    border-radius: 8px;
    width: 32px;
    height: 32px;
    cursor: pointer;
    font-size: 1rem;
    line-height: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    user-select: none;
}}
.book-panel-close:hover {{
    border-color: var(--accent);
    background: var(--card-hover);
}}
.book-panel-cover {{
    width: 100%;
    padding: 24px 40px 16px;
    text-align: center;
}}
.book-panel-cover img {{
    max-width: 180px;
    height: auto;
    border-radius: 10px;
    box-shadow: var(--shadow-lg);
}}
.book-panel-cover-placeholder {{
    font-size: 4rem;
    color: var(--muted);
    padding: 40px 0;
}}
.book-panel-body {{
    padding: 0 24px 28px;
}}
.book-panel-title {{
    font-size: 1.35rem;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 4px;
    background: linear-gradient(135deg, var(--ink) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.book-panel-authors {{
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 16px;
}}
.book-panel-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 18px;
}}
.book-panel-chip {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid var(--badge-border);
    color: var(--badge-ink);
    background: var(--badge-bg);
    font-size: 0.74rem;
    font-weight: 600;
}}
.book-panel-label {{
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--muted);
    margin-bottom: 6px;
    margin-top: 14px;
}}
.book-panel-desc {{
    font-size: 0.85rem;
    line-height: 1.7;
    color: var(--ink-secondary);
    max-height: 220px;
    overflow-y: auto;
    padding-right: 6px;
}}
.book-panel-desc::-webkit-scrollbar {{ width: 3px; }}
.book-panel-desc::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 4px; }}
.book-panel-preview {{
    display: inline-block;
    margin-top: 20px;
    padding: 10px 24px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--accent), #18a88a);
    color: #fff;
    font-weight: 700;
    font-size: 0.84rem;
    text-decoration: none;
    box-shadow: 0 4px 14px rgba(34, 211, 167, 0.3);
    transition: transform 0.2s, box-shadow 0.2s;
    width: 100%;
    text-align: center;
    box-sizing: border-box;
}}
.book-panel-preview:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(34, 211, 167, 0.45);
    color: #fff;
}}

/* === Rating comparison === */
.rating-compare {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 6px;
}}
.rating-row {{
    display: grid;
    grid-template-columns: 90px 1fr auto auto;
    align-items: center;
    gap: 10px;
}}
.rating-source {{
    font-size: 0.76rem;
    font-weight: 700;
    color: var(--muted);
    white-space: nowrap;
}}
.rating-bar-wrap {{
    height: 8px;
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    overflow: hidden;
}}
.rating-bar {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease-out;
}}
.rating-bar-gr {{
    background: linear-gradient(90deg, #f0a040, #e8d44d);
}}
.rating-bar-google {{
    background: linear-gradient(90deg, #4285f4, #34a8eb);
}}
.rating-score {{
    font-size: 0.82rem;
    font-weight: 800;
    color: var(--ink);
    min-width: 42px;
    text-align: right;
}}
.rating-count {{
    font-size: 0.72rem;
    color: var(--muted);
    min-width: 80px;
}}

/* === Review site links === */
.review-links {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 18px;
}}
.review-link {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 12px;
    border: 1px solid var(--line);
    background: var(--panel);
    color: var(--ink);
    text-decoration: none;
    font-size: 0.84rem;
    font-weight: 600;
    transition: all 0.2s;
}}
.review-link:hover {{
    transform: translateX(4px);
    border-color: var(--accent);
    background: var(--card-hover);
    color: var(--ink);
    text-decoration: none;
}}
.review-link:visited,
.review-link:active,
.review-link:focus {{
    text-decoration: none;
    color: var(--ink);
}}
.review-link-icon {{
    font-size: 1.1rem;
}}
.review-link-gr:hover {{ border-color: #e8d44d; }}
.review-link-douban:hover {{ border-color: #00b51d; }}
.review-link-sg:hover {{ border-color: #8b5cf6; }}

@media (max-width: 768px) {{
    .book-panel-overlay {{
        width: 100vw;
    }}
    .rating-row {{
        grid-template-columns: 70px 1fr auto;
    }}
    .rating-count {{ display: none; }}
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------
def render_hero(t) -> None:
    st.markdown(
        f"""
<div class="hero-wrap">
    <div class="hero-title">{t("app_title")}</div>
    <div class="hero-sub">{t("app_subtitle")}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f'<div class="section-hdr">{text}</div>', unsafe_allow_html=True)


def page_subtitle(text: str) -> None:
    st.markdown(f'<div class="page-subtitle">{text}</div>', unsafe_allow_html=True)


def row_count_badge(count: int, t) -> None:
    st.markdown(
        f'<span class="row-count">{t("rows_returned", count=count)}</span>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------
@st.cache_resource
def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_query(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> List[dict]:
    cur = conn.execute(sql, tuple(params))
    return [dict(row) for row in cur.fetchall()]


def run_scalar(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> Any:
    return conn.execute(sql, tuple(params)).fetchone()[0]


def ensure_app_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS reading_list (
            book_id INTEGER PRIMARY KEY,
            status TEXT NOT NULL CHECK (status IN ('want_to_read', 'reading', 'completed', 'dropped')),
            personal_rating REAL CHECK (personal_rating IS NULL OR (personal_rating BETWEEN 0 AND 5)),
            finished_date TEXT,
            notes TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_reading_list_status ON reading_list(status);
        CREATE INDEX IF NOT EXISTS idx_reading_list_updated_at ON reading_list(updated_at);
        """
    )


def ensure_author_id(conn: sqlite3.Connection, author_name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO authors(author_name) VALUES (?)", (author_name,))
    row = conn.execute(
        "SELECT author_id FROM authors WHERE author_name = ?",
        (author_name,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Could not create/find author: {author_name}")
    return int(row[0])


def get_author_line(conn: sqlite3.Connection, book_id: int) -> str:
    row = conn.execute(
        """
        SELECT GROUP_CONCAT(author_name, ', ')
        FROM (
            SELECT a.author_name AS author_name
            FROM book_authors ba
            JOIN authors a ON a.author_id = ba.author_id
            WHERE ba.book_id = ?
            ORDER BY ba.author_order
        )
        """,
        (book_id,),
    ).fetchone()
    return row[0] if row and row[0] else ""


def import_external_book_to_db(conn: sqlite3.Connection, info: dict) -> tuple[str, int | str]:
    title = (info.get("title") or "").strip()
    if not title:
        return "error", "missing title"

    isbn_13_raw = str(info.get("isbn_13") or "").strip()
    isbn_13_digits = re.sub(r"[^0-9]", "", isbn_13_raw)
    isbn_13 = int(isbn_13_digits) if len(isbn_13_digits) == 13 else None

    isbn_10_raw = str(info.get("isbn_10") or "").strip()
    isbn_10 = re.sub(r"[^0-9Xx]", "", isbn_10_raw).upper() or None

    publish_year = parse_year_from_text(info.get("published_date"))
    pages = info.get("page_count") if isinstance(info.get("page_count"), int) and info.get("page_count") > 0 else None
    publisher = (info.get("publisher") or "").strip() or None
    language = normalize_openlib_language(info.get("language_codes"))
    import_rating = _parse_openlibrary_rating(info.get("google_rating"))
    import_num_ratings = _parse_openlibrary_count(info.get("google_ratings_count"))

    authors = [
        a.strip()
        for a in (info.get("authors") or [])
        if isinstance(a, str) and a.strip()
    ]

    existing_row = None
    if isbn_13 is not None:
        existing_row = conn.execute(
            "SELECT book_id FROM books WHERE isbn13 = ? LIMIT 1",
            (isbn_13,),
        ).fetchone()
    if existing_row is None and isbn_10:
        existing_row = conn.execute(
            "SELECT book_id FROM books WHERE isbn = ? LIMIT 1",
            (isbn_10,),
        ).fetchone()
    if existing_row is None and publish_year is not None:
        existing_row = conn.execute(
            "SELECT book_id FROM books WHERE title = ? AND publish_year = ? LIMIT 1",
            (title, publish_year),
        ).fetchone()
    if existing_row is None:
        existing_row = conn.execute(
            "SELECT book_id FROM books WHERE title = ? LIMIT 1",
            (title,),
        ).fetchone()
    if existing_row is not None:
        return "existing", int(existing_row[0])

    next_book_id = int(run_scalar(conn, "SELECT COALESCE(MAX(book_id), 0) + 1 FROM books"))

    try:
        with conn:
            conn.execute(
                """
                INSERT INTO books (
                    book_id, title, isbn, isbn13, language, pages, publisher_name,
                    publish_year, num_ratings, rating, text_reviews_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    next_book_id,
                    title,
                    isbn_10,
                    isbn_13,
                    language,
                    pages,
                    publisher,
                    publish_year,
                    import_num_ratings,
                    import_rating,
                    None,
                ),
            )

            for idx, author_name in enumerate(authors, start=1):
                author_id = ensure_author_id(conn, author_name)
                conn.execute(
                    "INSERT INTO book_authors(book_id, author_id, author_order) VALUES (?, ?, ?)",
                    (next_book_id, author_id, idx),
                )
    except sqlite3.DatabaseError as err:
        return "error", str(err)

    return "imported", next_book_id


def show_table(rows: List[dict], t, lang: str = "en", height: int = 420) -> None:
    if rows:
        row_count_badge(len(rows), t)
        st.dataframe(_rename_rows(rows, lang), use_container_width=True, hide_index=True, height=height)
    else:
        st.info(t("no_data"))


# ---------------------------------------------------------------------------
# External Book APIs
# ---------------------------------------------------------------------------
OPENLIB_SEARCH_URL = "https://openlibrary.org/search.json"
OPENLIB_WORK_URL_TMPL = "https://openlibrary.org{work_key}.json"
OPENLIB_WORK_EDITIONS_URL_TMPL = "https://openlibrary.org{work_key}/editions.json"


def _short_api_error_reason(err: Exception) -> str:
    if isinstance(err, requests.Timeout):
        return "request timeout"
    if isinstance(err, requests.ConnectionError):
        msg = str(err).lower()
        if "nameresolutionerror" in msg or "nodename nor servname" in msg or "name or service not known" in msg:
            return "dns resolution failed"
        return "network connection failed"
    if isinstance(err, requests.HTTPError):
        status = err.response.status_code if err.response is not None else "unknown"
        if status == 403:
            return "HTTP 403 (forbidden)"
        if status == 429:
            return "HTTP 429 (rate limit)"
        return f"HTTP {status}"
    if isinstance(err, ValueError):
        return "invalid API response"
    return "unknown error"


def _parse_openlibrary_rating(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed < 0 or parsed > 5:
        return None
    return round(parsed, 2)


def _parse_openlibrary_count(value: Any) -> int | None:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            parsed = int(float(text))
        else:
            parsed = int(value)
    except (TypeError, ValueError):
        return None
    if parsed < 0:
        return None
    return parsed


def _normalize_openlibrary_doc(doc: dict, title_fallback: str) -> dict:
    isbn_13 = None
    isbn_10 = None
    for isbn in doc.get("isbn", []) or []:
        if not isinstance(isbn, str):
            continue
        digits = re.sub(r"[^0-9Xx]", "", isbn)
        if len(digits) == 13 and isbn_13 is None:
            isbn_13 = digits
        elif len(digits) == 10 and isbn_10 is None:
            isbn_10 = digits.upper()

    cover_id = doc.get("cover_i")
    thumbnail = (
        f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg?default=false"
        if cover_id
        else None
    )
    published_year = doc.get("first_publish_year")
    publishers = doc.get("publisher") or []
    subjects = doc.get("subject") or []
    key = doc.get("key")
    preview_link = f"https://openlibrary.org{key}" if key else None

    return {
        "title": doc.get("title") or title_fallback,
        "authors": doc.get("author_name", []) or [],
        "language_codes": doc.get("language", []) or [],
        "publisher": publishers[0] if publishers else None,
        "published_date": str(published_year) if published_year else None,
        "description": None,
        "page_count": doc.get("number_of_pages_median"),
        "categories": subjects[:3] if subjects else [],
        "thumbnail": thumbnail,
        "preview_link": preview_link,
        "isbn_13": isbn_13,
        "isbn_10": isbn_10,
        "google_rating": _parse_openlibrary_rating(doc.get("ratings_average")),
        "google_ratings_count": _parse_openlibrary_count(doc.get("ratings_count")),
        "data_source": "Open Library",
    }


def _extract_openlibrary_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, dict):
        nested = value.get("value") or value.get("text")
        if isinstance(nested, str):
            text = nested.strip()
            return text or None
    return None


def _first_valid_isbn(values: Any, length: int) -> str | None:
    if not isinstance(values, list):
        return None
    for raw in values:
        if not isinstance(raw, str):
            continue
        digits = re.sub(r"[^0-9Xx]", "", raw)
        if len(digits) == length:
            return digits.upper()
    return None


def _first_cover_url(values: Any) -> str | None:
    if not isinstance(values, list) or not values:
        return None
    cover_id = values[0]
    if isinstance(cover_id, int):
        return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg?default=false"
    return None


def _first_text(values: Any) -> str | None:
    if not isinstance(values, list):
        return None
    for item in values:
        if isinstance(item, str) and item.strip():
            return item.strip()
    return None


def _enrich_openlibrary_info(base_info: dict, work_key: str | None) -> dict:
    if not work_key:
        return base_info

    info = dict(base_info)

    # 1) Work-level enrichment: description/subjects/covers
    try:
        work_resp = requests.get(
            OPENLIB_WORK_URL_TMPL.format(work_key=work_key),
            headers={"User-Agent": "BooksDatabaseExplorer/1.0 (contact: local-app)"},
            timeout=8,
        )
        work_resp.raise_for_status()
        work = work_resp.json()
    except (requests.RequestException, ValueError):
        work = None

    if work:
        if not info.get("description"):
            info["description"] = _extract_openlibrary_text(work.get("description"))
        if not info.get("categories"):
            subjects = work.get("subjects")
            if isinstance(subjects, list):
                info["categories"] = [s for s in subjects[:3] if isinstance(s, str)]
        if not info.get("thumbnail"):
            info["thumbnail"] = _first_cover_url(work.get("covers"))

    # 2) Edition-level enrichment: ISBN/publisher/pages/publish date (+fallback desc/subjects/covers)
    try:
        editions_resp = requests.get(
            OPENLIB_WORK_EDITIONS_URL_TMPL.format(work_key=work_key),
            params={"limit": 20},
            headers={"User-Agent": "BooksDatabaseExplorer/1.0 (contact: local-app)"},
            timeout=8,
        )
        editions_resp.raise_for_status()
        editions_data = editions_resp.json()
    except (requests.RequestException, ValueError):
        editions_data = None

    entries = editions_data.get("entries") if isinstance(editions_data, dict) else None
    if not isinstance(entries, list) or not entries:
        return info

    def _edition_score(ed: dict) -> int:
        score = 0
        if _first_valid_isbn(ed.get("isbn_13"), 13):
            score += 3
        if _first_valid_isbn(ed.get("isbn_10"), 10):
            score += 2
        if _first_text(ed.get("publishers")):
            score += 1
        if ed.get("number_of_pages"):
            score += 1
        if _extract_openlibrary_text(ed.get("description")):
            score += 1
        if isinstance(ed.get("subjects"), list) and ed.get("subjects"):
            score += 1
        return score

    best_edition = max((e for e in entries if isinstance(e, dict)), key=_edition_score, default=None)
    if not isinstance(best_edition, dict):
        return info

    if not info.get("isbn_13"):
        info["isbn_13"] = _first_valid_isbn(best_edition.get("isbn_13"), 13)
    if not info.get("isbn_10"):
        info["isbn_10"] = _first_valid_isbn(best_edition.get("isbn_10"), 10)
    if not info.get("publisher"):
        info["publisher"] = _first_text(best_edition.get("publishers"))
    if not info.get("published_date"):
        publish_date = best_edition.get("publish_date")
        if isinstance(publish_date, str):
            info["published_date"] = publish_date
    if not info.get("page_count"):
        page_count = best_edition.get("number_of_pages")
        if isinstance(page_count, int):
            info["page_count"] = page_count
    if not info.get("language_codes"):
        languages = best_edition.get("languages")
        if isinstance(languages, list) and languages:
            info["language_codes"] = languages
    if not info.get("description"):
        info["description"] = _extract_openlibrary_text(best_edition.get("description"))
    if not info.get("categories"):
        subjects = best_edition.get("subjects")
        if isinstance(subjects, list):
            info["categories"] = [s for s in subjects[:3] if isinstance(s, str)]
    if not info.get("thumbnail"):
        info["thumbnail"] = _first_cover_url(best_edition.get("covers"))

    return info


def fetch_openlibrary_book(title: str, author: str | None = None) -> tuple[dict | None, str, str | None]:
    clean_title = (title or "").strip()
    clean_author = (author or "").strip()
    if not clean_title:
        return None, "not_found", None

    param_sets = []
    if clean_author:
        param_sets.append({"title": clean_title, "author": clean_author, "limit": 5})
    param_sets.append({"title": clean_title, "limit": 5})
    param_sets.append({"q": clean_title, "limit": 5})

    unique_param_sets = []
    seen = set()
    for params in param_sets:
        key = tuple(sorted(params.items()))
        if key in seen:
            continue
        seen.add(key)
        unique_param_sets.append(params)

    last_reason: str | None = None
    had_api_error = False

    for params in unique_param_sets:
        try:
            resp = requests.get(
                OPENLIB_SEARCH_URL,
                params=params,
                headers={"User-Agent": "BooksDatabaseExplorer/1.0 (contact: local-app)"},
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as err:
            had_api_error = True
            last_reason = _short_api_error_reason(err)
            continue

        docs = data.get("docs")
        if not docs:
            continue

        first_doc = docs[0]
        if not isinstance(first_doc, dict):
            continue

        base_info = _normalize_openlibrary_doc(first_doc, clean_title)
        work_key = first_doc.get("key") if isinstance(first_doc.get("key"), str) else None
        enriched_info = _enrich_openlibrary_info(base_info, work_key)
        return enriched_info, "ok", None

    if had_api_error:
        return None, "api_error", last_reason
    return None, "not_found", None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_openlibrary_book_cached(title: str, author: str | None = None) -> tuple[dict | None, str, str | None]:
    return fetch_openlibrary_book(title, author)


def render_book_card(info: dict, t, db_book: dict | None = None) -> None:
    """Render a right-side sliding panel with external book details."""
    import html as _html
    from urllib.parse import quote_plus as _qp

    title_esc = _html.escape(info["title"])
    authors_str = ", ".join(info["authors"]) if info["authors"] else t("unknown_author")
    authors_esc = _html.escape(authors_str)

    # Cover
    if info.get("thumbnail"):
        cover_html = f'<img src="{info["thumbnail"]}" alt="cover">'
    else:
        cover_html = '<div class="book-panel-cover-placeholder">📚</div>'

    # Meta chips
    chips = []
    if info.get("data_source"):
        chips.append(f'📡 {t("book_source")}: {_html.escape(str(info["data_source"]))}')
    if info.get("publisher"):
        chips.append(f'🏢 {_html.escape(info["publisher"])}')
    if info.get("published_date"):
        chips.append(f'📅 {_html.escape(info["published_date"])}')
    if info.get("page_count"):
        chips.append(f'📄 {info["page_count"]} {t("pages_unit_short")}')
    if info.get("isbn_13"):
        chips.append(f'🔢 {info["isbn_13"]}')
    elif info.get("isbn_10"):
        chips.append(f'🔢 {info["isbn_10"]}')
    if info.get("categories"):
        for cat in info["categories"][:3]:
            chips.append(f'🏷️ {_html.escape(cat)}')

    chips_html = "".join(f'<span class="book-panel-chip">{c}</span>' for c in chips)

    # Description (escape API HTML to avoid breaking panel structure)
    desc = info.get("description", "")
    desc_section = ""
    if desc:
        desc_label = t("book_description")
        safe_desc = _html.escape(desc)
        desc_section = f'<div class="book-panel-label">{desc_label}</div><div class="book-panel-desc">{safe_desc}</div>'

    # --- Rating comparison ---
    rating_section = ""
    gr_rating = db_book.get("rating") if db_book else None
    gr_count = db_book.get("num_ratings") if db_book else None
    g_rating = info.get("google_rating")
    g_count = info.get("google_ratings_count")

    if gr_rating or g_rating:
        rating_section += f'<div class="book-panel-label">{t("rating_compare")}</div>'
        rating_section += '<div class="rating-compare">'
        if gr_rating is not None:
            pct = gr_rating / 5.0 * 100
            count_str = f"{gr_count:,}" if gr_count else "—"
            rating_section += (
                '<div class="rating-row">'
                f'<span class="rating-source">{t("rating_goodreads")}</span>'
                '<div class="rating-bar-wrap">'
                f'<div class="rating-bar rating-bar-gr" style="width:{pct}%"></div>'
                '</div>'
                f'<span class="rating-score">★ {gr_rating}</span>'
                f'<span class="rating-count">{t("rating_people", count=count_str)}</span>'
                '</div>'
            )
        if g_rating is not None:
            pct = g_rating / 5.0 * 100
            count_str = f"{g_count:,}" if g_count else "—"
            rating_section += (
                '<div class="rating-row">'
                f'<span class="rating-source">{t("rating_google")}</span>'
                '<div class="rating-bar-wrap">'
                f'<div class="rating-bar rating-bar-google" style="width:{pct}%"></div>'
                '</div>'
                f'<span class="rating-score">★ {g_rating}</span>'
                f'<span class="rating-count">{t("rating_people", count=count_str)}</span>'
                '</div>'
            )
        rating_section += '</div>'

    # --- External review site links ---
    search_q = _qp(info["title"])
    links_section = (
        f'<div class="book-panel-label">{t("review_sites")}</div>'
        '<div class="review-links">'
        f'<a class="review-link review-link-gr" href="https://www.goodreads.com/search?q={search_q}" target="_blank" rel="noopener noreferrer">'
        '<span class="review-link-icon">📖</span> Goodreads</a>'
        f'<a class="review-link review-link-douban" href="https://search.douban.com/book/subject_search?search_text={search_q}" target="_blank" rel="noopener noreferrer">'
        '<span class="review-link-icon">🫘</span> 豆瓣读书</a>'
        f'<a class="review-link review-link-sg" href="https://app.thestorygraph.com/browse?search_term={search_q}" target="_blank" rel="noopener noreferrer">'
        '<span class="review-link-icon">📊</span> StoryGraph</a>'
        '</div>'
    )

    # Preview button
    preview_html = ""
    if info.get("preview_link"):
        btn_text = t("book_preview")
        preview_html = f'<a class="book-panel-preview" href="{info["preview_link"]}" target="_blank" rel="noopener noreferrer">🔗 {btn_text}</a>'

    header_label = t("book_detail")
    panel_id = f"book-panel-toggle-{abs(hash((info.get('title'), info.get('isbn_13'), info.get('isbn_10'), info.get('preview_link'))))}"

    panel = (
        '<div class="book-panel-root">'
        f'<input type="checkbox" id="{panel_id}" class="book-panel-toggle">'
        '<div class="book-panel-overlay">'
        '<div class="book-panel-header">'
        f'<span class="book-panel-header-title">{header_label}</span>'
        f'<label for="{panel_id}" class="book-panel-close" title="Close">←</label>'
        '</div>'
        f'<div class="book-panel-cover">{cover_html}</div>'
        '<div class="book-panel-body">'
        f'<div class="book-panel-title">{title_esc}</div>'
        f'<div class="book-panel-authors">{t("book_by", authors=authors_esc)}</div>'
        f'<div class="book-panel-meta">{chips_html}</div>'
        f'{desc_section}'
        f'{rating_section}'
        f'{links_section}'
        f'{preview_html}'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(panel, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_search(conn: sqlite3.Connection, t, lang: str) -> None:
    st.header(t("page_search"))
    page_subtitle(t("search_hint"))
    if "openlib_quick_result" not in st.session_state:
        st.session_state.openlib_quick_result = None
    if "openlib_quick_query" not in st.session_state:
        st.session_state.openlib_quick_query = ""

    section_title(t("filter_panel"))

    year_min = run_scalar(conn, "SELECT COALESCE(MIN(publish_year), 1900) FROM books WHERE publish_year IS NOT NULL")
    year_max = run_scalar(conn, "SELECT COALESCE(MAX(publish_year), 2026) FROM books WHERE publish_year IS NOT NULL")
    total_books = run_scalar(conn, "SELECT COUNT(*) FROM books")

    col_a, col_b = st.columns(2)
    with col_a:
        keyword = st.text_input(
            t("title_keyword"),
            "",
            placeholder=t("title_keyword_placeholder"),
        )
        year_range = st.slider(
            t("publish_year"),
            min_value=int(year_min),
            max_value=int(year_max),
            value=(int(year_min), int(year_max)),
        )
    with col_b:
        rating_range = st.slider(t("rating"), min_value=0.0, max_value=5.0, value=(3.5, 5.0), step=0.1)
        lang_list = [r["language"] for r in run_query(conn, "SELECT DISTINCT language FROM books WHERE language IS NOT NULL ORDER BY language")]
        _lang_zh = {
            "Arabic": "阿拉伯语", "English": "英语", "French": "法语",
            "German": "德语", "Greek": "希腊语", "Italian": "意大利语",
            "Japanese": "日语", "Latin": "拉丁语", "Multiple": "多语言",
            "Portuguese": "葡萄牙语", "Russian": "俄语", "Spanish": "西班牙语",
            "Swedish": "瑞典语", "Turkish": "土耳其语",
        }
        if lang == "zh":
            display_list = [_lang_zh.get(l, l) for l in lang_list]
        else:
            display_list = lang_list
        lang_options = [t("all_languages")] + display_list
        selected_lang_display = st.selectbox(t("filter_language"), lang_options, index=0)
        # Map display name back to DB value
        if selected_lang_display == t("all_languages"):
            selected_lang = None
        elif lang == "zh":
            _zh_to_en = {v: k for k, v in _lang_zh.items()}
            selected_lang = _zh_to_en.get(selected_lang_display, selected_lang_display)
        else:
            selected_lang = selected_lang_display

    sql = """
    SELECT
        b.book_id,
        b.title,
        (
            SELECT GROUP_CONCAT(author_name, ', ')
            FROM (
                SELECT a.author_name AS author_name
                FROM book_authors ba
                JOIN authors a ON a.author_id = ba.author_id
                WHERE ba.book_id = b.book_id
                ORDER BY ba.author_order
            )
        ) AS authors,
        b.publish_year,
        b.rating,
        b.num_ratings,
        b.pages,
        b.language
    FROM books b
    WHERE 1=1
    """
    params: List[Any] = []
    keyword_text = keyword.strip()

    if keyword_text:
        sql += " AND b.title LIKE ?"
        params.append(f"%{keyword_text}%")

    if keyword_text:
        sql += " AND (b.publish_year BETWEEN ? AND ? OR b.publish_year IS NULL)"
    else:
        sql += " AND b.publish_year BETWEEN ? AND ?"
    params.extend([year_range[0], year_range[1]])

    if keyword_text:
        sql += " AND (b.rating BETWEEN ? AND ? OR b.rating IS NULL)"
    else:
        sql += " AND b.rating BETWEEN ? AND ?"
    params.extend([rating_range[0], rating_range[1]])

    if selected_lang is not None:
        sql += " AND b.language = ?"
        params.append(selected_lang)

    sql += " ORDER BY b.rating DESC, b.title ASC"

    rows = run_query(conn, sql, params)

    # Separate book_id from display rows
    book_ids = [r["book_id"] for r in rows]
    display_rows = [{k: v for k, v in r.items() if k != "book_id"} for r in rows]

    section_title(t("results_panel"))

    if not display_rows:
        st.info(t("no_data"))
    else:
        row_count_badge(len(display_rows), t)
        st.caption(t("select_book_hint"))

        df = pd.DataFrame(_rename_rows(display_rows, lang))
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=480,
            on_select="rerun",
            selection_mode="single-row",
        )

        # --- Open Library detail on row click ---
        selected_indices = event.selection.rows if event and event.selection else []
        if selected_indices:
            idx = selected_indices[0]
            if idx < len(display_rows):
                selected_title = display_rows[idx]["title"]

                # Look up author for better matching
                bid = book_ids[idx] if idx < len(book_ids) else None
                author_row = run_query(
                    conn,
                    """SELECT a.author_name FROM authors a
                       JOIN book_authors ba ON a.author_id = ba.author_id
                       WHERE ba.book_id = ? ORDER BY ba.author_order LIMIT 1""",
                    (bid,),
                ) if bid else []
                author_name = author_row[0]["author_name"] if author_row else None

                with st.spinner(t("book_loading")):
                    info, status, reason = fetch_openlibrary_book_cached(selected_title, author_name)
                if info is None:
                    if status == "api_error":
                        if reason:
                            st.warning(t("book_api_error_with_reason", reason=reason))
                        else:
                            st.warning(t("book_api_error"))
                    else:
                        st.warning(t("book_no_result"))
                else:
                    # Pass the DB row for rating comparison
                    db_book = rows[idx] if idx < len(rows) else None
                    render_book_card(info, t, db_book=db_book)

    section_title(t("google_fallback_title"))
    st.caption(t("google_fallback_hint"))
    with st.form("google_fallback_form", clear_on_submit=False):
        fallback_col_title, fallback_col_author = st.columns(2)
        with fallback_col_title:
            fallback_title = st.text_input(
                t("google_fallback_input"),
                value="",
                placeholder=t("google_fallback_placeholder"),
            )
        with fallback_col_author:
            fallback_author = st.text_input(
                t("google_fallback_author_input"),
                value="",
                placeholder=t("google_fallback_author_placeholder"),
            )
        fallback_submit = st.form_submit_button(
            t("google_fallback_button"),
            type="secondary",
        )

    if fallback_submit:
        if not fallback_title.strip():
            st.warning(t("google_fallback_empty"))
        else:
            fallback_author_text = fallback_author.strip() or None
            with st.spinner(t("google_fallback_loading")):
                fallback_info, status, reason = fetch_openlibrary_book_cached(
                    fallback_title.strip(),
                    fallback_author_text,
                )
            if fallback_info is None:
                st.session_state.openlib_quick_result = None
                if status == "api_error":
                    if reason:
                        st.warning(t("book_api_error_with_reason", reason=reason))
                    else:
                        st.warning(t("book_api_error"))
                else:
                    st.warning(t("google_fallback_no_result"))
            else:
                st.session_state.openlib_quick_result = fallback_info
                st.session_state.openlib_quick_query = fallback_title.strip()

    quick_result = st.session_state.get("openlib_quick_result")
    if isinstance(quick_result, dict):
        render_book_card(quick_result, t)
        if st.button(t("openlib_import_button"), key="openlib_import_button"):
            status, payload = import_external_book_to_db(conn, quick_result)
            if status == "imported":
                st.success(t("openlib_imported", book_id=payload))
            elif status == "existing":
                st.info(t("openlib_import_exists", book_id=payload))
            else:
                st.error(t("openlib_import_failed", reason=str(payload)))


def page_reading_list(conn: sqlite3.Connection, t, lang: str) -> None:
    st.header(t("page_reading_list"))
    page_subtitle(t("reading_list_hint"))

    tab_my_reading, tab_manage_books = st.tabs([t("tab_my_reading"), t("tab_manage_books")])

    with tab_my_reading:
        section_title(t("reading_add_section"))

        reading_keyword = st.text_input(
            t("reading_search"),
            value="",
            placeholder=t("reading_search_placeholder"),
            key="reading_keyword",
        ).strip()

        reading_candidates = run_query(
            conn,
            """
            SELECT
                b.book_id,
                b.title,
                b.publish_year,
                COALESCE(
                    (
                        SELECT GROUP_CONCAT(author_name, ', ')
                        FROM (
                            SELECT a.author_name AS author_name
                            FROM book_authors ba
                            JOIN authors a ON a.author_id = ba.author_id
                            WHERE ba.book_id = b.book_id
                            ORDER BY ba.author_order
                        )
                    ),
                    ?
                ) AS authors
            FROM books b
            WHERE b.title LIKE ?
            ORDER BY COALESCE(b.num_ratings, 0) DESC, COALESCE(b.rating, 0) DESC, b.title ASC
            LIMIT 160
            """,
            (t("unknown_author"), f"%{reading_keyword}%"),
        )

        if not reading_candidates:
            st.info(t("no_data"))
        else:
            candidate_options = {}
            for row in reading_candidates:
                year_text = row["publish_year"] if row["publish_year"] is not None else "—"
                label = f'{row["title"]} ({year_text}) · {row["authors"]} · ID {row["book_id"]}'
                candidate_options[label] = row["book_id"]

            selected_book_label = st.selectbox(
                t("select_book_for_reading"),
                list(candidate_options.keys()),
                key="reading_selected_book",
            )
            selected_book_id = candidate_options[selected_book_label]

            existing_entry_rows = run_query(
                conn,
                "SELECT * FROM reading_list WHERE book_id = ?",
                (selected_book_id,),
            )
            existing_entry = existing_entry_rows[0] if existing_entry_rows else None

            status_pairs = reading_status_options(t)
            status_codes = [code for code, _ in status_pairs]
            status_labels = [label for _, label in status_pairs]
            default_status_code = existing_entry["status"] if existing_entry else "want_to_read"
            default_status_index = (
                status_codes.index(default_status_code)
                if default_status_code in status_codes
                else 0
            )

            default_set_rating = bool(
                existing_entry and existing_entry.get("personal_rating") is not None
            )
            default_rating_value = (
                float(existing_entry["personal_rating"])
                if default_set_rating
                else 3.0
            )

            default_set_finished = bool(
                existing_entry and existing_entry.get("finished_date")
            )
            default_finished_date = date.today()
            if default_set_finished:
                try:
                    default_finished_date = date.fromisoformat(existing_entry["finished_date"])
                except ValueError:
                    default_finished_date = date.today()

            default_notes = (existing_entry.get("notes") or "") if existing_entry else ""

            widget_prefix = f"reading_entry_{selected_book_id}"
            selected_status_label = st.selectbox(
                t("reading_status"),
                status_labels,
                index=default_status_index,
                key=f"{widget_prefix}_status",
            )

            c1, c2 = st.columns(2)
            with c1:
                set_my_rating = st.checkbox(
                    t("set_my_rating"),
                    value=default_set_rating,
                    key=f"{widget_prefix}_set_my_rating",
                )
                my_rating_value = None
                if set_my_rating:
                    my_rating_value = st.number_input(
                        t("my_rating"),
                        min_value=0.0,
                        max_value=5.0,
                        value=default_rating_value,
                        step=0.5,
                        key=f"{widget_prefix}_my_rating",
                    )
            with c2:
                set_finished_date = st.checkbox(
                    t("set_finished_date"),
                    value=default_set_finished,
                    key=f"{widget_prefix}_set_finished_date",
                )
                finished_date_value = None
                if set_finished_date:
                    finished_date_value = st.date_input(
                        t("finished_date"),
                        value=default_finished_date,
                        key=f"{widget_prefix}_finished_date",
                    )

            reading_notes = st.text_area(
                t("reading_notes"),
                value=default_notes,
                height=100,
                key=f"{widget_prefix}_notes",
            )
            save_reading_entry = st.button(
                t("save_reading_entry"),
                type="primary",
                key=f"{widget_prefix}_save",
            )

            selected_status_code = status_codes[status_labels.index(selected_status_label)]
            if selected_status_code == "completed" and not set_finished_date:
                st.caption(t("completed_date_hint"))

            if save_reading_entry:
                with conn:
                    conn.execute(
                        """
                        INSERT INTO reading_list (
                            book_id, status, personal_rating, finished_date, notes, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(book_id) DO UPDATE SET
                            status = excluded.status,
                            personal_rating = excluded.personal_rating,
                            finished_date = excluded.finished_date,
                            notes = excluded.notes,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (
                            selected_book_id,
                            selected_status_code,
                            float(my_rating_value) if set_my_rating else None,
                            finished_date_value.isoformat() if set_finished_date and finished_date_value else None,
                            reading_notes.strip() or None,
                        ),
                    )
                st.success(t("reading_saved"))
                st.rerun()

        section_title(t("reading_table_section"))
        reading_rows = run_query(
            conn,
            """
            SELECT
                rl.book_id,
                b.title,
                COALESCE(
                    (
                        SELECT GROUP_CONCAT(author_name, ', ')
                        FROM (
                            SELECT a.author_name AS author_name
                            FROM book_authors ba
                            JOIN authors a ON a.author_id = ba.author_id
                            WHERE ba.book_id = b.book_id
                            ORDER BY ba.author_order
                        )
                    ),
                    ?
                ) AS authors,
                rl.status,
                rl.personal_rating,
                rl.finished_date,
                rl.notes,
                rl.updated_at
            FROM reading_list rl
            JOIN books b ON b.book_id = rl.book_id
            ORDER BY
                CASE rl.status
                    WHEN 'reading' THEN 1
                    WHEN 'want_to_read' THEN 2
                    WHEN 'completed' THEN 3
                    WHEN 'dropped' THEN 4
                    ELSE 5
                END,
                rl.updated_at DESC
            """,
            (t("unknown_author"),),
        )

        if not reading_rows:
            st.info(t("no_data"))
        else:
            status_rows = run_query(
                conn,
                "SELECT status, COUNT(*) AS count FROM reading_list GROUP BY status",
            )
            if status_rows:
                parts = [
                    f'{reading_status_label(r["status"], t)}: {r["count"]}'
                    for r in status_rows
                ]
                st.caption(f'{t("status_breakdown")}: {" · ".join(parts)}')

            display_rows = []
            for row in reading_rows:
                item = dict(row)
                item["status"] = reading_status_label(item["status"], t)
                display_rows.append(item)

            row_count_badge(len(display_rows), t)
            st.dataframe(
                _rename_rows(display_rows, lang),
                use_container_width=True,
                hide_index=True,
                height=420,
            )

            section_title(t("reading_export_section"))
            st.caption(t("reading_export_ready", count=len(display_rows)))
            st.caption(t("reading_export_hint"))
            export_df = _rename_df(pd.DataFrame(display_rows), lang)
            export_csv = export_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                t("reading_export"),
                data=export_csv,
                file_name=f"reading_list_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=False,
            )

            entry_options = {}
            for row in reading_rows:
                label = (
                    f'{row["title"]} · {reading_status_label(row["status"], t)} · ID {row["book_id"]}'
                )
                entry_options[label] = row["book_id"]

            selected_entry_label = st.selectbox(
                t("select_reading_entry"),
                list(entry_options.keys()),
                key="reading_delete_select",
            )
            if st.button(t("delete_reading_entry"), key="reading_delete_btn"):
                with conn:
                    conn.execute(
                        "DELETE FROM reading_list WHERE book_id = ?",
                        (entry_options[selected_entry_label],),
                    )
                st.success(t("reading_deleted"))
                st.rerun()

    with tab_manage_books:
        st.caption(t("book_admin_hint"))

        section_title(t("book_add_section"))
        default_year = min(max(date.today().year, 1800), 2030)
        with st.form("add_book_form", clear_on_submit=True):
            add_title = st.text_input(f'{t("book_title")} *')
            add_authors = st.text_input(
                f'{t("book_authors_input")} *',
                placeholder=t("book_authors_placeholder"),
            )
            c1, c2, c3 = st.columns(3)
            with c1:
                add_publish_year = st.number_input(
                    f'{t("book_publish_year_input")} *',
                    min_value=1800,
                    max_value=2030,
                    value=int(default_year),
                    step=1,
                )
            with c2:
                add_rating = st.number_input(
                    f'{t("book_rating_input")} *',
                    min_value=0.0,
                    max_value=5.0,
                    value=4.0,
                    step=0.1,
                )
            with c3:
                add_language = st.text_input(
                    f'{t("book_language_input")} *',
                    value="English",
                )

            c4, c5, c6 = st.columns(3)
            with c4:
                add_pages = st.text_input(t("book_pages_input"), value="")
            with c5:
                add_num_ratings = st.text_input(t("book_num_ratings_input"), value="")
            with c6:
                add_reviews = st.text_input(t("book_reviews_count_input"), value="")

            add_publisher = st.text_input(t("book_publisher_input"), value="")
            add_isbn = st.text_input(t("book_isbn_input"), value="")
            add_isbn13 = st.text_input(t("book_isbn13_input"), value="")

            add_book_submit = st.form_submit_button(t("add_book_btn"), type="primary")

        if add_book_submit:
            payload, errors = sanitize_book_payload(
                title=add_title,
                authors_text=add_authors,
                publish_year=int(add_publish_year),
                rating=float(add_rating),
                language=add_language,
                pages_text=add_pages,
                num_ratings_text=add_num_ratings,
                reviews_text=add_reviews,
                publisher=add_publisher,
                isbn=add_isbn,
                isbn13_text=add_isbn13,
                t=t,
            )
            if errors:
                for msg in errors:
                    st.error(msg)
            else:
                next_book_id = int(run_scalar(conn, "SELECT COALESCE(MAX(book_id), 0) + 1 FROM books"))
                with conn:
                    conn.execute(
                        """
                        INSERT INTO books (
                            book_id, title, isbn, isbn13, language, pages, publisher_name,
                            publish_year, num_ratings, rating, text_reviews_count
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            next_book_id,
                            payload["title"],
                            payload["isbn"],
                            payload["isbn13"],
                            payload["language"],
                            payload["pages"],
                            payload["publisher_name"],
                            payload["publish_year"],
                            payload["num_ratings"],
                            payload["rating"],
                            payload["text_reviews_count"],
                        ),
                    )

                    for idx, author_name in enumerate(payload["authors"], start=1):
                        author_id = ensure_author_id(conn, author_name)
                        conn.execute(
                            "INSERT INTO book_authors(book_id, author_id, author_order) VALUES (?, ?, ?)",
                            (next_book_id, author_id, idx),
                        )

                st.success(t("book_added"))
                st.rerun()

        section_title(t("book_edit_section"))
        edit_keyword = st.text_input(
            t("book_search"),
            value="",
            placeholder=t("book_search_placeholder"),
            key="edit_book_keyword",
        ).strip()

        edit_candidates = run_query(
            conn,
            """
            SELECT
                b.book_id,
                b.title,
                b.publish_year,
                COALESCE(
                    (
                        SELECT GROUP_CONCAT(author_name, ', ')
                        FROM (
                            SELECT a.author_name AS author_name
                            FROM book_authors ba
                            JOIN authors a ON a.author_id = ba.author_id
                            WHERE ba.book_id = b.book_id
                            ORDER BY ba.author_order
                        )
                    ),
                    ?
                ) AS authors
            FROM books b
            WHERE b.title LIKE ?
            ORDER BY b.title ASC
            LIMIT 200
            """,
            (t("unknown_author"), f"%{edit_keyword}%"),
        )

        if not edit_candidates:
            st.info(t("no_data"))
        else:
            edit_options = {}
            for row in edit_candidates:
                year_text = row["publish_year"] if row["publish_year"] is not None else "—"
                label = f'{row["title"]} ({year_text}) · {row["authors"]} · ID {row["book_id"]}'
                edit_options[label] = row["book_id"]

            selected_edit_label = st.selectbox(
                t("select_existing_book"),
                list(edit_options.keys()),
                key="selected_edit_book",
            )
            selected_edit_book_id = edit_options[selected_edit_label]

            current_book_rows = run_query(
                conn,
                "SELECT * FROM books WHERE book_id = ?",
                (selected_edit_book_id,),
            )
            if current_book_rows:
                current_book = current_book_rows[0]
                current_authors = get_author_line(conn, selected_edit_book_id)
                current_year = (
                    int(current_book["publish_year"])
                    if current_book["publish_year"] is not None
                    else int(default_year)
                )
                current_rating = (
                    float(current_book["rating"])
                    if current_book["rating"] is not None
                    else 0.0
                )

                with st.form(f"edit_book_form_{selected_edit_book_id}", clear_on_submit=False):
                    edit_title = st.text_input(
                        f'{t("book_title")} *',
                        value=current_book["title"],
                    )
                    edit_authors = st.text_input(
                        f'{t("book_authors_input")} *',
                        value=current_authors,
                        placeholder=t("book_authors_placeholder"),
                    )
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        edit_publish_year = st.number_input(
                            f'{t("book_publish_year_input")} *',
                            min_value=1800,
                            max_value=2030,
                            value=int(current_year),
                            step=1,
                        )
                    with e2:
                        edit_rating = st.number_input(
                            f'{t("book_rating_input")} *',
                            min_value=0.0,
                            max_value=5.0,
                            value=float(current_rating),
                            step=0.1,
                        )
                    with e3:
                        edit_language = st.text_input(
                            f'{t("book_language_input")} *',
                            value=current_book["language"] or "",
                        )

                    e4, e5, e6 = st.columns(3)
                    with e4:
                        edit_pages = st.text_input(
                            t("book_pages_input"),
                            value=str(current_book["pages"]) if current_book["pages"] is not None else "",
                        )
                    with e5:
                        edit_num_ratings = st.text_input(
                            t("book_num_ratings_input"),
                            value=str(current_book["num_ratings"]) if current_book["num_ratings"] is not None else "",
                        )
                    with e6:
                        edit_reviews = st.text_input(
                            t("book_reviews_count_input"),
                            value=str(current_book["text_reviews_count"]) if current_book["text_reviews_count"] is not None else "",
                        )

                    edit_publisher = st.text_input(
                        t("book_publisher_input"),
                        value=current_book["publisher_name"] or "",
                    )
                    edit_isbn = st.text_input(
                        t("book_isbn_input"),
                        value=current_book["isbn"] or "",
                    )
                    edit_isbn13 = st.text_input(
                        t("book_isbn13_input"),
                        value=str(current_book["isbn13"]) if current_book["isbn13"] is not None else "",
                    )

                    update_book_submit = st.form_submit_button(
                        t("update_book_btn"),
                        type="primary",
                    )

                if update_book_submit:
                    payload, errors = sanitize_book_payload(
                        title=edit_title,
                        authors_text=edit_authors,
                        publish_year=int(edit_publish_year),
                        rating=float(edit_rating),
                        language=edit_language,
                        pages_text=edit_pages,
                        num_ratings_text=edit_num_ratings,
                        reviews_text=edit_reviews,
                        publisher=edit_publisher,
                        isbn=edit_isbn,
                        isbn13_text=edit_isbn13,
                        t=t,
                    )
                    if errors:
                        for msg in errors:
                            st.error(msg)
                    else:
                        with conn:
                            conn.execute(
                                """
                                UPDATE books
                                SET
                                    title = ?,
                                    isbn = ?,
                                    isbn13 = ?,
                                    language = ?,
                                    pages = ?,
                                    publisher_name = ?,
                                    publish_year = ?,
                                    num_ratings = ?,
                                    rating = ?,
                                    text_reviews_count = ?
                                WHERE book_id = ?
                                """,
                                (
                                    payload["title"],
                                    payload["isbn"],
                                    payload["isbn13"],
                                    payload["language"],
                                    payload["pages"],
                                    payload["publisher_name"],
                                    payload["publish_year"],
                                    payload["num_ratings"],
                                    payload["rating"],
                                    payload["text_reviews_count"],
                                    selected_edit_book_id,
                                ),
                            )
                            conn.execute(
                                "DELETE FROM book_authors WHERE book_id = ?",
                                (selected_edit_book_id,),
                            )
                            for idx, author_name in enumerate(payload["authors"], start=1):
                                author_id = ensure_author_id(conn, author_name)
                                conn.execute(
                                    "INSERT INTO book_authors(book_id, author_id, author_order) VALUES (?, ?, ?)",
                                    (selected_edit_book_id, author_id, idx),
                                )

                        st.success(t("book_updated"))
                        st.rerun()

                confirm_delete_book = st.checkbox(
                    t("confirm_delete_book"),
                    key=f"confirm_delete_book_{selected_edit_book_id}",
                )
                if st.button(
                    t("delete_book_btn"),
                    key=f"delete_book_btn_{selected_edit_book_id}",
                    type="secondary",
                ):
                    if not confirm_delete_book:
                        st.warning(t("confirm_delete_required"))
                    else:
                        with conn:
                            conn.execute(
                                "DELETE FROM books WHERE book_id = ?",
                                (selected_edit_book_id,),
                            )
                        st.success(t("book_deleted"))
                        st.rerun()


def page_analytics(conn: sqlite3.Connection, t, lang: str) -> None:
    st.header(t("page_analytics"))
    page_subtitle(t("analytics_hint"))

    # --- KPI metrics row (accuracy-oriented) ---
    total_books = run_scalar(conn, "SELECT COUNT(*) FROM books")
    total_authors = run_scalar(conn, "SELECT COUNT(*) FROM authors")
    total_publishers = run_scalar(
        conn,
        "SELECT COUNT(DISTINCT publisher_name) FROM books WHERE publisher_name IS NOT NULL",
    )
    avg_rating = run_scalar(conn, "SELECT AVG(rating) FROM books WHERE rating IS NOT NULL")
    weighted_avg_rating = run_scalar(
        conn,
        """
        SELECT
            CASE
                WHEN SUM(COALESCE(num_ratings, 0)) = 0 THEN NULL
                ELSE SUM(rating * num_ratings) * 1.0 / SUM(num_ratings)
            END
        FROM books
        WHERE rating IS NOT NULL AND num_ratings IS NOT NULL AND num_ratings > 0
        """,
    )
    rating_values = run_query(conn, "SELECT rating FROM books WHERE rating IS NOT NULL")
    median_rating = (
        float(pd.Series([r["rating"] for r in rating_values]).median())
        if rating_values
        else None
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(t("metric_books"), f"{total_books:,}")
    c2.metric(t("metric_authors"), f"{total_authors:,}")
    c3.metric(t("metric_publishers"), f"{total_publishers:,}")
    c4.metric(
        t("metric_avg_rating"),
        f"⭐ {weighted_avg_rating:.2f}" if weighted_avg_rating is not None else "—",
        delta=(
            t("rating_weight_delta", value=f"{avg_rating:.2f}")
            if avg_rating is not None and weighted_avg_rating is not None
            else None
        ),
    )
    c5.metric(
        t("metric_median_rating"),
        f"⭐ {median_rating:.2f}" if median_rating is not None else "—",
    )

    st.markdown("")

    # --- Top publishers ---
    section_title(t("top_publishers"))
    top_pubs = run_query(
        conn,
        """
        SELECT publisher_name, COUNT(*) AS book_count
        FROM books
        WHERE publisher_name IS NOT NULL
        GROUP BY publisher_name
        ORDER BY book_count DESC
        LIMIT 20
        """,
    )
    if top_pubs:
        df_pubs = pd.DataFrame(top_pubs)
        df_pubs = _rename_df(df_pubs, lang)
        st.bar_chart(
            df_pubs,
            x=_col("publisher_name", lang),
            y=_col("book_count", lang),
            horizontal=True,
            height=420,
        )

    # --- Rating distribution: count vs rating volume ---
    rating_bucket_rows = run_query(
        conn,
        """
        SELECT
            ROUND(rating * 2) / 2.0 AS rating_bucket,
            COUNT(*) AS count,
            SUM(COALESCE(num_ratings, 0)) AS ratings_volume
        FROM books
        WHERE rating IS NOT NULL
        GROUP BY rating_bucket
        ORDER BY rating_bucket
        """,
    )
    left, right = st.columns(2)
    with left:
        section_title(t("rating_distribution"))
        if rating_bucket_rows:
            df_rating = pd.DataFrame(rating_bucket_rows)
            df_rating = _rename_df(df_rating, lang)
            st.bar_chart(
                df_rating,
                x=_col("rating_bucket", lang),
                y=_col("count", lang),
                height=320,
            )
    with right:
        section_title(t("rating_volume_distribution"))
        if rating_bucket_rows:
            df_rating_volume = pd.DataFrame(rating_bucket_rows)
            df_rating_volume = _rename_df(df_rating_volume, lang)
            st.line_chart(
                df_rating_volume,
                x=_col("rating_bucket", lang),
                y=_col("ratings_volume", lang),
                height=320,
            )

    # --- Language distribution ---
    section_title(t("language_dist"))
    lang_dist = run_query(
        conn,
        """
        SELECT COALESCE(language, 'Unknown') AS language, COUNT(*) AS count
        FROM books
        GROUP BY language
        ORDER BY count DESC
        LIMIT 12
        """,
    )
    if lang_dist:
        df_lang = pd.DataFrame(lang_dist)
        df_lang = _rename_df(df_lang, lang)
        st.bar_chart(
            df_lang,
            x=_col("language", lang),
            y=_col("count", lang),
            horizontal=True,
            height=360,
        )

    # --- Books by year trend + YoY change ---
    section_title(t("books_by_year"))
    books_by_year = run_query(
        conn,
        """
        SELECT publish_year, COUNT(*) AS books_count
        FROM books
        WHERE publish_year IS NOT NULL AND publish_year >= 1950
        GROUP BY publish_year
        ORDER BY publish_year ASC
        """,
    )
    if books_by_year:
        df_year = pd.DataFrame(books_by_year)
        df_year["rolling_avg_5y"] = (
            df_year["books_count"].rolling(window=5, min_periods=1).mean().round(2)
        )
        df_year["yearly_change_pct"] = (
            df_year["books_count"].pct_change().fillna(0).mul(100).round(2)
        )

        year_left, year_right = st.columns([2, 1])
        with year_left:
            df_year_chart = _rename_df(
                df_year[["publish_year", "books_count", "rolling_avg_5y"]]
                .rename(columns={"rolling_avg_5y": "books_count_rolling"}),
                lang,
            )
            st.line_chart(
                df_year_chart,
                x=_col("publish_year", lang),
                y=[_col("books_count", lang), _col("books_count_rolling", lang)],
                height=340,
            )
        with year_right:
            st.caption(t("books_yoy_change"))
            yoy = _rename_df(
                df_year[["publish_year", "yearly_change_pct"]].tail(20),
                lang,
            )
            st.bar_chart(
                yoy,
                x=_col("publish_year", lang),
                y=_col("yearly_change_pct", lang),
                height=340,
            )

    # --- Pages vs rating scatter ---
    section_title(t("pages_vs_rating"))
    pages_vs_rating = run_query(
        conn,
        """
        SELECT pages, rating, num_ratings
        FROM books
        WHERE pages IS NOT NULL
          AND rating IS NOT NULL
          AND pages BETWEEN 40 AND 1800
          AND num_ratings IS NOT NULL
        ORDER BY num_ratings DESC
        LIMIT 1800
        """,
    )
    if pages_vs_rating:
        df_pages = pd.DataFrame(pages_vs_rating)
        corr = df_pages["pages"].corr(df_pages["rating"])
        st.caption(f"Pearson r = {corr:.3f}" if pd.notna(corr) else "Pearson r = —")
        df_pages = _rename_df(df_pages, lang)
        st.scatter_chart(
            df_pages,
            x=_col("pages", lang),
            y=_col("rating", lang),
            height=360,
        )

    # --- Top authors: scatter + table ---
    section_title(t("top_authors_scatter"))
    author_scatter = run_query(
        conn,
        """
        SELECT
            a.author_name,
            COUNT(*) AS books_count,
            ROUND(AVG(b.rating), 2) AS avg_rating
        FROM book_authors ba
        JOIN authors a ON ba.author_id = a.author_id
        JOIN books b ON ba.book_id = b.book_id
        WHERE b.rating IS NOT NULL
        GROUP BY a.author_id, a.author_name
        HAVING COUNT(*) >= 3
        ORDER BY books_count DESC
        LIMIT 250
        """,
    )
    if author_scatter:
        df_author_scatter = pd.DataFrame(author_scatter)
        df_author_scatter = _rename_df(df_author_scatter, lang)
        st.scatter_chart(
            df_author_scatter,
            x=_col("books_count", lang),
            y=_col("avg_rating", lang),
            height=340,
        )

    section_title(t("top_authors"))
    top_authors = run_query(
        conn,
        """
        SELECT
            a.author_name,
            COUNT(*) AS books_count,
            ROUND(AVG(b.rating), 2) AS avg_rating
        FROM book_authors ba
        JOIN authors a ON ba.author_id = a.author_id
        JOIN books b ON ba.book_id = b.book_id
        WHERE b.rating IS NOT NULL
        GROUP BY a.author_id, a.author_name
        HAVING COUNT(*) >= 5
        ORDER BY avg_rating DESC, books_count DESC
        LIMIT 20
        """,
    )
    show_table(top_authors, t, lang=lang, height=420)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    inject_theme()

    # --- Language selector (top-right via columns) ---
    if "lang" not in st.session_state:
        st.session_state.lang = "zh"
    if "page" not in st.session_state:
        st.session_state.page = "search"

    # --- Top navigation bar ---
    nav_left, nav_right = st.columns([8, 1])
    with nav_left:
        t_temp = get_text_fn(st.session_state.lang)
        pages = [
            ("search", "page_search"),
            ("analytics", "page_analytics"),
            ("reading_list", "page_reading_list"),
        ]
        cols = st.columns(len(pages) + 1)
        with cols[0]:
            st.markdown(
                f'<div class="nav-brand">{t_temp("nav_brand")}</div>',
                unsafe_allow_html=True,
            )
        for idx, (key, label_key) in enumerate(pages, 1):
            with cols[idx]:
                is_active = st.session_state.page == key
                if st.button(
                    t_temp(label_key),
                    key=f"nav_{key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.page = key
                    st.rerun()

    with nav_right:
        lang_code = st.selectbox(
            "🌐",
            ["zh", "en"],
            format_func=lambda c: "中文" if c == "zh" else "EN",
            index=0 if st.session_state.lang == "zh" else 1,
            label_visibility="collapsed",
        )
        if lang_code != st.session_state.lang:
            st.session_state.lang = lang_code
            st.rerun()

    lang = st.session_state.lang
    t = get_text_fn(lang)
    page = st.session_state.page

    st.markdown("---")

    render_hero(t)

    if not DB_PATH.exists():
        st.error(t("db_not_found"))
        st.code("python3 scripts/load_new_data.py")
        return

    conn = get_conn(str(DB_PATH))
    ensure_app_schema(conn)

    # --- Page dispatch ---
    if page == "search":
        page_search(conn, t, lang)
    elif page == "analytics":
        page_analytics(conn, t, lang)
    else:
        page_reading_list(conn, t, lang)

    # --- Footer ---
    st.markdown(
        f'<div class="app-footer">{t("footer_built_with")}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
