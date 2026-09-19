"""建议生成器（Advisor）：简历优化 / 技能路径 / 模拟面试题。

每条简历建议都要求给出「修改前 vs 修改后」对照，方便用户直接套用。
无 LLM 时提供模板化的兜底建议。
"""
from __future__ import annotations

from typing import Any, Dict, List

from . import llm, prompts


def _rule_based_advice(gaps: Dict[str, Any]) -> Dict[str, Any]:
    """无 LLM 的兜底建议：基于差距给出通用模板。"""
    missing = gaps.get("missing_skills", []) or []
    suggestions: List[Dict[str, str]] = [
        {
            "target": "经历描述缺少量化",
            "before": "负责数据平台开发，提升了系统性能。",
            "after": (
                "[Situation] 数据平台查询延迟高，影响分析效率；"
                "[Task] 目标将 P95 延迟降低 50%；"
                "[Action] 引入缓存与索引优化，重构慢查询；"
                "[Result] P95 延迟从 2.4s 降至 0.9s，日均节省人工等待约 40 小时。"
            ),
            "rationale": "用 STAR 结构 + 具体数字，让成果可衡量、可信。",
        },
        {
            "target": "缺少与 JD 对齐的关键词",
            "before": "(现有技能栏)",
            "after": (
                "补充 JD 明确要求、且你确有经验的技能："
                + ("、".join(missing[:5]) if missing else "按 JD 关键词补齐")
                + "，并注明熟练程度。"
            ),
            "rationale": "提升关键词命中率，兼顾 ATS 系统与人工筛选。",
        },
        {
            "target": "项目描述过于笼统",
            "before": "参与了一个机器学习项目。",
            "after": (
                "[S] 用户流失率上升；[T] 搭建流失预测模型；"
                "[A] 特征工程 + LightGBM，AUC 0.82；"
                "[R] 存量用户召回率提升 12%，季度增收约 XX 万元。"
            ),
            "rationale": "突出个人贡献、方法与业务价值。",
        },
        {
            "target": "格式与可读性",
            "before": "大段文字堆叠。",
            "after": "每段 3-5 行内，要点前置，动词开头（主导/搭建/优化）。",
            "rationale": "HR 平均 7 秒浏览一份简历，结构化更易被抓住重点。",
        },
        {
            "target": "岗位针对性",
            "before": "一份简历投所有岗位。",
            "after": "针对本 JD 调整「个人简介」与「技能排序」，突出最相关的 3 段经历。",
            "rationale": "让最匹配的信息第一时间被看到。",
        },
    ]
    skill_paths = [
        {
            "skill": s,
            "how": "官方文档 + 小项目实战",
            "resource": "官方文档 / 极客时间 / Coursera",
            "duration": "2-4 周",
        }
        for s in (missing[:3] or ["补充一个 JD 高频技能"])
    ]
    return {"resume_suggestions": suggestions, "skill_paths": skill_paths, "mode": "rule"}


def generate_advice(jd: str, resume_text: str, gaps: Dict[str, Any],
                    use_llm: bool = True) -> Dict[str, Any]:
    """生成简历优化建议与技能提升路径。"""
    if use_llm and llm.is_configured():
        try:
            result = llm.chat_json(
                [
                    {"role": "system", "content": prompts.ADVICE_SYSTEM},
                    {
                        "role": "user",
                        "content": prompts.ADVICE_USER_TEMPLATE.format(
                            jd=jd,
                            resume=resume_text[:10000],
                            gaps=gaps,
                        ),
                    },
                ]
            )
            result.setdefault("mode", "llm")
            return result
        except Exception as e:
            fb = _rule_based_advice(gaps)
            fb["llm_error"] = str(e)
            return fb
    return _rule_based_advice(gaps)


def _rule_based_interview(jd: str) -> Dict[str, Any]:
    base = [
        ("请用 STAR 法则介绍你与这个岗位最相关的一段经历。", "经历匹配与表达", "S 背景→T 目标→A 行动→R 结果，结果要量化。", "简单"),
        ("你如何理解这个岗位的核心职责？你认为自己最大的优势是什么？", "岗位理解与自我认知", "先拆解 JD 职责，再逐一对应自身证据。", "中等"),
        ("讲一个你主导并克服困难的项目的案例。", "问题解决与抗压", "突出你的决策与复盘。", "中等"),
        ("你在简历中提到的【某技能】是如何落地的？遇到的最大坑是什么？", "技能深度", "给具体场景、技术选型与踩坑经验。", "困难"),
        ("你未来 1-3 年的职业规划是什么？", "稳定性与成长性", "与团队/岗位方向对齐。", "简单"),
    ]
    return {
        "questions": [
            {"question": q, "focus": f, "hint": h, "difficulty": d} for q, f, h, d in base
        ],
        "mode": "rule",
    }


def generate_interview_questions(jd: str, resume_text: str,
                                 use_llm: bool = True) -> Dict[str, Any]:
    """生成模拟面试题（默认 5 道）。"""
    if use_llm and llm.is_configured():
        try:
            result = llm.chat_json(
                [
                    {"role": "system", "content": prompts.INTERVIEW_SYSTEM},
                    {
                        "role": "user",
                        "content": prompts.INTERVIEW_USER_TEMPLATE.format(
                            jd=jd, resume=resume_text[:10000]
                        ),
                    },
                ]
            )
            result.setdefault("mode", "llm")
            return result
        except Exception as e:
            fb = _rule_based_interview(jd)
            fb["llm_error"] = str(e)
            return fb
    return _rule_based_interview(jd)
