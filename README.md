# pdf_to_markdown - PDF转Markdown工具使用说明

## 项目简介

pdf_to_markdown 是一个强大的PDF处理工具，可以帮助您：
1. 解析PDF文件并提取结构化内容
2. 处理和合并解析后的报告，进行文本清理
3. 将结果导出为多种格式（JSON、Markdown）

## 系统要求

- Windows 10/11
- Python 3.8 或更高版本
- 至少 4GB 内存
- 足够的磁盘空间存储PDF文件和输出结果

## 安装步骤

### 第一步：安装Python

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载最新版本的Python（建议3.9或以上）
3. 运行安装程序时，**务必勾选"Add Python to PATH"**
4. 安装完成后，按 `Win + R`，输入 `cmd`，回车
5. 在命令行中输入 `python --version`，如果显示版本号则安装成功

### 第二步：下载项目文件

1. 将整个项目文件夹下载到您的电脑上
2. 建议放在容易找到的位置，如 `C:\Users\您的用户名\Desktop\pdf_to_markdown`

### 第三步：安装依赖包

1. 按 `Win + R`，输入 `cmd`，回车打开命令行
2. 使用 `cd` 命令进入项目文件夹，例如：
   ```
   cd C:\Users\您的用户名\Desktop\pdf_to_markdown
   ```
3. 安装必需的Python包：
   ```
   pip install docling tabulate pathlib
   ```

## 文件夹结构说明

```
pdf_to_markdown/
├── main.py                    # 主程序文件
├── src/                       # 源代码文件夹
│   ├── pdf_parsing.py         # PDF解析模块
│   └── parsed_reports_merging.py  # 报告合并模块
├── pdfs/                      # 放置要处理的PDF文件
├── parsed_reports/            # 解析后的JSON文件存储位置
├── merged_reports/            # 合并处理后的文件存储位置
├── markdown/                  # 最终Markdown文件存储位置
└── pdf_to_markdown.log        # 程序运行日志
```

## 使用方法

### 准备工作

1. 将您要处理的PDF文件放入 `pdfs/` 文件夹中
2. 打开命令行并进入项目目录

### 方法一：一键完整处理（推荐新手）

如果您想一次性完成所有处理步骤，使用以下命令：

```bash
python main.py pipeline --input pdfs/ --output final_output/
```

这个命令会：
1. 解析 `pdfs/` 文件夹中的所有PDF文件
2. 处理和清理文本内容
3. 导出为Markdown格式
4. 所有结果保存在 `final_output/` 文件夹中

### 方法二：分步骤处理（适合高级用户）

#### 步骤1：解析PDF文件
```bash
python main.py parse --input pdfs/ --output parsed_reports/
```

#### 步骤2：处理和合并报告
```bash
python main.py merge --input parsed_reports/ --output merged_reports/
```

#### 步骤3：导出为Markdown格式
```bash
python main.py export --input merged_reports/ --output markdown/ --format markdown
```

### 其他有用的命令

#### 查看文件夹内容
```bash
python main.py list --directory pdfs/
```

#### 查看帮助信息
```bash
python main.py --help
```

#### 查看特定命令的帮助
```bash
python main.py parse --help
python main.py merge --help
python main.py export --help
```

## 输出文件说明

### 解析阶段输出（parsed_reports/）
- 每个PDF文件对应一个JSON文件
- 包含提取的文本、表格、图片等结构化信息

### 合并阶段输出（merged_reports/）
- 清理和格式化后的JSON文件
- 包含处理摘要文件 `processing_summary.json`

### 最终输出（markdown/）
- 每个PDF对应一个 `.md` 文件
- 可以用任何文本编辑器或Markdown查看器打开
- 内容按页面组织，便于阅读

## 常见问题解决

### 问题1：提示"python不是内部或外部命令"
**解决方案：**
- 重新安装Python，确保勾选"Add Python to PATH"
- 或者使用完整路径，如：`C:\Python39\python.exe main.py`

### 问题2：提示缺少某个模块
**解决方案：**
```bash
pip install 模块名
```
例如：`pip install docling`

### 问题3：PDF文件处理失败
**解决方案：**
- 检查PDF文件是否损坏
- 确保PDF文件不是扫描版（纯图片）
- 查看 `pdf_to_markdown.log` 文件了解详细错误信息

