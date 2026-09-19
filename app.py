"""Streamlit 主应用 —— AI 求职竞争力引擎。

运行：
    streamlit run app.py
"""
from __future__ import annotations

import os
from typing import Any, Dict

import streamlit as st

from src import analyzer, advisor, llm, report
from src.parser import extract_text, parse_resume

st.set_page_config(
    page_title="AI 求职竞争力引擎",
    page_icon="🎯",
    layout="wide",
)

# --------------------------------------------------------------------------- #
# 侧边栏：LLM 配置（支持模型切换）
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("⚙️ 模型配置")
    st.caption("支持任意 OpenAI 兼容接口（OpenAI / DeepSeek / 本地模型）")

    api_key = st.text_input(
        "API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="留空则使用环境变量；未配置时自动降级为规则模式。",
    )
    base_url = st.text_input(
        "Base URL",
        value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    model_name = st.text_input(
        "模型名称",
        value=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    )
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        os.environ["LLM_MODEL"] = model_name

    use_llm = st.toggle("启用 LLM 智能分析", value=True)
    if use_llm and not llm.is_configured():
        st.warning("未配置 API Key，将使用规则模式。")
    st.divider()
    st.caption("MVP：上传简历 + 粘贴 JD → 多维匹配分析 + 优化建议 + 模拟面试题")

st.title("🎯 AI 求职竞争力引擎")
st.caption("从匹配分析到面试准备的求职全流程助手")

# --------------------------------------------------------------------------- #
# 输入区
# --------------------------------------------------------------------------- #
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1️⃣ 上传简历")
    uploaded = st.file_uploader(
        "支持 PDF / Word(.docx) / 文本",
        type=["pdf", "docx", "txt", "md"],
    )

with col_right:
    st.subheader("2️⃣ 粘贴岗位描述 (JD)")
    jd_text = st.text_area(
        "岗位 JD",
        height=260,
        placeholder="把目标岗位的 JD 粘贴到这里……",
    )

run = st.button("🚀 开始分析", type="primary", use_container_width=True)

# --------------------------------------------------------------------------- #
# 分析主流程
# --------------------------------------------------------------------------- #
if run:
    if not uploaded:
        st.error("请先上传简历文件。")
        st.stop()
    if not jd_text.strip():
        st.error("请粘贴岗位 JD。")
        st.stop()

    with st.spinner("正在解析简历……"):
        raw = extract_text(uploaded.name, uploaded.getvalue())
        profile = parse_resume(raw)

    with st.spinner("正在进行多维匹配分析……"):
        analysis = analyzer.analyze(jd_text, raw, use_llm=use_llm)
        gaps = analysis.get("gaps", {})

    with st.spinner("正在生成优化建议……"):
        advice = advisor.generate_advice(jd_text, raw, gaps, use_llm=use_llm)

    with st.spinner("正在生成模拟面试题……"):
        interview = advisor.generate_interview_questions(jd_text, raw, use_llm=use_llm)

    st.session_state["result"] = {
        "profile": profile.to_dict(),
        "analysis": analysis,
        "advice": advice,
        "interview": interview,
        "jd": jd_text,
    }

# --------------------------------------------------------------------------- #
# 结果展示
# --------------------------------------------------------------------------- #
res: Dict[str, Any] = st.session_state.get("result")  # type: ignore
if res:
    profile = res["profile"]
    analysis = res["analysis"]
    advice = res["advice"]
    interview = res["interview"]

    mode = analysis.get("mode", "rule")
    if mode == "rule":
        st.info("当前为规则模式（未配置 LLM）。配置 API Key 可获得更精准的语义级分析。")

    st.divider()
    st.header("📊 匹配总览")
    overall = analyzer.overall_score(analysis)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("加权总分", f"{overall} / 100")
    with c2:
        st.metric("匹配等级", analyzer.score_level(overall))
    with c3:
        st.write("**候选人：**", profile.get("name") or "未识别")
        st.write("**邮箱：**", profile.get("email") or "-")
        st.write("**电话：**", profile.get("phone") or "-")
    st.info(analysis.get("summary", ""))

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🕸️ 分项雷达", "📋 逐项对比", "🛠️ 优化建议", "💬 模拟面试"]
    )

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            st.plotly_chart(
                report.build_radar(analysis.get("category_scores", {})),
                use_container_width=True,
            )
        with c_r:
            st.plotly_chart(
                report.build_gap_heatmap(analysis.get("dimensions", [])),
                use_container_width=True,
            )
        st.plotly_chart(
            report.build_dimension_bar(analysis.get("dimensions", [])),
            use_container_width=True,
        )

    with tab2:
        st.subheader("关键能力维度拆解")
        for d in analysis.get("dimensions", []):
            with st.container(border=True):
                a, b = st.columns([3, 1])
                with a:
                    st.markdown(f"**{d.get('name','')}** · _{d.get('category','')}_")
                    st.caption(d.get("reason", ""))
                with b:
                    st.metric("覆盖度", f"{d.get('score','')}", f"权重 {d.get('weight','')}")

        st.subheader("差距分析")
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("**缺失技能**")
            for s in gaps.get("missing_skills", []) or ["无"]:
                st.markdown(f"- {s}")
        with g2:
            st.markdown("**经验深度不足**")
            for s in gaps.get("experience_gaps", []) or ["无"]:
                st.markdown(f"- {s}")
        with g3:
            st.markdown("**量化指标缺失**")
            for s in gaps.get("quantification_gaps", []) or ["无"]:
                st.markdown(f"- {s}")

    with tab3:
        st.subheader("简历优化建议（修改前 vs 修改后）")
        for i, s in enumerate(advice.get("resume_suggestions", []), 1):
            with st.expander(f"{i}. {s.get('target','')}", expanded=i == 1):
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown("**修改前**")
                    st.code(s.get("before", ""), language=None)
                with cc2:
                    st.markdown("**修改后**")
                    st.code(s.get("after", ""), language=None)
                st.caption("💡 " + s.get("rationale", ""))

        st.subheader("技能提升路径")
        for p in advice.get("skill_paths", []):
            st.markdown(
                f"- **{p.get('skill','')}**（{p.get('duration','')}）："
                f"{p.get('how','')} ｜ 资源：{p.get('resource','')}"
            )

    with tab4:
        st.subheader("模拟面试题")
        for i, q in enumerate(interview.get("questions", []), 1):
            with st.expander(
                f"Q{i}. {q.get('question','')} （{q.get('difficulty','')}）",
                expanded=i == 1,
            ):
                st.markdown(f"- **考察点：** {q.get('focus','')}")
                st.markdown(f"- **回答思路：** {q.get('hint','')}")

    # 导出
    st.divider()
    md = report.build_markdown_report(profile, analysis, advice, interview)
    st.download_button(
        "⬇️ 导出 Markdown 报告",
        data=md,
        file_name="resume_match_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
    with st.expander("查看 Markdown 报告全文"):
        st.markdown(md)
