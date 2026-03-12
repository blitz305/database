# Books Database Work

一个基于 Goodreads 图书数据集的小型数据应用项目，包含：
- CSV 清洗与质量检查
- SQLite 规范化建模与导入
- Streamlit 可视化查询界面（中英双语 + 浅色/深色主题）

## 1. 项目结构

```text
database_work/
├─ app.py                          # Streamlit 前端入口
├─ books_1.Best_Books_Ever.csv     # 原始数据
├─ processed/
│  └─ books_clean.csv              # 清洗后数据
├─ reports/
│  └─ eda_summary.md               # EDA 与清洗报告
├─ scripts/
│  ├─ preprocess_books.py          # 清洗脚本
│  └─ load_to_sqlite.py            # 入库脚本
├─ sql/
│  └─ schema.sql                   # SQLite 表结构
├─ data/
│  └─ genre_zh_map.csv             # 流派中英映射
└─ database/
   └─ books.db                     # SQLite 数据库
```

## 2. 功能说明

### 数据处理链路
1. `scripts/preprocess_books.py`  
   读取原始 CSV，做字段清洗、类型解析、年份规范化、重复处理。  
   输出：
   - `processed/books_clean.csv`
   - `reports/eda_summary.md`

2. `scripts/load_to_sqlite.py`  
   基于 `sql/schema.sql` 建表并导入清洗结果，写入 `database/books.db`。

### 前端（Streamlit）
- 页面：
  - 数据浏览（Data Browser）
  - 条件查询（Filtered Search）
  - 关系视图（Book ↔ Authors / Book ↔ Genres）
  - 统计分析（Analytics）
- 语言：中文 / English
- 主题：浅色 / 深色（侧边栏切换）
- 当前前端已隐藏 `book_id` 列（数据库内部仍保留主键）

## 3. 快速开始

### 3.1 环境准备
项目没有锁定依赖文件，至少需要：
- Python 3.10+
- `streamlit`

安装示例：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit
```

### 3.2 数据清洗（可选，已有结果可跳过）

```bash
python3 scripts/preprocess_books.py
```

### 3.3 导入 SQLite（首次或需重建时）

```bash
python3 scripts/load_to_sqlite.py --overwrite
```

可选参数：
- `--csv` 指定清洗后 CSV 路径
- `--schema` 指定 schema 文件
- `--db` 指定输出数据库路径

### 3.4 启动前端

```bash
streamlit run app.py
```

不要使用 `python app.py` 直接运行，否则会出现 `missing ScriptRunContext` 警告且不按 Web 应用方式工作。

## 4. 常见问题

### Q1: 启动后提示 `Database file not found`
数据库不存在或路径不对。先执行：

```bash
python3 scripts/load_to_sqlite.py --overwrite
```

或通过环境变量覆盖数据库路径：

```bash
BOOKS_DB_PATH=/your/path/books.db streamlit run app.py
```

### Q2: 页面样式和组件颜色冲突
这是主题样式未刷新导致。先重启 Streamlit，再浏览器强制刷新（`Ctrl+F5`）。

### Q3: `ModuleNotFoundError: No module named 'streamlit'`
当前 Python 环境未安装 Streamlit，请在该环境执行：

```bash
pip install streamlit
```

## 5. 面向后续维护者

### 5.1 想改页面文案/语言
- 修改 `app.py` 内 `TRANSLATIONS` 字典。

### 5.2 想改主题样式（浅色/深色）
- 修改 `app.py` 内 `inject_theme(mode)`。
- 主题切换 UI 在 `main()` 的侧边栏 `Theme/主题` 单选框。

### 5.3 想改查询逻辑
- 页面函数：
  - `page_browser`
  - `page_search`
  - `page_relations`
  - `page_analytics`
- SQL 语句都在上述函数内集中维护。

### 5.4 想改数据库结构
1. 先改 `sql/schema.sql`
2. 再同步 `scripts/load_to_sqlite.py` 的插入逻辑
3. 最后重建库并验证前端查询

## 6. 开发建议

- 前端改动后，先本地验证：
  ```bash
  python3 -m py_compile app.py
  streamlit run app.py
  ```
- 数据链路改动后，建议全流程回归：
  1. `preprocess_books.py`
  2. `load_to_sqlite.py --overwrite`
  3. Streamlit 页面抽样检查（浏览、搜索、关系、统计）