### 问题4：内存不足
**解决方案：**
- 一次处理较少的PDF文件
- 关闭其他占用内存的程序
- 考虑升级电脑内存

### 问题5：处理速度慢
**解决方案：**
- 大文件需要较长时间，请耐心等待
- 可以先用小文件测试
- 查看命令行输出了解处理进度

## 高级选项

### 表格处理选项
如果您需要特殊的表格处理，可以使用以下选项：

```bash
# 使用序列化表格格式
python main.py merge --input parsed_reports/ --output merged_reports/ --use-serialized-tables

# 用序列化格式替代Markdown表格
python main.py merge --input parsed_reports/ --output merged_reports/ --serialized-instead-of-markdown
```

## 技术支持

如果遇到问题：
1. 首先查看 `pdf_to_markdown.log` 日志文件
2. 确认所有依赖包都已正确安装
3. 检查PDF文件格式和完整性
4. 确保有足够的磁盘空间

## 使用示例

假设您有3个PDF文件要处理：

1. 将PDF文件放入 `pdfs/` 文件夹
2. 打开命令行，进入项目目录
3. 运行：`python main.py pipeline --input pdfs/ --output results/`
4. 等待处理完成
5. 在 `results/markdown/` 文件夹中查看转换后的Markdown文件

处理完成后，您会看到类似这样的输出：
```
INFO - Starting complete processing pipeline
INFO - Step 1/3: Parsing PDFs
INFO - Found 3 PDF files to process
INFO - Step 2/3: Merging reports
INFO - Successfully processed 3 reports
INFO - Step 3/3: Exporting to markdown
INFO - Pipeline completed! Results available in: results/
```

## 注意事项

1. **文件路径**：避免使用包含中文或特殊字符的文件夹路径
2. **文件大小**：单个PDF文件建议不超过100MB
3. **批量处理**：一次处理大量文件时，建议分批进行
4. **备份**：处理重要文件前请先备份原始PDF文件
5. **编码**：输出的文件使用UTF-8编码，确保文本编辑器支持

## 鸣谢

本项目基于优秀的开源技术和理念构建，特此感谢：

### 原作者贡献
- **Ilya Rice** - 企业RAG挑战赛冠军，本项目的核心技术架构和算法设计灵感来源
- 技术文章：[How I Won the Enterprise RAG Challenge](https://abdullin.com/ilya/how-to-build-best-rag/) - 详细介绍了从零到SOTA的RAG系统构建方法
- 开源代码：[RAG-Challenge-2](https://github.com/IlyaRice/RAG-Challenge-2) - 提供了完整的获奖解决方案实现

### 核心技术理念
本项目采用了Ilya Rice在RAG挑战赛中验证的关键技术：
- **高质量PDF解析** - 使用Docling进行结构化内容提取
- **智能文本清理** - 正则表达式批处理和OCR后备方案
- **表格序列化** - 将复杂表格转换为语义独立的文本块
- **分页检索策略** - 小块检索+完整页面上下文的混合方法
- **LLM重排序** - 使用GPT-4o-mini进行相关性评分优化

### 开源项目依赖
- **Docling** - IBM开发的先进PDF解析库，在RAG挑战赛中表现最佳
- **Tabulate** - 优雅的表格格式化工具，支持Markdown输出
- **Python** 生态系统 - 提供丰富的文档处理和机器学习工具链

### 技术创新致敬
- **结构化输出 (Structured Output)** - 确保LLM响应格式的一致性
- **思维链推理 (Chain of Thought)** - 提高复杂问题的解答质量
- **多路由架构** - 针对不同类型查询的专门化处理流程
- **父文档检索** - 平衡检索精度和上下文完整性的创新方法

### 特别感谢
感谢Ilya Rice在RAG技术领域的开创性工作和无私分享。他的获奖方案不仅在企业RAG挑战赛中取得了第一名的优异成绩，更为整个社区提供了宝贵的技术洞察和最佳实践。本项目正是在这些先进理念的指导下，为用户提供高质量的PDF到Markdown转换服务。

同时感谢所有为文档处理、自然语言处理和RAG技术发展做出贡献的开发者和研究者们。

---

祝您使用愉快！