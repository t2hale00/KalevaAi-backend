# Prompts Directory

This directory contains platform-specific prompts for text generation. Each platform has its own subdirectory with optimized prompts for different content types and text lengths.

## Directory Structure

```
prompts/
├── instagram/
│   └── post_prompts.py
├── facebook/
│   └── post_prompts.py
├── linkedin/
│   └── post_prompts.py
└── README.md
```

## Platform-Specific Prompts

### Instagram (`instagram/post_prompts.py`)
- **Focus**: Visual-first, engaging, emoji-friendly content
- **Tone**: Friendly, engaging, and visually appealing
- **Audience**: Finnish-speaking Instagram users aged 18-45
- **Features**: 
  - Emoji usage guidelines
  - Visual storytelling focus
  - Hashtag-friendly content
  - Call-to-action emphasis

### Facebook (`facebook/post_prompts.py`)
- **Focus**: Community-driven, discussion-oriented content
- **Tone**: Conversational, community-focused, and engaging
- **Audience**: Finnish-speaking Facebook users aged 25-65
- **Features**:
  - Community discussion encouragement
  - Local relevance focus
  - Minimal emoji usage
  - Professional yet approachable tone

### LinkedIn (`linkedin/post_prompts.py`)
- **Focus**: Professional, business-focused content
- **Tone**: Professional, authoritative, and thought-leadership focused
- **Audience**: Finnish-speaking LinkedIn professionals aged 25-55
- **Features**:
  - Business value emphasis
  - Industry insights
  - No emoji usage
  - Thought leadership focus

## Text Length Options

Each platform supports three text length options:

### Short (≤100 characters)
- Concise, attention-grabbing content
- Minimal context
- Strong call-to-action

### Medium (100-500/1000 characters)
- Balanced content with context
- Moderate engagement elements
- Informative yet engaging

### Long (500+ characters)
- Comprehensive content
- Full context and analysis
- Multiple engagement prompts
- Detailed storytelling

## Content Types

### Posts
- Full text generation with heading and description
- Platform-specific optimization
- Engagement-focused content

### Stories
- Heading-only generation (visual-first)
- Immediate, casual tone
- Ephemeral content focus

## Usage

Prompts are loaded and managed by the `PromptManager` service in `services/prompt_manager.py`. The service automatically:

1. Loads all prompt modules from platform directories
2. Provides a clean interface for prompt retrieval
3. Handles formatting with input text and newspaper branding
4. Manages fallbacks for unsupported combinations

## Adding New Platforms

To add a new platform:

1. Create a new directory: `prompts/[platform_name]/`
2. Create `post_prompts.py` with the required prompt dictionaries:
   - `[PLATFORM]_POST_PROMPTS` (uppercase)
   - `[PLATFORM]_STORY_PROMPTS` (uppercase)
3. Each dictionary should have keys: `"short"`, `"medium"`, `"long"`
4. The `PromptManager` will automatically detect and load the new platform

## Prompt Template Variables

All prompts support these template variables:
- `{newspaper}`: The newspaper brand name
- `{input_text_context}`: Formatted input text context

## Best Practices

1. **Platform-Specific Tone**: Each platform has unique characteristics that should be reflected in the prompts
2. **Character Limits**: Always specify clear character limits for headings and descriptions
3. **Engagement**: Include specific guidance for encouraging platform-appropriate engagement
4. **Finnish Language**: All prompts are optimized for Finnish-speaking audiences
5. **Brand Consistency**: Maintain consistent branding across all platforms while adapting to platform norms


