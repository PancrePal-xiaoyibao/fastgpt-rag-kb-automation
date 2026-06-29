# Tasks：content-pipeline-refactor

> 状态：全部完成 ✅（最终验证 104 passed，process-local 已注册）

- [x] 1. 停用旧并行管线 + 修复导入耦合（原子任务）
  - 将 `processor.py`、`examples.py`、`fetchers/wechat_article.py` 重命名为 `.bak`
  - 更新 `fetchers/__init__.py`：移除 `from .wechat_article import WechatArticleFetcher` 及 `__all__` 中对应条目
  - 验证基线：`python3 -c "from cleaners import FormatCleaner, FrontmatterDoctor; from fetchers import WeChatMCPDownloader"` 通过；`python3 -m pytest` 通过
  - 对应设计：§3（A 档 + 导入耦合硬约束）、§2

- [x] 2. 注释禁用 `MarkdownCleaner` 与 `WeChatMarkdownCleaner`
  - 在 `cleaners/markdown.py`、`cleaners/wechat_markdown.py` 顶部加弃用头注释（标注"待删除，已被 FormatCleaner 取代/无引用"）
  - 在 `cleaners/__init__.py` 注释这两个 import 及 `__all__` 条目
  - 在 `tests/test_core_logic.py` 注释/`@pytest.mark.skip` 掉 `MarkdownCleaner` 的 import 与用例；保留 `TextCleaner`、`WechatArticleCleaner` 测试
  - 验证：`from cleaners import FormatCleaner` 正常、`python3 -m pytest` 通过
  - 对应设计：§3（B 档）

- [x] 3. 收紧 `FormatCleaner` 的 `{...}` CSS 规则
  - 围栏代码块 ` ``` ... ``` ` 内整体跳过 CSS/噪音清洗
  - `\{[^}]*\}` 改为仅"疑似 CSS"上下文删除（含 `:` 且无中文/非代码），保留含中文、JSON、LaTeX 的花括号
  - 新增回归测试：含代码块 / JSON / LaTeX 的 `.md`、`.txt` 不被误删；微信 CSS 残留仍被清掉
  - 对应设计：§8

- [x] 4. 新建 `ContentCleaningPipeline`（`cleaners/pipeline.py`）
  - 接口：`clean(content, content_type, metadata) -> (cleaned_text, frontmatter)`
  - 路由：`html→WechatArticleCleaner`、`markdown→FormatCleaner`、`text→TextCleaner`，统一接 `FrontmatterDoctor`
  - 单元测试：三种类型各走对应清洗器、输出含标准化 frontmatter
  - 对应设计：§4

- [x] 5. 去重 key 重构 + 更新改名告警
  - 新增 `compute_dedup_key(frontmatter, cleaned_body, file_path)`：优先 `original_url` → 内容 hash → 文件字节 hash
  - 改造 `FastGPTSyncer.upload_file`：按新 key 去重，检查与写入同一口径；状态文件仍为 `data/fastgpt_sync_state.json`
  - 更新行为：key 命中且 hash 相同→`skipped`；命中但 hash 变化→以新名 `{stem}-{短hash}` 上传 + `logger.warning`；未命中→正常新建
  - 测试：同 `original_url` 不同路径→跳过；内容变化→改名上传并产生 warn；全新→新建
  - 对应设计：§5、§6

- [x] 6. 新增 `process-local` 命令
  - `parse_args` 加子命令：`--input/--output/--extensions(默认 .md,.txt,.html)/--no-enrich(默认富化开)/--dataset-id/--dry-run`
  - `cmd_process_local`：`FileFetcher` 收集+类型 → `ContentCleaningPipeline` → 默认 `FrontmatterEnricher` 富化 → 写出 → 可选 `upload_file`
  - 失败不阻断批次，per-file 记录；`rich` 汇总表（文件/类型/清洗/富化/上传）；`--dry-run` 只列文件与路由
  - 注册到 `commands` 映射与交互式菜单
  - 测试：`--dry-run` 列举正确；端到端（mock LLM/上传）跑通混合扩展名目录
  - 对应设计：§4、§7、§9

- [x] 7. 重构 `clean-wechat` 与 `download-and-clean` 复用内核
  - 两者改为调用 `ContentCleaningPipeline`，移除各自重复的两阶段清洗循环
  - `clean-wechat` 扩展支持 `--extensions`（默认 `.md`，保持向后兼容）
  - 富化默认开启与 `process-local` 统一
  - 验证：现有微信下载→清洗→上传链路行为不回归（mock 跑通）
  - 对应设计：§4、§7

- [x] 8. 文档与最终验证
  - 更新 `README.md` 项目结构与命令说明（新增 `process-local`，标注停用项），与代码同步
  - 全量 `python3 -m pytest` 通过；手动 `--dry-run` 冒烟
  - 对应设计：§10

## 执行顺序建议
任务 1、2 是低风险可回滚停用，先做并验证基线；3–5 是内核能力；6–7 是命令整合；8 收尾。
