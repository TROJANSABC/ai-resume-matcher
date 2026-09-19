"""冒烟测试：验证解析/分析/建议/报告在无 LLM（规则模式）下可跑通。

运行：
    python smoke_test.py
"""
from __future__ import annotations

import os
import pathlib

# 强制规则模式，避免测试依赖网络
os.environ.pop("OPENAI_API_KEY", None)

from src import analyzer, advisor, report  # noqa: E402
from src.parser import parse_resume  # noqa: E402

ROOT = pathlib.Path(__file__).parent


def main() -> None:
    resume_text = (ROOT / "sample" / "sample_resume.txt").read_text("utf-8")
    jd_text = (ROOT / "sample" / "sample_jd.txt").read_text("utf-8")

    profile = parse_resume(resume_text)
    assert profile.email == "zhangwei@example.com", profile.email
    assert profile.name == "张伟", profile.name
    print(f"[OK] 解析：姓名={profile.name} 邮箱={profile.email} 技能数={len(profile.skills)}")

    analysis = analyzer.analyze(jd_text, resume_text, use_llm=False)
    score = analyzer.overall_score(analysis)
    assert 0 <= score <= 100
    assert set(analysis["category_scores"]) == {"技能", "经验", "教育", "软实力"}
    print(f"[OK] 分析：总分={score} 等级={analyzer.score_level(score)} 模式={analysis['mode']}")

    advice = advisor.generate_advice(jd_text, resume_text, analysis["gaps"], use_llm=False)
    assert len(advice["resume_suggestions"]) >= 1
    print(f"[OK] 建议：{len(advice['resume_suggestions'])} 条优化 + {len(advice['skill_paths'])} 条技能路径")

    interview = advisor.generate_interview_questions(jd_text, resume_text, use_llm=False)
    assert len(interview["questions"]) == 5
    print(f"[OK] 面试题：{len(interview['questions'])} 道")

    md = report.build_markdown_report(profile.to_dict(), analysis, advice, interview)
    assert "# AI 求职竞争力分析报告" in md and len(md) > 500
    print(f"[OK] 报告：Markdown {len(md)} 字符")

    # 图表可构建
    assert report.build_radar(analysis["category_scores"]) is not None
    assert report.build_gap_heatmap(analysis["dimensions"]) is not None
    assert report.build_dimension_bar(analysis["dimensions"]) is not None
    print("[OK] 图表：雷达图 / 热力图 / 条形图 构建成功")

    print("\n✅ 全部冒烟测试通过（规则模式，无需 API Key）")


if __name__ == "__main__":
    main()
