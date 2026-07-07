# 销售数字分身（Sales Digital Twin）

基于 **Python 3.12 + DeepSeek + LangChain** 的 B2B 销售自动化 Agent。输入模拟销售通话/会议文本，自动完成信息提取、结构化跟进记录、CRM 更新建议与商业合同变更建议。

## 功能概览

| 能力 | 说明 |
|------|------|
| 信息提取 | 客户名称、沟通摘要、需求痛点、下一步行动（负责人 / 任务 / 截止时间） |
| 结构化输出 | 固定四行文本格式，可直接复制到 CRM |
| CRM 更新建议 | 推断需变更的 CRM 字段（如客户状态、商机金额） |
| 非销售兜底 | 识别非销售对话，输出「非销售场景，跳过处理」 |
| 合同变更建议 | 识别价格、条款、交付周期等合同相关变更需求 |
| 交互式演示 | 菜单选择示例或自定义输入；每轮完成后直接回主菜单，适合答辩验收 |

---

## 环境要求

| 项目 | 要求 |
|------|------|
| Python | **3.12 及以上**（推荐 3.12） |
| 操作系统 | Windows / macOS / Linux |
| API Key | [DeepSeek](https://platform.deepseek.com/) API Key（销售场景必需） |
| 网络 | 可访问 DeepSeek API |

> **说明**：示例 3（非销售闲聊）可通过规则引擎短路处理，**无需 API Key** 即可运行；示例 1、2 及完整演示需要配置有效的 `DEEPSEEK_API_KEY`。

---

## 安装

### 1. 获取代码

```bash
git clone <your-repo-url>
cd poject_custom
```

若使用压缩包，解压后进入项目根目录即可。

### 2. 创建虚拟环境（推荐）

**Windows（PowerShell / CMD）：**

```bash
python -m venv venv
```

**激活虚拟环境：**

| 终端 | 命令 |
|------|------|
| **CMD**（推荐，无策略限制） | `venv\Scripts\activate.bat` |
| **PowerShell** | `venv\Scripts\Activate.ps1` |
| **不激活，直接调用** | 见下方说明 |

PowerShell 若报错「禁止运行脚本」，任选一种方式：

```powershell
# 方式 1：改用 CMD 激活（最简单）
cmd /c "venv\Scripts\activate.bat && pip install -e .[dev]"

# 方式 2：放宽当前用户脚本策略（一次性）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 方式 3：不激活 venv，直接用完整路径（无需改策略）
venv\Scripts\python.exe -m pip install -e ".[dev]"
venv\Scripts\python.exe -m sales_digital_twin
```

**macOS / Linux：**

```bash
python3.12 -m venv venv
source venv/bin/activate
```

激活成功后，命令行前会出现 `(venv)` 前缀。

### 3. 安装依赖

**方式 A：可编辑安装（推荐，含 CLI 命令 `sales-twin`）**

```bash
pip install -e ".[dev]"
```

**方式 B：仅安装运行依赖**

```bash
pip install -r requirements.txt
```

**方式 C：仅安装运行依赖（不含 pytest 等开发工具）**

```bash
pip install -e .
```

### 4. 验证安装

```bash
python -m sales_digital_twin --help
```

或使用已注册的 CLI 命令：

```bash
sales-twin --help
```

---

## 配置

### 1. 创建环境变量文件

在项目根目录执行：

**Windows：**

```bash
copy .env.example .env
```

**macOS / Linux：**

```bash
cp .env.example .env
```

### 2. 编辑 `.env`

```env
# DeepSeek API（OpenAI 兼容）
DEEPSEEK_API_KEY=sk-你的密钥
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# LLM 参数（可选，有默认值）
LLM_TEMPERATURE=0.1
LLM_MAX_RETRIES=2
LLM_TIMEOUT_SECONDS=60

# 日志级别（可选）
LOG_LEVEL=INFO
```

### 3. 配置项说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | 销售场景必填 | DeepSeek 平台申请的 API Key |
| `DEEPSEEK_API_BASE` | 否 | API 地址，默认 `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | 否 | 模型名称，默认 `deepseek-chat` |
| `LLM_TEMPERATURE` | 否 | 生成温度，默认 `0.1` |
| `LLM_MAX_RETRIES` | 否 | LLM 调用失败重试次数，默认 `2` |
| `LLM_TIMEOUT_SECONDS` | 否 | 单次请求超时（秒），默认 `60` |
| `LOG_LEVEL` | 否 | 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` |

> `.env` 已加入 `.gitignore`，请勿将 API Key 提交到 Git。

---

## 运行

所有命令均需在**项目根目录**、**已激活虚拟环境**下执行。

### 推荐：交互式演示系统（答辩 / 验收）

不带任何参数启动，进入交互式菜单：

```bash
python -m sales_digital_twin
```

等效命令：

```bash
sales-twin
```

启动后会看到如下菜单：

```text
============================================================
  销售数字分身 —— 交互式演示系统
============================================================
  1. 运行全部系统默认示例
  2. 选择单个系统默认示例
  3. 自定义输入通话文本
  0. 退出
------------------------------------------------------------
```

| 选项 | 说明 |
|------|------|
| **1** | 依次运行全部 3 组系统默认示例 |
| **2** | 子菜单选择单个示例（示例 1 / 2 / 3） |
| **3** | 手动粘贴或输入自定义通话文本（空行结束） |
| **0** | 退出程序 |

每轮处理完成后**直接回到主菜单**继续演示；仅选 **0** 退出（子菜单选 0 返回主菜单）。

系统默认示例对应 `examples/` 目录：

1. **示例 1** — 正常销售通话（`sample1_sales.txt`）
2. **示例 2** — 价格谈判（`sample2_negotiation.txt`）
3. **示例 3** — 非销售场景（`sample3_chitchat.txt`）

> 示例 1、2 及选项 3 中的销售文本需要配置有效的 `DEEPSEEK_API_KEY`；示例 3 无需 API Key。

### 命令行参数（脚本 / 自动化）

不带参数时默认进入交互式演示；也可通过参数直接运行，跳过菜单：

| 参数 | 简写 | 说明 |
|------|------|------|
| `--demo` | — | 批量运行 `examples/` 下三组标准示例 |
| `--file <路径>` | `-f` | 从文本文件读取通话内容 |
| `--text <内容>` | `-t` | 直接传入通话文本 |
| `--interactive` | `-i` | 多行输入模式（空行结束） |
| `--output <路径>` | `-o` | 指定结果输出文件 |

> `--demo`、`--file`、`--text`、`--interactive` 四选一；与无参数启动互斥。

**批量演示（命令行）：**

```bash
python -m sales_digital_twin --demo
sales-twin --demo
```

### 单条运行

**从文件读取：**

```bash
python -m sales_digital_twin --file examples/sample1_sales.txt
python -m sales_digital_twin --file examples/sample2_negotiation.txt
python -m sales_digital_twin --file examples/sample3_chitchat.txt
```

**直接传入文本：**

```bash
python -m sales_digital_twin --text "今天下午与深圳智创科技李经理进行了价格谈判..."
```

**交互式输入：**

```bash
python -m sales_digital_twin --interactive
```

按提示粘贴通话文本，输入单独一行空行后结束。

**指定输出文件：**

```bash
python -m sales_digital_twin --file examples/sample1_sales.txt --output outputs/my_result.txt
```

未指定 `--output` 时，结果会打印到控制台，并自动保存到 `outputs/result_YYYYMMDD_HHMMSS.txt`（stderr 会提示保存路径）。

### 无需 API Key 的快速验证

仅验证非销售兜底逻辑：

```bash
python -m sales_digital_twin --file examples/sample3_chitchat.txt
```

预期输出：

```text
非销售场景，跳过处理
```

### 预期输出格式（销售场景）

```text
客户名称：上海华讯科技（王总）
沟通摘要：介绍 SalesMind 平台，针对客户 CRM 老旧、数据分散的痛点，获得初步兴趣。
客户需求：CRM 系统老旧、数据分散；需要一体化销售管理、自动跟进记录、商机预测
下一步行动：负责人张三，任务发送详细方案报价并安排在线演示，截止2026-07-14 14:00

【CRM 更新建议】
- 客户状态：跟进中 → 方案报价中
- ...

【商业合同变更建议】
暂无合同变更需求，待方案确认后再议。
```

更多输入输出示例见 [docs/需求文档.md](docs/需求文档.md#73-标准示例摘要)。

---

## 测试

项目使用 **pytest** 组织测试，分为单元测试与集成测试。

### 运行全部单元测试（无需 API Key）

```bash
pytest tests/unit -v
```

覆盖内容：

| 测试文件 | 说明 |
|----------|------|
| `test_rule_engine.py` | 销售 / 非销售规则预筛、强关键词 |
| `test_formatter.py` | 四行结构化输出格式 |
| `test_pipeline_fallback.py` | 非销售场景 Pipeline 短路、空输入 |
| `test_pipeline_success.py` | 销售链路 Mock、合同 Agent 条件跳过 |
| `test_json_parser.py` | LLM JSON 文本解析 |
| `test_llm_retry.py` | LLM 网络层重试装饰器 |
| `test_cli_parser.py` | CLI 参数解析、演示样本加载 |

### 运行集成测试（需要 API Key）

集成测试会真实调用 DeepSeek API，需在 `.env` 或环境变量中配置有效的 `DEEPSEEK_API_KEY`：

```bash
pytest tests/integration -v
```

或在命令行临时注入（PowerShell 示例）：

```powershell
$env:DEEPSEEK_API_KEY="sk-你的密钥"
pytest tests/integration -v
```

集成测试会验证 `examples/` 下三组标准样本的端到端输出。

### 运行所有测试

```bash
pytest tests -v
```

未配置 API Key 时，集成测试会自动跳过（显示 `SKIPPED`），单元测试仍正常执行。

### 查看测试覆盖率（可选）

```bash
pytest tests/unit --cov=sales_digital_twin --cov-report=term-missing
```

---

## 项目结构

```
poject_custom/
├── src/sales_digital_twin/     # 主程序
│   ├── cli/                    # 命令行入口（交互式菜单 + 参数模式）
│   ├── core/                   # Pipeline 编排、工厂、常量、异常
│   ├── agents/                 # 分类 / 提取 / CRM / 合同 Agent
│   ├── services/               # 规则引擎、格式化
│   ├── models/                 # Pydantic 数据模型
│   └── infrastructure/         # 配置、LLM、Prompt、重试、trace_id
├── examples/                   # 三组演示输入样本
├── tests/                      # 单元测试 + 集成测试
├── outputs/                    # 运行结果（自动生成）
├── docs/                       # 需求、架构、设计文档
├── .env.example                # 环境变量模板
├── pyproject.toml              # 项目配置与依赖
└── requirements.txt            # pip 依赖清单
```

---

## 调用链路

```
CLI 输入（交互式菜单 / 命令行参数）
  → SalesDigitalTwinPipeline.process()
  → RuleEngine 规则预筛（强关键词 + 普通关键词）
      ├─ [高置信 non_sales] →「非销售场景，跳过处理」（零 LLM）
      └─ [边界样本]         → ClassifierAgent LLM 复核
  → [sales] ExtractorAgent（JSON 模式 + Pydantic 校验）
  → FormatterService（四行格式化）
  → CRM / 合同建议
      ├─ 无合同关键词 → 仅 CRM，合同用默认文案
      └─ 有关键词     → CRM 与合同并行 LLM 调用
  → PipelineResult.render() → 控制台 / outputs/
```

每次请求生成 `trace_id`，Pipeline 与 Agent 日志可关联排查。

---

## 实现要点（v1.0）

| 主题 | 说明 |
|------|------|
| 降本提速 | 规则高置信短路；无合同关键词时跳过 ContractAdvisor |
| 延迟优化 | CRM 与合同建议并行 LLM 调用 |
| 输出稳定 | DeepSeek `json_object` 模式 + Pydantic 校验 |
| 重试分层 | 网络异常（tenacity）与 Schema 解析失败（BaseAgent）分开处理 |
| CLI 体验 | 会话内复用 Pipeline；交互式一轮后直接回主菜单 |

---

## 常见问题

**Q：PowerShell 激活 venv 报「禁止运行脚本」**

- 改用 CMD：`venv\Scripts\activate.bat`
- 或执行：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- 或不激活，直接用：`venv\Scripts\python.exe -m sales_digital_twin`

**Q：启动后没有菜单，直接报错**

- 若使用了 `--text`、`--file`、`--demo` 等参数，会跳过菜单直接执行
- 进入交互式演示需不带任何参数运行：`sales-twin` 或 `python -m sales_digital_twin`

**Q：`未配置有效的 DEEPSEEK_API_KEY`**

- 确认已在项目根目录创建 `.env` 并填入真实 Key
- 销售场景（示例 1、2）必须配置 Key；示例 3 可不配置

**Q：`ModuleNotFoundError: No module named 'sales_digital_twin'`**

- 确认已激活虚拟环境
- 执行 `pip install -e ".[dev]"` 安装项目

**Q：集成测试被 SKIP**

- 检查 `DEEPSEEK_API_KEY` 是否已设置且不是 `.env.example` 中的占位值

**Q：DeepSeek API 调用超时**

- 增大 `.env` 中 `LLM_TIMEOUT_SECONDS`（如 `120`）
- 检查网络是否能访问 `api.deepseek.com`

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/需求文档.md](docs/需求文档.md) | 产品需求、验收标准、演示示例 |
| [docs/技术方案.md](docs/技术方案.md) | 架构设计、模块职责、实现与测试 |

---

## 技术栈

- Python 3.12
- LangChain + langchain-openai
- DeepSeek API（OpenAI 兼容接口）
- Pydantic v2 + pydantic-settings
- pytest（测试）
