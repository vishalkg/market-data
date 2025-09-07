# Strategy Builder Template

## Instructions for Using This Template

**When to Create a New Strategy:**
- Major feature additions or system changes
- Performance optimization initiatives  
- Provider migrations or integrations
- Architecture refactoring projects

**How to Use This Template:**
1. Copy this template to a new file: `[FEATURE_NAME]_STRATEGY.md`
2. Fill in each section based on your specific feature/change
3. Use the Robinhood optimization strategy as a reference example
4. Keep it focused and actionable - avoid over-planning

---

# [FEATURE NAME] Strategy

## Executive Summary

**Objective**: [One sentence describing what you want to achieve]

**Current Problem**: [What limitation/issue are you solving]

**Proposed Solution**: [High-level approach to solve it]

**Expected Impact**: [Key benefits and improvements]

## Current State Analysis

### Existing Implementation
```
Current System:
├── Component A: [Current status and limitations]
├── Component B: [Current status and limitations]  
└── Component C: [Current status and limitations]
```

**Critical Gaps Identified:**
- **Gap 1**: [Specific limitation with impact]
- **Gap 2**: [Specific limitation with impact]
- **Gap 3**: [Specific limitation with impact]

### Performance/Usage Metrics (Current)
- **Metric 1**: [Current performance/capacity]
- **Metric 2**: [Current performance/capacity]
- **Metric 3**: [Current performance/capacity]

## Research & Feasibility Analysis

### Technical Requirements
**Must Have:**
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

**Nice to Have:**
- [ ] Enhancement 1
- [ ] Enhancement 2

### API/Library Capabilities Research
**[Primary Technology/API]:**
- ✅ Feature A - [Description and benefit]
- ✅ Feature B - [Description and benefit]
- ❌ Feature C - [Not available, need alternative]

**[Fallback Technology/API]:**
- ✅ Feature A - [Description and limitations]
- ✅ Feature B - [Description and limitations]

### Risk Assessment
**High Risk:**
- **Risk 1**: [Description] → Mitigation: [How to handle]

**Medium Risk:**
- **Risk 2**: [Description] → Mitigation: [How to handle]

**Low Risk:**
- **Risk 3**: [Description] → Mitigation: [How to handle]

## Implementation Strategy

### Proposed Architecture
```
New System:
├── 🥇 PRIMARY: [New primary provider/approach]
│   ├── Feature A ──── [Capability and benefit]
│   ├── Feature B ──── [Capability and benefit]
│   └── Feature C ──── [Capability and benefit]
├── 🥈 FALLBACK: [Backup provider/approach]
│   ├── Feature A ──── [Limited capability]
│   └── Feature B ──── [Limited capability]
└── 🔧 UTILITIES: [Supporting components]
    ├── Component A ─── [Purpose]
    └── Component B ─── [Purpose]
```

### Task Breakdown
- [ ] **Phase 1 - [Core Implementation]**: [Description]
- [ ] **Phase 2 - [Enhancement/Integration]**: [Description]  
- [ ] **Phase 3 - [Optimization/Polish]**: [Description]
- [ ] **Phase 4 - [Testing & Deployment]**: [Description]

**Progress**: 0/4 tasks complete (0%) - READY TO START

### Quick Status Overview

| Task | Status | Priority | Estimated Impact |
|------|--------|----------|------------------|
| Phase 1 | ⏳ Pending | High | [Impact description] |
| Phase 2 | ⏳ Pending | Medium | [Impact description] |
| Phase 3 | ⏳ Pending | Medium | [Impact description] |
| Phase 4 | ⏳ Pending | High | [Impact description] |

## Expected Outcomes

### Performance Improvements
- **Metric 1**: [Current] → [Target] ([X]% improvement)
- **Metric 2**: [Current] → [Target] ([X]% improvement)
- **Metric 3**: [Current] → [Target] ([X]% improvement)

### Feature Enhancements
- **Enhancement 1**: [Description and benefit]
- **Enhancement 2**: [Description and benefit]
- **Enhancement 3**: [Description and benefit]

### Success Metrics
**Primary KPIs:**
- [ ] Metric 1 achieves target of [X]
- [ ] Metric 2 improves by [X]%
- [ ] Feature A works reliably

**Secondary KPIs:**
- [ ] User satisfaction improves
- [ ] System reliability increases
- [ ] Maintenance overhead decreases

## Implementation Timeline

### Phase 1: [Name] (Estimated: [X] hours)
**Deliverables:**
- [ ] Component A implementation
- [ ] Component B implementation
- [ ] Basic testing

**Success Criteria:**
- [ ] Core functionality working
- [ ] Basic tests passing

### Phase 2: [Name] (Estimated: [X] hours)
**Deliverables:**
- [ ] Integration with existing system
- [ ] Enhanced features
- [ ] Comprehensive testing

**Success Criteria:**
- [ ] Full integration working
- [ ] Performance targets met

### Phase 3: [Name] (Estimated: [X] hours)
**Deliverables:**
- [ ] Optimization and polish
- [ ] Documentation updates
- [ ] Production deployment

**Success Criteria:**
- [ ] All success metrics achieved
- [ ] System stable in production

## Fallback Plan

**If Primary Approach Fails:**
1. **Immediate Action**: [What to do if things go wrong]
2. **Alternative Approach**: [Backup plan]
3. **Rollback Strategy**: [How to revert changes]

**Risk Mitigation:**
- **Data Loss Prevention**: [How to protect data]
- **Service Continuity**: [How to maintain uptime]
- **User Impact Minimization**: [How to reduce disruption]

## Strategy Update Log

### Update: [DATE] - STRATEGY CREATED
**Status**: Planning phase initiated
**Next Steps**: Begin Phase 1 implementation
**Notes**: [Any additional context or decisions made]

---

## Template Usage Notes

**Key Principles from Successful Strategies:**
1. **Start with clear problem definition** - What exactly are you solving?
2. **Research thoroughly** - Understand capabilities and limitations upfront
3. **Plan in phases** - Break large changes into manageable chunks
4. **Test incrementally** - Validate each phase before proceeding
5. **Maintain fallbacks** - Always have a backup plan
6. **Track progress** - Update the strategy as you implement

**Reference Examples:**
- See `ROBINHOOD_OPTIMIZATION_STRATEGY.md` for a successful multi-phase optimization
- Focus on concrete deliverables and measurable outcomes
- Keep the strategy document updated as you progress

**Remember**: The strategy should be a living document that guides implementation, not a static plan that gets forgotten.
