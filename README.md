# FastGPT 内容处理器

一个用于管理和处理 FastGPT 知识库内容的命令行工具，支持知识库查询、内容搜索、文件上传，以及微信公众号文章的下载、清理和上传。

## 功能特性

- **list-datasets**: 列出所有 FastGPT 知识库
- **list-collections**: 列出指定知识库下的文章/集合
- **search**: 在知识库中搜索内容（语义搜索）
- **upload-file**: 上传单个 Markdown 文件到知识库
- **upload-folder**: 批量上传整个文件夹的 Markdown 文件
- **download-wechat**: 批量下载微信公众号文章（通过 MCP 服务）
- **clean-wechat**: 两阶段清理微信公众号文章
- **download-and-clean**: 一站式处理（下载 → 清理 → 上传）

## 安装与运行

### 推荐方式：uv

```bash
cd fastgpt-content-processor
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
```

### 标准方式：venv

```bash
cd fastgpt-content-processor
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
```

### 运行方式

```bash
python3 main.py --help
python3 main.py list-datasets
python3 main.py search --dataset-id 697b19a113081cf58b45cac3 --query "KRAS 突变"
```

> 提示：如果你直接在系统环境中运行，可能会出现 `python: command not found`。本项目统一建议使用 `python3`，并优先在独立虚拟环境中执行。

## 环境变量配置

在 `.env` 文件中配置：

```env
# FastGPT 配置
FASTGPT_BASE_URL=https://your-fastgpt-domain.com
FASTGPT_API_KEY=your-api-key-here

# 翻译模型配置（可选）
TRANSLATE_PRIMARY=qwen
TRANSLATE_FALLBACK=glm
QWEN_API_KEY=your-qwen-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
GLM_API_KEY=your-glm-key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

## 使用示例

### 列出所有知识库

```bash
python3 main.py list-datasets
```

### 列出知识库下的文章

```bash
python3 main.py list-collections --dataset-id 697b19a113081cf58b45cac3
```

### 在知识库中搜索

```bash
python3 main.py search --dataset-id 697b19a113081cf58b45cac3 --query "KRAS 突变"
```

### 上传单个文件

```bash
python3 main.py upload-file --file article.md --dataset-id 697b19a113081cf58b45cac3
```

### 批量上传文件夹

```bash
python3 main.py upload-folder --folder ./articles --dataset-id 697b19a113081cf58b45cac3
```

### 下载微信公众号文章

创建 `urls.txt`，每行一个微信文章 URL，然后：

```bash
python3 main.py download-wechat --urls urls.txt --output ./wechat-downloads
```

### 清理微信公众号文章

```bash
python3 main.py clean-wechat --input ./wechat-downloads --output ./cleaned-articles
```

### 一站式处理（下载 → 清理 → 上传）

```bash
python3 main.py download-and-clean \
  --urls urls.txt \
  --output ./wechat-downloads \
  --cleaned-output ./cleaned-articles \
  --dataset-id 697b19a113081cf58b45cac3
```

## 项目结构

```
fastgpt-content-processor/
├── main.py                      # 主程序入口
├── fastgpt_sync.py              # FastGPT API 封装
├── fetchers/                    # 内容抓取模块
│   ├── wechat_mcp.py           # 微信文章下载（MCP 服务）
│   └── file.py                 # 本地文件读取
├── cleaners/                    # 内容清理模块
│   ├── format_cleaner.py       # 阶段 1：格式清理
│   ├── frontmatter_doctor.py   # 阶段 2：Frontmatter 标准化
│   ├── wechat_markdown.py      # 微信文章清理（整合两阶段）
│   └── markdown.py             # Markdown 通用清理
├── utils/                       # 工具函数
│   ├── hash.py                 # Hash 计算
│   └── dedup.py                # 去重逻辑
├── tests/                       # 测试目录
├── .env.example                 # 环境变量模板
├── requirements.txt             # Python 依赖
└── README.md                    # 本文档
```

## 测试

请查看 [`tests/README.md`](tests/README.md)，其中列出了核心逻辑测试范围与后续测试主题建议。

### 运行测试

```bash
python3 -m pytest
```

只跑核心逻辑测试：

```bash
python3 -m pytest tests/test_core_logic.py
```

## 二开路线图

本项目建议优先走"稳健交付"路线：先完善环境、测试和文档，再逐步扩展能力。

### 短期：可复现与可验证
- 统一 `python3` 与虚拟环境说明
- 补齐核心逻辑测试
- 明确 FastGPT、MCP 与示例脚本的运行边界
- 提升文档一致性

### 中期：可维护与可协作
- 统一清理链路，减少重复实现
- 优化 CLI 参数与交互体验
- 增加 dry-run / 预览模式
- 增加更细粒度的日志与统计
- 增加测试数据与回归样例

### 长期：可扩展与可平台化
- 插件化抓取器 / 清理器 / 上传适配器
- 支持更多内容源
- 支持更多知识库目标与导出格式
- 引入工作流化处理链路
- 支持规则配置化与批量任务编排

## 如何贡献

欢迎贡献代码、文档、测试和使用经验。

### 推荐贡献方式
- 先提 issue 说明需求或问题
- 优先补测试，再改逻辑
- 保持文档与代码同步
- 新增清理规则时提供样例输入/输出
- 新增抓取器或上传适配时说明适用场景

### 适合贡献的方向
- 新的内容清理规则
- 新的数据源抓取器
- FastGPT 接口适配增强
- CLI 交互体验优化
- 测试覆盖率提升
- 示例与教程补充

## 致谢

感谢以下项目与资料为本项目提供了思路和参考：

- [wechat-article-downloader](https://github.com/qiye45/wechatDownload)
- [baoyu-format-markdown](https://github.com/baoyu-tech/markdown-formatter)
- [markdown-frontmatter-doctor](https://github.com/example/frontmatter-doctor)
- [FastGPT API 文档](https://doc.fastgpt.in/docs/development/api/)

## 许可证

MIT License

---

**其他语言版本**: [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [한국어](README.ko.md)
