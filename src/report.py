"""展示/导出工具：Markdown 报告生成 + 图表构建。"""
from __future__ import annotations

from typing import Any, Dict, List

import plotly.graph_objects as go


def build_radar(category_scores: Dict[str, int]) -> go.Figure:
    """构建四维匹配度雷达图。"""
    cats = ["技能", "经验", "教育", "软实力"]
    vals = [int(category_scores.get(c, 0)) for c in cats]
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill="toself",
                name="匹配度",
                line_color="#4C78A8",
            )
        ]
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=380,
    )
    return fig


def build_dimension_bar(dimensions: List[Dict[str, Any]]) -> go.Figure:
    """构建各能力维度的覆盖度条形图。"""
    names = [d.get("name", "") for d in dimensions]
    scores = [int(d.get("score", 0)) for d in dimensions]
    fig = go.Figure(
        data=[go.Bar(x=scores, y=names, orientation="h", marker_color="#72B7B2")]
    )
    fig.update_layout(
        xaxis=dict(range=[0, 100], title="覆盖度"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=20, b=40),
        height=max(300, 40 * len(names) + 100),
    )
    return fig


def build_gap_heatmap(dimensions: List[Dict[str, Any]]) -> go.Figure:
    """构建「维度 × 类别」覆盖度热力图，直观看出短板。"""
    cats = ["技能", "经验", "教育", "软实力"]
    names = [d.get("name", "") for d in dimensions] or ["(无维度)"]
    z: List[List[int]] = []
    for name in names:
        row = []
        for c in cats:
            match = next(
                (d for d in dimensions if d.get("name") == name and d.get("category") == c),
                None,
            )
            row.append(int(match.get("score", 0)) if match else 0)
        z.append(row)
    fig = go.Figure(data=go.Heatmap(z=z, x=cats, y=names, colorscale="RdYlGn",
                                    zmin=0, zmax=100))
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=40),
                      height=max(300, 32 * len(names) + 120))
    return fig


def build_markdown_report(
    profile: Dict[str, Any],
    analysis: Dict[str, Any],
    advice: Dict[str, Any],
    interview: Dict[str, Any],
) -> str:
    """把全流程结果导出为 Markdown 报告。"""
    cs = analysis.get("category_scores", {})
    overall = analysis.get("overall_score", 0)
    lines: List[str] = []
    lines.append("# AI 求职竞争力分析报告\n")
    lines.append(f"**候选人：** {profile.get('name') or '未识别'}  ")
    lines.append(f"**联系方式：** {profile.get('email') or '-'} / {profile.get('phone') or '-'}\n")

    lines.append("## 一、匹配总览\n")
    lines.append(f"- **加权总分：{overall} / 100**")
    for c in ["技能", "经验", "教育", "软实力"]:
        lines.append(f"- {c}匹配：{cs.get(c, 0)} / 100")
    lines.append(f"\n> {analysis.get('summary', '')}\n")

    lines.append("## 二、关键能力维度拆解\n")
    lines.append("| 维度 | 类别 | 权重 | 覆盖度 | 判定理由 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for d in analysis.get("dimensions", []):
        lines.append(
            f"| {d.get('name','')} | {d.get('category','')} | {d.get('weight','')} "
            f"| {d.get('score','')} | {d.get('reason','')} |"
        )
    lines.append("")

    gaps = analysis.get("gaps", {})
    lines.append("## 三、差距分析\n")
    lines.append("**缺失技能：** " + ("、".join(gaps.get("missing_skills", [])) or "无"))
    lines.append("\n**经验深度不足：**")
    for g in gaps.get("experience_gaps", []) or ["无"]:
        lines.append(f"- {g}")
    lines.append("\n**量化指标缺失：**")
    for g in gaps.get("quantification_gaps", []) or ["无"]:
        lines.append(f"- {g}")
    lines.append("")

    lines.append("## 四、简历优化建议（修改前 vs 修改后）\n")
    for i, s in enumerate(advice.get("resume_suggestions", []), 1):
        lines.append(f"### {i}. {s.get('target','')}")
        lines.append(f"- **修改前：** {s.get('before','')}")
        lines.append(f"- **修改后：** {s.get('after','')}")
        lines.append(f"- **理由：** {s.get('rationale','')}\n")

    lines.append("## 五、技能提升路径\n")
    for p in advice.get("skill_paths", []):
        lines.append(
            f"- **{p.get('skill','')}**（{p.get('duration','')}）："
            f"{p.get('how','')}｜资源：{p.get('resource','')}"
        )
    lines.append("")

    lines.append("## 六、模拟面试题\n")
    for i, q in enumerate(interview.get("questions", []), 1):
        lines.append(f"**Q{i}. {q.get('question','')}**  _（难度：{q.get('difficulty','')}）_")
        lines.append(f"- 考察点：{q.get('focus','')}")
        lines.append(f"- 思路：{q.get('hint','')}\n")

    return "\n".join(lines)
