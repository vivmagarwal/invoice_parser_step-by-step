# CLAUDE.md

## Context Management Protocol

### When to Clear Context
**MANDATORY**: Clear context with `/clear` after completing each of these:
- Teaching plan step completion
- Major feature implementation
- Engineering plan task completion
- Test suite execution
- Large file analysis tasks

### Context Clearing Workflow
```
Task Complete → Update Docs → Commit → `/clear` → Load Next Task
```

### What Stays in CLAUDE.md (Persistent Context)
This file persists across all sessions and should contain:
- Critical architectural decisions
- Project-specific conventions
- Common issue resolutions
- Testing protocols
- Update frequency rules
- Backend-first development approach
- File change tracking requirements
- Context management protocol

### Living Documents Structure
These documents must be continuously updated:
1. **TEACHING-PLAN.md**: Current step progress, all 10 steps defined upfront
2. **FILES_CHANGED.yaml**: Complete history of all file modifications
3. **Engineering Plan**: Task status, implementation notes, discoveries
4. **TEST_REPORT.md**: Test results, issues, and resolutions

### Context Loading Priority
After `/clear`, load in this order:
1. CLAUDE.md (always)
2. Current plan document (TEACHING-PLAN.md or engineering plan)
3. FILES_CHANGED.yaml (if exists)
4. Current step/task specific files only

## Teaching Plan Step Structure

When implementing teaching plan steps, ALWAYS follow this structure:

### Required Directory Structure for Each Step
```
invoice-parser-stepXXX/
├── starting-code/      # What the student begins with (copy from previous step's ending-code)
├── ending-code/        # What the student should have at the end
└── teacher-notes.md    # Teaching guidance and common issues
```

### Backend-First Development (CRITICAL for Fullstack)
For fullstack projects, ALWAYS:
1. Complete entire backend API (steps 1-5) FIRST
2. Test all endpoints as external world would (curl/httpie)
3. Verify database operations independently
4. Ensure authentication/authorization working
5. Only then move to frontend (steps 6-10)

### Critical Rules for Step Implementation
1. **All Steps Upfront**: TEACHING-PLAN.md must define ALL 10 steps from the beginning
2. **Step Progression**: The `ending-code` of step N MUST become the `starting-code` of step N+1
3. **First Step**: Step 001's `starting-code` directory should be empty (starting from scratch)
4. **Continuity**: Each step must build upon the previous step's work - no gaps allowed
5. **Documentation**: Teacher notes are mandatory and must include common issues and solutions
6. **File Tracking**: Document EVERY file change in FILES_CHANGED.yaml

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

## File Change Documentation Protocol

After EVERY file modification, update FILES_CHANGED.yaml:
```yaml
# FILES_CHANGED.yaml
step_XXX:
  created:
    - path/to/file: "Description of what this file does"
  modified:
    - path/to/file: "What was changed and why"
  deleted:
    - path/to/file: "Why this was removed"
```

## API Testing Commands Reference

### Backend Steps (1-5) - Test with curl/httpie
```bash
# Step 1: Health Check
curl http://localhost:8000/health

# Step 3: CRUD Operations
curl -X POST http://localhost:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item"}'

# Step 4: Authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secure123"}'
```

### Frontend Steps (6-10) - Test with Playwright MCP
```javascript
await browser_navigate({ url: "http://localhost:3000" });
await browser_snapshot();
await browser_wait_for({ text: "Expected Text" });
```

## Command Quick Reference

### Context Management
- `/clear` - Complete context reset (use after each task/step)
- `/compact` - Reduce history while keeping key context

### Git Workflow for Steps
```bash
git add .
git commit -m "STEP-XXX: Description"
git push origin step-XXX
```

## Critical Reminders

1. **ALWAYS** show all 10 steps upfront in TEACHING-PLAN.md
2. **ALWAYS** complete backend before frontend
3. **ALWAYS** document file changes immediately
4. **ALWAYS** clear context after major tasks
5. **NEVER** skip testing at appropriate layer
6. **NEVER** leave documentation gaps
7. **NEVER** create unnecessary files

Remember: A new developer should be able to continue work using ONLY the codebase and plan documents.