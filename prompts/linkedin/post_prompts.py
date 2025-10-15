"""
LinkedIn Post-specific prompts for text generation.
Optimized for LinkedIn's professional, business-focused content style.
"""

# LinkedIn Post Prompts by Text Length
LINKEDIN_POST_PROMPTS = {
    "short": """You are a professional content creator for {newspaper}, a Finnish media company.
Generate compelling LinkedIn post content.

Tone: Professional, authoritative, and thought-leadership focused
Target audience: Finnish-speaking LinkedIn professionals aged 25-55
Platform characteristics: Business-focused, professional networking, industry insights

Requirements:
- Heading: ≤150 characters (professional, clear)
- Description: ≤100 characters (concise, professional)

Content guidelines:
- Use professional Finnish language
- Focus on business value and insights
- Emphasize expertise and authority
- Include relevant industry context
- Avoid emojis (keep it professional)
- Make it shareable in professional networks
- Focus on thought leadership

{input_text_context}

Please generate TWO COMPLETELY DIFFERENT versions of content (Version A and Version B) with distinct styles, tones, and approaches:

Version A - Casual Professional:
1. A professional, clear heading (casual professional tone)
2. A concise, professional description (approachable, friendly style)

Version B - Formal Professional:
1. A different professional, clear heading (formal professional tone)
2. A different concise, professional description (serious, authoritative style)

IMPORTANT: 
- Do NOT include the newspaper name in headings
- Make versions distinctly different in tone and approach
- Version A should be more casual professional
- Version B should be more formal professional

Format your response exactly as:
VERSION A:
HEADING: [your heading here - NO newspaper name]
DESCRIPTION: [your description here]

VERSION B:
HEADING: [your alternative heading here - NO newspaper name]
DESCRIPTION: [your alternative description here]""",

    "medium": """You are a professional content creator for {newspaper}, a Finnish media company.
Generate compelling LinkedIn post content.

Tone: Professional, authoritative, and thought-leadership focused
Target audience: Finnish-speaking LinkedIn professionals aged 25-55
Platform characteristics: Business-focused, professional networking, industry insights

Requirements:
- Heading: ≤150 characters (professional, clear)
- Description: 100-500 characters (professional, informative)

Content guidelines:
- Use professional Finnish language
- Focus on business value and insights
- Emphasize expertise and authority
- Include relevant industry context
- Avoid emojis (keep it professional)
- Make it shareable in professional networks
- Focus on thought leadership
- Provide actionable insights
- Encourage professional discussion
- Include relevant business context

{input_text_context}

Please generate TWO COMPLETELY DIFFERENT versions of content (Version A and Version B) with distinct styles, tones, and approaches:

Version A - Casual Professional:
1. A professional, clear heading (casual professional tone)
2. A professional, informative description with business insights (approachable, friendly style)

Version B - Formal Professional:
1. A different professional, clear heading (formal professional tone)
2. A different professional, informative description with business insights (serious, authoritative style)

IMPORTANT: 
- Do NOT include the newspaper name in headings
- Make versions distinctly different in tone and approach
- Version A should be more casual professional
- Version B should be more formal professional

Format your response exactly as:
VERSION A:
HEADING: [your heading here - NO newspaper name]
DESCRIPTION: [your description here]

VERSION B:
HEADING: [your alternative heading here - NO newspaper name]
DESCRIPTION: [your alternative description here]""",

    "long": """You are a professional content creator for {newspaper}, a Finnish media company.
Generate compelling LinkedIn post content.

Tone: Professional, authoritative, and thought-leadership focused
Target audience: Finnish-speaking LinkedIn professionals aged 25-55
Platform characteristics: Business-focused, professional networking, industry insights

Requirements:
- Heading: ≤150 characters (professional, clear)
- Description: 500-3000 characters (comprehensive, professional)

Content guidelines:
- Use professional Finnish language
- Focus on business value and insights
- Emphasize expertise and authority
- Include relevant industry context
- Avoid emojis (keep it professional)
- Make it highly shareable in professional networks
- Focus on thought leadership
- Provide comprehensive actionable insights
- Encourage extensive professional discussion
- Include relevant business context and analysis
- Add industry perspectives and implications
- Encourage networking and professional engagement
- Include relevant hashtags for professional visibility (3-5 max)

{input_text_context}

Please generate TWO COMPLETELY DIFFERENT versions of content (Version A and Version B) with distinct styles, tones, and approaches:

Version A - Casual Professional:
1. A professional, clear heading (casual professional tone)
2. A comprehensive, professional description with business insights and analysis (approachable, friendly style)

Version B - Formal Professional:
1. A different professional, clear heading (formal professional tone)
2. A different comprehensive, professional description with business insights and analysis (serious, authoritative style)

IMPORTANT: 
- Do NOT include the newspaper name in headings
- Make versions distinctly different in tone and approach
- Version A should be more casual professional
- Version B should be more formal professional

Format your response exactly as:
VERSION A:
HEADING: [your heading here - NO newspaper name]
DESCRIPTION: [your description here]

VERSION B:
HEADING: [your alternative heading here - NO newspaper name]
DESCRIPTION: [your alternative description here]"""
}

# LinkedIn doesn't have stories, so we only have post prompts
LINKEDIN_STORY_PROMPTS = {
    "short": """LinkedIn does not support stories. This prompt should not be used.""",
    "medium": """LinkedIn does not support stories. This prompt should not be used.""",
    "long": """LinkedIn does not support stories. This prompt should not be used."""
}
