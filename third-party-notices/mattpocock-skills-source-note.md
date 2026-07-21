# Matt Pocock skills 方法来源说明

## 来源

- 项目：mattpocock/skills
- 来源目录：skills/productivity/grilling、skills/productivity/grill-me、skills/engineering/grill-with-docs、skills/engineering/domain-modeling、skills/engineering/research、skills/productivity/handoff、skills/productivity/writing-great-skills
- 上游基准：main 分支提交 697d4ce，2026-07-13
- 上游提交：https://github.com/mattpocock/skills/commit/697d4ce9742da558fd1ba6697c8e9775e2e302dd
- 许可：MIT License，全文见 mattpocock-skills-LICENSE.txt

## 本仓库中的使用方式

jq-pm-grilling 吸收并重新组织了以下公开方法：

- 每轮只问一个问题，持续沿决策树解决依赖关系。
- 为每个问题提供推荐答案和取舍。
- 能从项目材料查明的事实主动读取，把真正的决定交给用户确认。
- 在共享理解形成前不进入实施。
- 带文档模式即时维护领域术语和长期决定记录。
- 多业务域项目通过 CONTEXT-MAP.md 定位对应术语和决定载体。
- 大型调研可按独立来源或对象并行收集资料，由主 Agent 完成证据复核和综合。
- 跨会话交接引用已有成果、完成敏感信息处理并建议下一 Skill。
- Skill 维护强调单一事实源、触发边界、渐进披露和正向目标表达。

本仓库进一步增加了产品经理工作流需要的能力：

- 发现拷问与评审拷问两种上下文。
- 事实、决定、假设、未知项和规范术语组成的决策账本。
- PRODUCT-BRIEF、工作决定、工作假设和下一阶段交接。
- AI、确定性规则、计算引擎和人工决策的职责拆分。
- 与调研、PRD、原型、评审和汇报 Skill 的阶段流转协议。

原始项目名称和方法来源仅用于许可与溯源说明。jq-pm-grilling 的中文流程、文件协议和产品阶段协作规则由本仓库重新设计。

## Codex 调用策略

上游 grill-me 通过 agents/openai.yaml 设置 allow_implicit_invocation: false，只在用户显式输入 $grill-me 时调用。

jq-pm-copilot 中的 jq-pm-grilling 设置 allow_implicit_invocation: true，用于自动承接产品拷问任务，并供 jq-pm-discovery 和 jq-pm-review 复用。两者的调用策略按各自职责保留。
