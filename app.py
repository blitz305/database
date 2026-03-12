#!/usr/bin/env python3
"""Books Database Explorer — Streamlit frontend (v2 redesign)."""

import os
import sqlite3
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
        "no_data": "No data found for current filters.",
        "title_keyword": "Title keyword",
        "title_keyword_placeholder": "e.g. Harry Potter",
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
        "filter_panel": "⚙️  Filters",
        "results_panel": "📋  Results",
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
        "select_book_hint": "Select a row to view richer details from Google Books",
        "select_book": "Select a book to view details",
        "book_by": "Author: {authors}",
        "book_publisher": "Publisher",
        "book_pages": "Pages",
        "book_published": "Published",
        "book_isbn": "ISBN",
        "book_categories": "Categories",
        "book_preview": "Preview on Google Books",
        "book_description": "Description",
        "book_no_result": "No results found on Google Books for this title.",
        "book_api_error": "Could not connect to Google Books API.",
        "book_loading": "Looking up on Google Books …",
        "rating_compare": "Rating Comparison",
        "rating_goodreads": "Goodreads",
        "rating_google": "Google Books",
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
        "no_data": "当前筛选条件下没有数据。",
        "title_keyword": "书名关键词",
        "title_keyword_placeholder": "例如：哈利·波特",
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
        "filter_panel": "⚙️  筛选条件",
        "results_panel": "📋  查询结果",
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
        "select_book_hint": "点击表格中的行，即可查看来自 Google Books 的详细信息",
        "select_book": "选择一本书查看详情",
        "book_by": "作者：{authors}",
        "book_publisher": "出版社",
        "book_pages": "页数",
        "book_published": "出版日期",
        "book_isbn": "ISBN",
        "book_categories": "分类",
        "book_preview": "在 Google Books 中预览",
        "book_description": "简介",
        "book_no_result": "未在 Google Books 中找到该书。",
        "book_api_error": "无法连接 Google Books API。",
        "book_loading": "正在查询 Google Books …",
        "rating_compare": "评分对比",
        "rating_goodreads": "Goodreads",
        "rating_google": "Google Books",
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


def show_table(rows: List[dict], t, lang: str = "en", height: int = 420) -> None:
    if rows:
        row_count_badge(len(rows), t)
        st.dataframe(_rename_rows(rows, lang), use_container_width=True, hide_index=True, height=height)
    else:
        st.info(t("no_data"))


# ---------------------------------------------------------------------------
# Google Books API
# ---------------------------------------------------------------------------
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_google_book(title: str, author: str | None = None) -> dict | None:
    """Query Google Books API by title (+ optional author) and return the best match."""
    q = f'intitle:{title}'
    if author:
        q += f'+inauthor:{author}'
    try:
        resp = requests.get(
            GOOGLE_BOOKS_URL,
            params={"q": q, "maxResults": 1},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    items = data.get("items")
    if not items:
        return None

    vol = items[0].get("volumeInfo", {})
    cover = vol.get("imageLinks", {})
    identifiers = {i["type"]: i["identifier"] for i in vol.get("industryIdentifiers", [])}

    return {
        "title": vol.get("title", title),
        "authors": vol.get("authors", []),
        "publisher": vol.get("publisher"),
        "published_date": vol.get("publishedDate"),
        "description": vol.get("description"),
        "page_count": vol.get("pageCount"),
        "categories": vol.get("categories", []),
        "thumbnail": cover.get("thumbnail") or cover.get("smallThumbnail"),
        "preview_link": vol.get("previewLink"),
        "isbn_13": identifiers.get("ISBN_13"),
        "isbn_10": identifiers.get("ISBN_10"),
        "google_rating": vol.get("averageRating"),
        "google_ratings_count": vol.get("ratingsCount"),
    }


def render_book_card(info: dict, t, db_book: dict | None = None) -> None:
    """Render a right-side sliding panel with book details from Google Books."""
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

    panel = (
        '<div class="book-panel-overlay">'
        '<div class="book-panel-header">'
        f'<span class="book-panel-header-title">{header_label}</span>'
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
    )
    st.markdown(panel, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_search(conn: sqlite3.Connection, t, lang: str) -> None:
    st.header(t("page_search"))
    page_subtitle(t("search_hint"))

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
        b.publish_year,
        b.rating,
        b.num_ratings,
        b.pages,
        b.language
    FROM books b
    WHERE 1=1
    """
    params: List[Any] = []

    if keyword.strip():
        sql += " AND b.title LIKE ?"
        params.append(f"%{keyword.strip()}%")

    sql += " AND b.publish_year BETWEEN ? AND ?"
    params.extend([year_range[0], year_range[1]])

    sql += " AND b.rating BETWEEN ? AND ?"
    params.extend([rating_range[0], rating_range[1]])

    if selected_lang is not None:
        sql += " AND b.language = ?"
        params.append(selected_lang)

    sql += " ORDER BY b.rating DESC, b.title ASC"

    rows = run_query(conn, sql, params)

    # Separate book_id from display rows
    book_id_map = {r["title"]: r["book_id"] for r in rows}
    display_rows = [{k: v for k, v in r.items() if k != "book_id"} for r in rows]

    section_title(t("results_panel"))

    if not display_rows:
        st.info(t("no_data"))
        return

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

    # --- Google Books detail on row click ---
    selected_indices = event.selection.rows if event and event.selection else []
    if selected_indices:
        idx = selected_indices[0]
        selected_title = display_rows[idx]["title"]

        # Look up author for better matching
        bid = book_id_map.get(selected_title)
        author_row = run_query(
            conn,
            """SELECT a.author_name FROM authors a
               JOIN book_authors ba ON a.author_id = ba.author_id
               WHERE ba.book_id = ? ORDER BY ba.author_order LIMIT 1""",
            (bid,),
        ) if bid else []
        author_name = author_row[0]["author_name"] if author_row else None

        with st.spinner(t("book_loading")):
            info = fetch_google_book(selected_title, author_name)
        if info is None:
            st.warning(t("book_no_result"))
        else:
            # Pass the DB row for rating comparison
            db_book = rows[idx] if idx < len(rows) else None
            render_book_card(info, t, db_book=db_book)


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
        pages = [("search", "page_search"), ("analytics", "page_analytics")]
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

    # --- Page dispatch ---
    if page == "search":
        page_search(conn, t, lang)
    else:
        page_analytics(conn, t, lang)

    # --- Footer ---
    st.markdown(
        f'<div class="app-footer">{t("footer_built_with")}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
