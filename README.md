# Books Database Explorer

[English](#english) | [中文](#中文)

---

## English

# 📚 Books Database Explorer

A **Streamlit**-based book data explorer using a curated high-quality subset from ***Goodreads*** as the local database. It supports search, analytics, and detailed book viewing. Beyond local data, it integrates the ***Google Books API*** to enrich book information, making it easy to preview books and access related links. The interface is clean and modern, very easy to start with, and suitable for both quick browsing and deeper analysis.
<p align="center">
  <img src="assets/images/image-6.png" alt="Book Detail Panel" width="780" />
</p>

## Quick Start


### Install

```bash
pip install streamlit pandas requests
```

### Launch

```bash
streamlit run app.py
```
Then open the URL shown in terminal (usually `http://localhost:8501`).

## Simple Usage Guide


On the filtered search page, you can combine publish year, rating, and language filters to quickly narrow down a large set of books.  
Select the checkbox on the left of the book you want to inspect, and the app will call the ***Google Books API*** to fetch richer details, including cover, publisher, publish date, categories, ISBN, and description. It also provides quick links (such as Goodreads, Douban, and StoryGraph).



## Data Source
This project uses the Kaggle dataset **“Goodreads-books”**.
- Source: <https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks>
- Maintainer: `soumik`
- License: [CC0 1.0 (Public Domain Dedication)](https://creativecommons.org/publicdomain/zero/1.0/)
- Source page license label: `CC0: Public Domain` (accessed on `2026-03-12`)
  
This project uses a cleaned subset of the original dataset.

---

## 中文
# 📚图书数据库浏览器

一个基于 **Streamlit** 的图书数据探索浏览器，精选了 ***Goodreads*** 的一部分高质量数据集作为本地数据库，支持检索、分析和书籍详情查看。不止于本地，浏览器还集成了 ***Google Books API*** 来丰富书籍信息，能够快速预览书籍内容和相关链接。界面设计简洁现代，上手极其简单，适合快速浏览和深入分析。
<p align="center">
  <img src="assets/images/image.png" alt="Book Detail Panel" width="780" />
</p>

## 快速入门


### 安装

```bash
pip install streamlit pandas requests
```

### 启动

```bash
streamlit run app.py
```
然后在浏览器打开终端给出的地址（通常是 `http://localhost:8501`）。

## 简单的使用说明
条件查询页面可以根据书籍出版年份，评分和语言进行组合过滤，快速筛选大批书本
勾选想了解的书籍左边的方框，即可调用 ***Google book API*** 进行查询，获得书籍更为详细的信息，包括封面、出版社、出版日期、类别、ISBN 和描述等，还会提供一些快捷链接（如 Goodreads、豆瓣、StoryGraph 等）。


## 数据来源
本项目数据来源于 Kaggle 数据集 **“Goodreads-books”**。
- 来源: <https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks>
- 维护者: `soumik`
- 许可证: [CC0 1.0（Public Domain Dedication）](https://creativecommons.org/publicdomain/zero/1.0/)
- 数据页许可标注: `CC0: Public Domain`（访问日期：`2026-03-12`）
  
本项目使用的是清洗后的子集数据。
