---
name: create-teaching-plan
description: Transform project into 10-step teaching journey for beginners
argument-hint: [project-path or leave blank for current project]
---

<task>Generate complete progressive teaching plan for project</task>

<objective>
Transform complex codebase into step-by-step learning experience that:
- Rebuilds project through 10 incremental, testable steps
- Teaches absolute beginners with no framework knowledge
- Tracks progress via YAML status (living document)
- Provides complete context (codebase + plan = everything needed)
- Works after EVERY step (no broken states)
</objective>

<agent-architecture>
This command leverages specialized agents:
- **code-researcher**: Deep codebase analysis and pattern extraction
- **web-researcher**: Framework documentation and best practices
These agents operate with independent context windows for optimal performance.
</agent-architecture>

<workflow>
  <phase_1_discovery>
    COMPLETE CODEBASE ANALYSIS:
    Task(
      subagent_type="code-researcher",
      description="Comprehensive codebase analysis",
      prompt="Analyze entire codebase: file structure, dependencies, architecture patterns, data flows, API endpoints, component relationships. Extract ALL features and functionality. Miss nothing."
    )

    Document in .claude-project-management/TEACHING-CONTEXT.yaml
  </phase_1_discovery>

  <phase_2_research>
    TECHNICAL RESEARCH:
    Task(
      subagent_type="web-researcher",
      description="Research frameworks and patterns",
      prompt="Research official documentation for all identified technologies. Find current best practices, common patterns, and beginner-friendly explanations. Focus on official sources from last 12 months."
    )
  </phase_2_research>

  <phase_3_verification>
    CODE EXECUTION AND LIVE TESTING:
    - Set up development environment
    - Run application end-to-end
    - Use Playwright MCP to test all features:
      • browser_navigate to localhost
      • browser_snapshot for current state
      • browser_click for interactions
      • browser_wait_for to verify elements
    - Document setup quirks
  </phase_3_verification>

  <phase_4_plan_generation>
    Generate: .claude-project-management/TEACHING-PLAN.md
  </phase_4_plan_generation>

  <phase_5_testing>
    PLAYWRIGHT MCP TESTING FRAMEWORK:
    - Create test suite for each step
    - Execute tests using Playwright MCP server
    - Capture screenshots for documentation
    - Verify functionality in real browser
  </phase_5_testing>

  <phase_6_documentation>
    Generate complete PROJECT-README.md
  </phase_6_documentation>
</workflow>

<teaching-plan-structure>

# Project Teaching Plan

## Usage Instructions
1. Read this plan at every session start
2. Update YAML status after EACH step completion
3. Document all discoveries inline
4. This document + codebase = complete learning resource

## Target Audience
- Absolute beginners with basic programming knowledge
- No framework-specific experience required
- Learning by building, not just reading

## Teaching Philosophy
- One concept per step
- Working application after every step
- Test everything before proceeding
- Document the "why" not just "how"

## Progress Tracking

```yaml
teaching_progress:
  current_step: 1
  total_steps: 10
  last_updated: ""

steps:
  - step_id: "STEP-001"
    title: "Project Setup & First Output"
    description: "Create project structure and display 'Hello World'"

    pre_implementation:
      previous_step_complete: true
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Understand project structure"
        achieved: false
      - objective: "Set up development environment"
        achieved: false
      - objective: "Run first application"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Critical discoveries and context for next session]

    learner_feedback: |
      [Common issues encountered and solutions]
```

## Step Definitions

### Step 1: Project Setup & First Output
**Starting Code**: Empty directory
**Ending Code**: Basic project with "Hello World" output

<lesson>
#### Why This Step Matters
Every application starts with a foundation. We're building the minimal structure needed to see something work.

#### What You'll Build
1. Project directory structure
2. Package.json with basic configuration
3. Entry point file
4. First visible output

#### Implementation Guide
[Detailed step-by-step instructions with explanations]

#### Understanding the Code
[Concept explanations]

#### Common Issues & Solutions
[Troubleshooting guide]

#### Testing This Step

**Automated Test Execution with Playwright MCP:**
```javascript
// Executed via Playwright MCP server
// Step 1: Navigate to application
await browser_navigate({ url: "http://localhost:3000" });

// Step 2: Take initial snapshot
await browser_snapshot();

// Step 3: Verify "Hello World" appears
await browser_wait_for({ text: "Hello World" });

// Step 4: Take screenshot for documentation
await browser_take_screenshot({
  filename: "step-001-complete.png",
  fullPage: true
});

// Step 5: Verify console output
const output = await Bash({ command: "npm start" });
expect(output).toContain("Hello World");
```

**Manual Verification:**
```bash
npm start
# Should see "Hello World" in terminal
```
</lesson>

### Steps 2-10
[Similar structure for each step]

## Architecture Decisions Log

```yaml
decisions:
  - decision_id: "DEC-001"
    step: 3
    choice: "Use functional components over class components"
    reasoning: "Simpler mental model for beginners, industry standard"
    impact: "All components will use hooks pattern"
    alternatives_considered: ["Class components", "Mixed approach"]
```

## Playwright MCP Testing Workflow

### After Each Step Implementation

