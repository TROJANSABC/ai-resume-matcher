# 🎯 AI 求职竞争力引擎 (AI Resume Matcher)

> 不只是分析匹配度，而是求职者的全流程助手 —— 从 **匹配分析 → 差距诊断 → 简历优化 → 面试准备** 一站式完成。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ 核心价值

传统工具只给一个「相似度百分比」。本项目把匹配度**拆解为技能 / 经验 / 教育 / 软实力四个维度**，
给出雷达图与逐项对比，并把每条建议**可执行化**（附「修改前 vs 修改后」示例），
再生成**模拟面试题**，形成完整求职闭环。

## 🧩 架构

```
resume-matcher/
├── app.py                 # Streamlit 展示层（匹配总览 / 逐项对比 / 建议 / 面试）
├── src/
│   ├── parser.py          # 解析层：PDF/Word 解析 + 结构化提取
│   ├── analyzer.py        # 分析引擎：多维匹配度计算 + 差距分析
│   ├── advisor.py         # 建议生成器：简历优化 / 技能路径 / 模拟面试题
│   ├── llm.py             # LLM 封装：预留模型切换接口
│   ├── prompts.py         # 提示词模板
│   └── report.py          # 可视化图表 + Markdown 报告导出
├── sample/                # 示例简历与 JD
├── smoke_test.py          # 冒烟测试（规则模式，无需 API Key）
├── requirements.txt
└── .env.example
```

| 层级 | 技术选型 | 说明 |
| --- | --- | --- |
| 前端 | Streamlit | 快速出 Demo，后期可迁移 FastAPI + React |
| 后端 | Python（Streamlit 自包含） | 可选 FastAPI 拆分 |
| LLM | OpenAI 兼容接口 | 支持 OpenAI / DeepSeek / 本地模型切换 |
| 解析 | PyMuPDF + python-docx | 覆盖 PDF 与 Word |
| 可视化 | Plotly | 雷达图 / 热力图 / 对比条形图 |
| 部署 | Streamlit Cloud / HuggingFace Spaces | 免费托管，方便分享 |

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置模型（可选；不配置则自动降级为规则模式）
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY 等

# 3. 运行
streamlit run app.py
```

打开浏览器访问 `http://localhost:8501`，上传简历 + 粘贴 JD，点击「开始分析」即可。

### 无 API Key 也能跑

未配置 `OPENAI_API_KEY` 时，工具自动使用**规则模式**（关键词覆盖度分析），
保证离线可用、便于演示。配置后即切换为 LLM 语义级分析。

```bash
python smoke_test.py   # 验证解析/分析/建议/报告全链路
```

## 🔌 模型切换

只需改 `.env` 三个变量，即可在任意 OpenAI 兼容后端间切换：

```env
# OpenAI
OPENAI_API_KEY=sk-xxxx
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# DeepSeek（性价比）
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 本地 Ollama
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b
```

## 📦 功能优先级

**MVP（当前已实现）**
- [x] PDF/Word 简历上传 + JD 粘贴 → 结构化提取
- [x] AI 多维匹配度分析（技能 / 经验 / 教育 / 软实力 + 差距分析）
- [x] 简历优化建议（修改前 vs 修改后）+ 模拟面试题（各 5 条）

**V2 规划**
- [ ] 简历版本对比视图
- [ ] 竞争力画像热力图增强
- [ ] PDF 报告导出
- [ ] 批量岗位对比

## ⚠️ 说明

- 本工具输出为辅助参考，不构成录用承诺；请结合实际情况判断。
- 上传的简历仅在本机处理，模型调用直接发往你配置的接口，请自行注意数据隐私。

## 📄 License

[MIT](LICENSE)
