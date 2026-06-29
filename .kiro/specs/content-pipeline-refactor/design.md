# Design：内容处理管线整合与清理（content-pipeline-refactor）

## 1. 目标
采用方案A：停用旧并行管线 `processor.py`，新增**来源无关、覆盖 `.md/.txt/.html`** 的统一本地处理命令（清洗 → 富化 → 可选去重上传），并修正去重 key、收紧过激清洗规则。全程**保守可回滚**。

## 2. 微信链路安全性（已验证）
真实「下载→清洗→转化」链路依赖 `WeChatMCPDownloader`（转化在远程 MCP）+ `FormatCleaner` + `FrontmatterDoctor` + `FrontmatterEnricher` + `FastGPTSyncer`，**均不在停用名单**。停用项对该链路无功能影响，唯一风险是包 `__init__.py` 的导入耦合（见 §3）。

## 3. 停用 / 复用 决策表（两档降级）

降级方式分两档：

**A 档 → 重命名为 `.bak`（彻底移出导入，可改名回滚）**

| 文件 | 处理 |
|------|------|
| `processor.py` | → `processor.py.bak` |
| `examples.py` | → `examples.py.bak` |
| `fetchers/wechat_article.py`（`WechatArticleFetcher`，失效的实时抓取） | → `.bak` |

**B 档 → 代码注释禁用（保留文件，更轻，便于快速复核后再删）**

| 文件 | 处理 |
|------|------|
| `cleaners/markdown.py`（`MarkdownCleaner`，被 `FormatCleaner` 取代且有已知 bug） | 文件加弃用头注释；在 `__init__` 注释其导入；注释对应测试 |
| `cleaners/wechat_markdown.py`（`WeChatMarkdownCleaner`，全仓库无调用） | 同上 |

**复用（保留，作为新管线零件）**

| 文件 | 用途 |
|------|------|
| `fetchers/file.py`（`FileFetcher`） | 收集文件 + `.md/.html/.txt` 类型判断 |
| `cleaners/wechat_article.py`（`WechatArticleCleaner`，bs4） | `.html` 正文提取 |
| `cleaners/text.py`（`TextCleaner`） | `.txt` 噪音清理 |

### 导入耦合处理（硬约束 · 必须与停用同一次改动）
- `fetchers/__init__.py`：移除 `from .wechat_article import WechatArticleFetcher` 及 `__all__` 条目（因其变 `.bak` 不可导入）。
- `cleaners/__init__.py`：注释 `from .markdown import MarkdownCleaner`、`from .wechat_markdown import WeChatMarkdownCleaner` 及 `__all__` 条目。
- `tests/test_core_logic.py`：注释/跳过 `MarkdownCleaner` 相关 import 与用例；**保留** `TextCleaner`、`WechatArticleCleaner` 测试。
- 验证基线：`from cleaners import FormatCleaner, FrontmatterDoctor` 与 `python3 -m pytest` 必须通过。

## 4. 统一命令：`process-local`

选 `process-local`，语义清晰（处理本地文件），与在线来源的 `download-and-clean` 区分。`clean-wechat`、`download-and-clean` 重构为复用同一内核，行为对用户不变。

```
python3 main.py process-local \
  --input <dir|file> \
  --output ./cleaned \
  --extensions .md,.txt,.html \
  [--no-enrich] \            # 富化默认开启，加此 flag 关闭
  [--dataset-id <id>] \      # 给定才上传
  [--dry-run]
```

数据流：
```
FileFetcher.scan_directory → [{content, type, identifier, filename}]
  type=html     → WechatArticleCleaner ┐
  type=markdown → FormatCleaner(收紧)  ├→ FrontmatterDoctor → (默认)FrontmatterEnricher → 写出
  type=text     → TextCleaner          ┘
                                         → (可选) FastGPTSyncer.upload_file（去重+改名告警）
```

新增 `cleaners/pipeline.py` 的 `ContentCleaningPipeline`：输入 `(content, type, metadata)`，按类型选清洗器并接 `FrontmatterDoctor`，输出 `(cleaned_text, frontmatter)`。`clean-wechat`/`download-and-clean` 改为调用它，消除重复清洗循环；`clean-wechat` 顺带支持 `--extensions`。

## 5. 去重策略（改用 original_url / 内容 hash）

新增 `compute_dedup_key(frontmatter, cleaned_body, file_path)`：
- 优先 `original_url`（来自 frontmatter）；
- 缺失则用清洗后正文的内容 hash；
- 再缺失回退文件字节 hash。

`FastGPTSyncer.upload_file` 去重改为按此 key，**检查与写入用同一 key/hash 口径**（避免重蹈 `processor.py` 覆辙）。状态文件维持 `data/fastgpt_sync_state.json`。

## 6. 更新行为（不覆盖，改名 + warn）
- key 命中且内容 hash 相同 → `skipped`（未变化）。
- key 命中但内容 hash 变化（即"更新"）→ **不覆盖旧 collection**；以新名上传（`{stem}-{短hash}` 或 `{stem}-vN`），并 `logger.warning` 记录"检测到内容更新，已另存为新 collection: <新名>"。更新去重记录。
- key 未命中 → 正常新建。

## 7. 富化（默认开启）
`process-local` 与 `download-and-clean` 统一：富化默认 ON，`--no-enrich` 关闭。富化失败降级为空、不阻断（`FrontmatterEnricher` 已实现）。

## 8. 收紧清洗规则
`FormatCleaner` 的 `\{[^}]*\}`：
- 围栏代码块 ` ``` ... ``` ` 内整体跳过所有 CSS/噪音清洗；
- 花括号仅在"疑似 CSS"上下文删除（含 `:` 且无中文/非代码），保留含中文、JSON、LaTeX 的 `{...}`。
- 新增回归测试：含代码/JSON/LaTeX 的 `.md/.txt` 不被误删。

## 9. 错误处理与可观测
- 单文件清洗/富化/上传失败不阻断批次，per-file 记录、末尾汇总。
- 富化失败降级为空。
- `rich` 统一输出进度与汇总表：文件 / 类型 / 清洗 / 富化 / 上传结果。

## 10. 测试策略
- 注释 `MarkdownCleaner` 测试；保留扩展 `TextCleaner`、`WechatArticleCleaner`、`FormatCleaner`（含"不误删代码/JSON"）、`FrontmatterDoctor`。
- 新增 `ContentCleaningPipeline` 路由测试（`.md/.txt/.html` 各走对应清洗器）。
- 新增去重测试：同 `original_url` 不同路径→跳过；内容变化→改名上传 + warn。
- `python3 -m pytest` 全绿为完成基线。
