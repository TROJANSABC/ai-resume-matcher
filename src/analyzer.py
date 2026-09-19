"""分析引擎（Analyzer）：多维匹配度计算 + 差距分析。

核心思路：把 JD 拆解为「关键能力维度」，逐维评估简历覆盖度，
再聚合为技能/经验/教育/软实力四个分项雷达，最后加权得到总分。
支持两种模式：
- LLM 模式：调用大模型做语义级拆解与评分（推荐）。
- 规则模式：无 API Key 时的兜底，基于关键词覆盖做粗略估算。
"""
from __future__ import annotations

from typing import Any, Dict, List

from . import llm, prompts
from .parser import SKILL_VOCAB

CATEGORIES = ["技能", "经验", "教育", "软实力"]


def _rule_based_analysis(jd: str, resume_text: str) -> Dict[str, Any]:
    """无 LLM 的兜底分析：关键词覆盖度。"""
    jd_low = (jd or "").lower()
    resume_low = (resume_text or "").lower()
    # 从技能词典中找出 JD 出现过的技能
    jd_skills = [s for s in SKILL_VOCAB if s.lower() in jd_low]
    if not jd_skills:
        jd_skills = ["Python", "SQL", "沟通", "项目管理"]
    covered = [s for s in jd_skills if s.lower() in resume_low]
    missing = [s for s in jd_skills if s.lower() not in resume_low]
    cover_rate = len(covered) / max(len(jd_skills), 1)

    dimensions = []
    weight = round(1.0 / len(jd_skills), 2)
    for s in jd_skills:
        hit = s.lower() in resume_low
        dimensions.append(
            {
                "name": s,
                "category": "技能",
                "weight": weight,
                "score": 85 if hit else 30,
                "reason": "简历中已体现该技能。" if hit else "简历未提及该技能。",
            }
        )

    skill_score = int(cover_rate * 100)
    overall = int(skill_score * 0.6 + 60 * 0.4)
    return {
        "dimensions": dimensions,
        "category_scores": {
            "技能": skill_score,
            "经验": 60,
            "教育": 60,
            "软实力": 60,
        },
        "overall_score": overall,
        "gaps": {
            "missing_skills": missing,
            "experience_gaps": ["规则模式无法评估经验深度，建议配置 LLM。"],
            "quantification_gaps": ["请检查经历描述是否包含量化结果（如提升 X%）。"],
        },
        "summary": (
            f"[规则模式] JD 命中技能 {len(covered)}/{len(jd_skills)}，"
            f"技能覆盖度约 {skill_score}%。配置 LLM API Key 可获得更精准的多维分析。"
        ),
        "mode": "rule",
    }


def analyze(jd: str, resume_text: str, use_llm: bool = True) -> Dict[str, Any]:
    """执行匹配分析。

    Args:
        jd: 岗位描述。
        resume_text: 简历纯文本。
        use_llm: 是否优先使用 LLM；未配置或失败时回退规则模式。
    """
    if use_llm and llm.is_configured():
        try:
            result = llm.chat_json(
                [
                    {"role": "system", "content": prompts.MATCH_SYSTEM},
                    {
                        "role": "user",
                        "content": prompts.MATCH_USER_TEMPLATE.format(
                            jd=jd, resume=resume_text[:12000]
                        ),
                    },
                ]
            )
            result.setdefault("mode", "llm")
            # 规范化 category_scores 缺省键
            cs = result.get("category_scores", {}) or {}
            result["category_scores"] = {c: cs.get(c, 0) for c in CATEGORIES}
            return result
        except Exception as e:  # LLM 失败则回退
            fallback = _rule_based_analysis(jd, resume_text)
            fallback["llm_error"] = str(e)
            return fallback
    return _rule_based_analysis(jd, resume_text)


def overall_score(result: Dict[str, Any]) -> int:
    """从分析结果中取总分（缺失时用分项均值）。"""
    if isinstance(result.get("overall_score"), (int, float)):
        return int(round(result["overall_score"]))
    cs = result.get("category_scores", {})
    vals = [v for v in cs.values() if isinstance(v, (int, float))]
    return int(round(sum(vals) / len(vals))) if vals else 0


def score_level(score: int) -> str:
    """把分数映射为可读的匹配等级。"""
    if score >= 85:
        return "高度匹配"
    if score >= 70:
        return "较为匹配"
    if score >= 55:
        return "部分匹配"
    return "匹配度较低"
