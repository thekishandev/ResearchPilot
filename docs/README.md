# 📚 ResearchPilot Documentation

Welcome to the ResearchPilot documentation hub. This directory contains all technical documentation, development guides, and archived project notes.

## 📖 Core Documentation

Essential reading for understanding and using ResearchPilot:

- **[Main README](../README.md)** - Project overview, features, and quick start
- **[Getting Started Guide](../GETTING_STARTED.md)** - Detailed setup instructions
- **[API Documentation](../API.md)** - API endpoints and usage
- **[MCP Gateway Implementation](../MCP_GATEWAY_IMPLEMENTATION.md)** - Custom gateway architecture

## 🚀 Current Status & Planning

Active development documentation:

- **[Next Steps](../NEXT_STEPS.md)** - Actionable roadmap with implementation plans
- **[Feature Summary](../FEATURE_SUMMARY.md)** - Complete feature inventory (37 implemented!)
- **[Implementation Complete](../IMPLEMENTATION_COMPLETE.md)** - Latest session achievements
- **[Cerebras Enhancement Plan](../ENHANCEMENT_PLAN_CEREBRAS.md)** - Advanced AI capabilities roadmap

## 🛠️ Development Resources

Files for developers and troubleshooting:

### `/development` - Active Development Files
- **[Voice Input Debugging](development/VOICE_INPUT_DEBUGGING.md)** - Troubleshooting Web Speech API
- **[Voice Input Quick Test](development/VOICE_INPUT_QUICK_TEST.md)** - Quick test guide
- **[test-voice-input.html](development/test-voice-input.html)** - Standalone voice input test page

### `/archive` - Historical Documentation
Older documentation kept for reference:
- BUGFIX_FOLLOW_UPS.md
- CONVERSATION_HISTORY_UI.md
- ENHANCEMENTS_SUMMARY.md
- ENHANCEMENT_PLAN.md
- IMPLEMENTATION_STATUS.md
- LATEST_ENHANCEMENTS.md
- PROJECT_COMPLETION_STATUS.md
- PROJECT_STRUCTURE.md
- PROJECT_SUMMARY.md
- ROUTE_ORDERING_FIX.md
- TESTING_VOICE_INPUT.md
- VOICE_INPUT_COMPLETE.md
- VOICE_INPUT_FEATURE.md
- VOICE_INPUT_INTEGRATION.md

---

## 📋 Quick Reference

### Documentation Categories

| Category | Files | Purpose |
|----------|-------|---------|
| **User Guides** | README.md, GETTING_STARTED.md | How to use ResearchPilot |
| **API Reference** | API.md | Backend API endpoints |
| **Architecture** | MCP_GATEWAY_IMPLEMENTATION.md | System design |
| **Planning** | NEXT_STEPS.md, FEATURE_SUMMARY.md | Development roadmap |
| **Development** | development/*.md | Debugging & testing |
| **Archive** | archive/*.md | Historical records |

### Key Features Documented

✅ **Implemented & Documented:**
- Multi-source research orchestration (6 sources)
- Cerebras AI with structured outputs
- Automatic reasoning (query complexity detection)
- Voice input (Web Speech API)
- Multi-turn conversations
- Real-time streaming
- Custom MCP Gateway

⏳ **Planned (see NEXT_STEPS.md):**
- Tool use orchestration
- Research templates
- Export formats (PDF, Markdown, JSON)
- Knowledge graph visualization
- Custom source management

---

## 🔗 External Resources

- **Cerebras Inference API**: https://inference-docs.cerebras.ai/
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **Docker Documentation**: https://docs.docker.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/

---

## 📝 Contributing to Documentation

When adding new documentation:

1. **User-facing guides** → Root directory (e.g., GETTING_STARTED.md)
2. **Development/debugging** → `docs/development/`
3. **Outdated but useful** → `docs/archive/`
4. **Update this index** → Add link to appropriate section above

Keep documentation:
- ✅ Clear and concise
- ✅ With code examples
- ✅ Up-to-date with code changes
- ✅ Cross-linked for easy navigation

---

**Last Updated:** October 5, 2025