```javascript
// LIVE TESTING WITH PLAYWRIGHT MCP SERVER

// 1. Start the application
await Bash({ command: "npm start", run_in_background: true });

// 2. Wait for server to be ready
await Bash({ command: "sleep 3" });

// 3. Open browser and navigate
await browser_navigate({ url: "http://localhost:3000" });

// 4. Take accessibility snapshot
const snapshot = await browser_snapshot();
console.log("Current page state:", snapshot);

// 5. Test new functionality
// Example for Step 3 (React components):
await browser_wait_for({ text: "Welcome" });
await browser_click({
  element: "Navigation menu button",
  ref: "button[aria-label='menu']"
});

// 6. Verify previous features still work
await browser_navigate({ url: "http://localhost:3000/about" });
await browser_wait_for({ text: "About Us" });

// 7. Test interactions
await browser_fill_form({
  fields: [
    {
      name: "Username field",
      ref: "input[name='username']",
      type: "textbox",
      value: "testuser"
    }
  ]
});

// 8. Capture screenshots for documentation
await browser_take_screenshot({
  filename: `step-${stepNumber}-complete.png`,
  fullPage: true
});

// 9. Test responsive design
await browser_resize({ width: 375, height: 667 }); // Mobile
await browser_take_screenshot({ filename: `step-${stepNumber}-mobile.png` });

await browser_resize({ width: 1920, height: 1080 }); // Desktop
await browser_take_screenshot({ filename: `step-${stepNumber}-desktop.png` });

// 10. Close browser and stop server
await browser_close();
await KillShell({ shell_id: "npm_start_shell" });
```

### Regression Testing

```javascript
// Run after EVERY step to ensure nothing broke
async function runRegressionTests(upToStep) {
  for (let step = 1; step <= upToStep; step++) {
    console.log(`Testing Step ${step} functionality...`);

    // Navigate to step-specific features
    await browser_navigate({ url: `http://localhost:3000/step${step}` });

    // Verify step still works
    const snapshot = await browser_snapshot();

    // Check for expected elements
    await browser_wait_for({
      text: `Step ${step} Complete`,
      time: 5
    });

    // Take comparison screenshot
    await browser_take_screenshot({
      filename: `regression-step-${step}.png`
    });
  }
}
```

## Commands Reference

```bash
# Development
npm start
npm test
npm run build

# Testing with Playwright MCP
# (Executed through Claude Code, not terminal)
browser_navigate({ url: "http://localhost:3000" })
browser_snapshot()
browser_click({ element: "button", ref: "#submit" })
browser_take_screenshot({ filename: "test.png" })

# Git Workflow
git checkout -b step-{number}
git add .
git commit -m "STEP-{number}: {description}"
git push origin step-{number}
```

## Continuous Update Protocol
After EVERY step completion:
1. Update step YAML status
2. Add implementation_notes with discoveries
3. Document any learner_feedback
4. Verify all previous steps still work
5. Commit changes with message: "STEP-{id}: {description}"

## Emergency Recovery
If something breaks:
1. Check step_{n-1} end code
2. Verify environment variables
3. Clear cache and reinstall dependencies
4. Refer to implementation_notes for context

## Project Standards

### Code Style
- Use 2 spaces for indentation
- Use meaningful variable names
- Comment complex logic
- Keep functions under 20 lines

### File Organization
```
src/
├── components/
├── services/
├── utils/
├── styles/
└── tests/
```

### Naming Conventions
- Components: PascalCase
- Functions: camelCase
- Constants: UPPER_SNAKE_CASE
- CSS classes: kebab-case

</teaching-plan-structure>

<output-structure>
```
.claude-project-management/
├── TEACHING-PLAN.md          # Master plan with live status
├── TEACHING-CONTEXT.yaml     # Codebase analysis and progress
├── PROJECT-README.md         # Complete project documentation
├── steps/
│   ├── step-001/
│   │   ├── start-code/       # Complete starting point
│   │   ├── end-code/         # Complete ending point
│   │   ├── lesson.md         # Detailed teaching content
│   │   └── changes.diff      # What changed in this step
│   └── [steps 2-10...]
├── testing-framework/
│   ├── playwright-teaching.config.js
│   └── tests/
│       └── teaching-steps/
│           └── [test files...]
└── progress-reports/
    └── [timestamp]-status.yaml
```
</output-structure>

<validation-rules>
Before marking ANY step complete - LIVE VERIFICATION:
☐ Previous step's end-code works perfectly (tested with browser_navigate)
☐ New functionality works as specified (verified with browser_snapshot)
☐ All previous features still functional (regression test with browser_wait_for)
☐ UI elements are accessible (checked with browser_snapshot)
☐ Forms work correctly (tested with browser_fill_form)
☐ Navigation works (verified with browser_click and browser_navigate)
☐ Screenshots captured for documentation (browser_take_screenshot)
☐ Mobile/desktop responsive (tested with browser_resize)
☐ Console has no errors (checked with browser_console_messages)
☐ YAML status reflects current state
☐ Junior developer could continue from this point
</validation-rules>

<critical-reminders>
- This is a LIVING DOCUMENT - update continuously
- Never skip pre-implementation checks
- Document EVERYTHING a future developer needs
- Test external behavior, not implementation details
- Keep the application working after EVERY change
- The plan is the single source of truth
- Update after EVERY task completion
- New developer should continue using ONLY codebase and documentation
</critical-reminders>

<execution-notes>
- Use <thinking> tags to plan analysis approach
- Verify each step produces working code
- Include helpful comments in all code
- Explain the "why" not just the "how"
- Anticipate common beginner mistakes
- Provide clear error messages and debugging tips
- Keep technical jargon to minimum
- Use progressive disclosure of complexity
</execution-notes>

<output-checklist>
☐ All project features identified and documented
☐ 10 progressive steps defined with clear boundaries
☐ Each step has complete start and end code
☐ Lessons explain concepts for absolute beginners
☐ Playwright tests provided for each step
☐ YAML tracking structure in place
☐ Living documentation approach implemented
☐ Junior developer can execute independently
☐ Architecture decisions documented with reasoning
☐ Emergency recovery procedures included
</output-checklist>