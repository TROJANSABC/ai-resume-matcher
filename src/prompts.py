"""提示词模板（Prompts）。

所有面向 LLM 的指令集中管理，便于迭代与多语言扩展。
"""

MATCH_SYSTEM = (
    "你是一位资深招聘专家与职业发展顾问，擅长把岗位 JD 拆解为能力维度，"
    "并客观评估候选人简历的匹配程度。你的评估必须具体、可追溯、避免空话。"
    "严格按要求输出 JSON。"
)

MATCH_USER_TEMPLATE = """请对比以下【岗位描述 JD】与【候选人简历】，完成多维匹配分析。

=== 岗位描述 JD ===
{jd}

=== 候选人简历 ===
{resume}

要求：
1. 从 JD 中提取 5-8 个「关键能力维度」（技能/经验/教育/软实力）。
2. 为每个维度给出：维度名称、类别（技能/经验/教育/软实力）、权重(0-1，合计约 1)、
   候选人覆盖度评分(0-100)、判定理由（结合简历原文，一句话）。
3. 给出四个分项总分（0-100）：技能匹配、经验匹配、教育匹配、软实力匹配。
4. 给出差距分析：缺失技能列表、经验深度不足点、量化指标缺失点。
5. 计算加权总分 overall_score（0-100）。

只输出如下 JSON：
{{
  "dimensions": [
    {{"name": "...", "category": "技能|经验|教育|软实力", "weight": 0.2,
      "score": 80, "reason": "..."}}
  ],
  "category_scores": {{"技能": 80, "经验": 70, "教育": 90, "软实力": 65}},
  "overall_score": 76,
  "gaps": {{
     "missing_skills": ["..."],
     "experience_gaps": ["..."],
     "quantification_gaps": ["..."]
  }},
  "summary": "整体匹配度的一段总结"
}}"""


ADVICE_SYSTEM = (
    "你是一位简历优化与求职辅导专家，擅长用 STAR 法则改写经历，"
    "并提供可执行的提升建议。严格按要求输出 JSON。"
)

ADVICE_USER_TEMPLATE = """基于以下岗位 JD 与候选人简历，给出可执行的优化建议。

=== 岗位描述 JD ===
{jd}

=== 候选人简历 ===
{resume}

=== 匹配差距 ===
{gaps}

要求：
1. resume_suggestions：5 条简历优化建议。每条包含：
   - target：针对的简历片段或问题
   - before：修改前的原文（若原文缺失可给出「(现有描述)」占位）
   - after：用 STAR 法则改写后的示例（含量化结果）
   - rationale：为什么这样改
2. skill_paths：3 条技能提升路径，每条含 skill / how（学习方式）/ resource（推荐资源）/
   duration（预计周期）。
3. 输出 JSON：
{{
  "resume_suggestions": [
    {{"target": "...", "before": "...", "after": "...", "rationale": "..."}}
  ],
  "skill_paths": [
    {{"skill": "...", "how": "...", "resource": "...", "duration": "..."}}
  ]
}}"""


INTERVIEW_SYSTEM = (
    "你是一位经验丰富的面试官，擅长围绕岗位重点要求与候选人薄弱点设计面试题，"
    "并给出考察点与参考回答思路。严格按要求输出 JSON。"
)

INTERVIEW_USER_TEMPLATE = """基于以下岗位 JD 与候选人简历，生成 5 道模拟面试题。

=== 岗位描述 JD ===
{jd}

=== 候选人简历 ===
{resume}

要求：覆盖 JD 重点要求，并针对简历薄弱点追问。每题包含：
- question：题目
- focus：考察点
- hint：回答思路（含 STAR 结构建议）
- difficulty：难度（简单/中等/困难）

只输出 JSON：
{{"questions": [{{"question": "...", "focus": "...", "hint": "...", "difficulty": "中等"}}]}}"""
