# CLAUDE.md

## Teaching Plan Step Structure

When implementing teaching plan steps, ALWAYS follow this structure:

### Required Directory Structure for Each Step
```
invoice-parser-stepXXX/
├── starting-code/      # What the student begins with (copy from previous step's ending-code)
├── ending-code/        # What the student should have at the end
└── teacher-notes.md    # Teaching guidance and common issues
```

### Critical Rules for Step Implementation
1. **Step Progression**: The `ending-code` of step N MUST become the `starting-code` of step N+1
2. **First Step**: Step 001's `starting-code` directory should be empty (starting from scratch)
3. **Continuity**: Each step must build upon the previous step's work - no gaps allowed
4. **Documentation**: Teacher notes are mandatory and must include common issues and solutions

### Required Components in Each Step
- Clear learning objectives in teacher-notes.md
- **CRITICAL: Step-by-step instructions to run and test the ending-code**
  - Exact commands to set up environment
  - Exact commands to install dependencies
  - Exact commands to run the application
  - Manual testing instructions for EVERY feature
  - Expected output for each test
  - Troubleshooting guide for common issues
- Common student mistakes and their fixes
- Explicit connection to previous and next steps
- Assessment checkpoints for verifying student understanding
- Time estimates and pacing guidelines

## Engineering Plan Usage

When implementing features using an engineering plan document:

1. **Location**: Engineering plan documents are typically provided by the user and located in `.project-management/` directory
2. **Continuous Reference**: Until the product/feature is fully built, ALWAYS refer back to the engineering plan document
3. **Active Updates**: Update the plan after EVERY task completion - it's a living document
4. **Complete Context**: The engineering plan + codebase must contain ALL information a new developer needs
5. **Triple Purpose**: The plan serves as:
   - Project plan (what to build)
   - Progress tracker (what's done)
   - Progress memory (how it was done)

## Critical Rules

- **Never skip reading** the engineering plan at session start
- **Never skip updating** task status and notes after completion
- **Never leave gaps** in context - document all decisions and discoveries
- The engineering plan is the single source of truth for project state

## Update Frequency

- After completing each task: Update status and add implementation notes
- When discovering new requirements: Add to plan immediately
- When making architectural decisions: Document reasoning
- When encountering blockers: Document issue and resolution

## Testing Best Practices

When testing full-stack applications:

1. **Environment Setup First**:
   - Verify all environment variables are correct BEFORE testing
   - Test database connections independently (create test scripts like test-db-1.py)
   - Ensure API keys are valid and not expired
   - Create necessary directories (static, uploads) before starting servers

2. **Test Order Matters**:
   - Backend first: Ensure API is running and healthy
   - Database second: Verify connections and table creation
   - Frontend last: Test UI only after backend is confirmed working

3. **Use TodoWrite for Test Planning**:
   - Create comprehensive test task lists
   - Update status in real-time as tests complete
   - Document failures immediately for debugging

4. **Common Issues to Check**:
   - Database connection strings (especially for cloud databases like Neon)
   - API key expiration (Google, OpenAI, etc.)
   - Missing directories or permissions
   - CORS configuration for frontend-backend communication
   - Port conflicts

5. **Documentation Requirements**:
   - Always create a TEST_REPORT.md after testing
   - Include both successes and failures
   - Document all fixes applied
   - Provide clear reproduction steps for any remaining issues

## Real-World Application Testing Checklist

- [ ] Database connectivity verified
- [ ] API endpoints responding
- [ ] Authentication flow working
- [ ] File uploads processing correctly
- [ ] AI/ML integrations functional
- [ ] Frontend rendering properly
- [ ] Responsive design tested
- [ ] Error handling graceful
- [ ] Performance metrics acceptable
- [ ] Security considerations noted
- [ ] No mocks. No dummies. No pathy-fixes. Only fully working code.
 
Remember: A new developer should be able to continue work using ONLY the codebase and engineering plan.