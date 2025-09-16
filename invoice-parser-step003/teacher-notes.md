# STEP-003: Tailwind CSS and Dark Mode - Teacher Notes

## Overview
In this step, students learn to replace traditional CSS with Tailwind utility classes and implement a dark mode toggle using React Context API.

## Learning Objectives
By the end of this step, students will:
1. Understand utility-first CSS with Tailwind
2. Configure Tailwind in a Vite React project
3. Implement dark mode using React Context
4. Use localStorage for theme persistence
5. Apply responsive design with Tailwind

## Prerequisites
- Completed STEP-002 with working React frontend
- Basic understanding of CSS
- Familiarity with React hooks (useState, useEffect)

## Time Estimate
2-3 hours

## Setup and Run Instructions

### Terminal 1: Backend Server
```bash
cd invoice-parser-step003/ending-code/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend Development
```bash
cd invoice-parser-step003/ending-code/frontend
npm install
npm run dev
```

### Testing the Application
1. Open http://localhost:5173 in browser
2. Verify Tailwind styles are applied (gradient header, cards)
3. Click moon/sun icon to toggle dark mode
4. Refresh page - theme should persist
5. Check responsive design by resizing browser

## Key Concepts Explained

### 1. Tailwind CSS Philosophy
**Traditional CSS:**
```css
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  text-align: center;
}
```

**Tailwind CSS:**
```jsx
<header className="bg-gradient-to-r from-purple-600 to-indigo-600 p-8 text-center">
```

Benefits:
- No context switching between files
- Faster development
- Consistent spacing and colors
- No unused CSS

### 2. Dark Mode Implementation
```jsx
// Context provides theme state globally
const ThemeContext = createContext()

// Toggle function manages class on <html> element
document.documentElement.classList.toggle('dark', theme === 'dark')

// Tailwind dark: prefix applies styles in dark mode
className="bg-white dark:bg-gray-800"
```

### 3. Local Storage for Persistence
```jsx
// Save theme preference
localStorage.setItem('theme', newTheme)

// Load on mount
const savedTheme = localStorage.getItem('theme') || 'light'
```

## Step-by-Step Implementation Guide

### Part 1: Install and Configure Tailwind (15 mins)

1. **Install Dependencies:**
```bash
npm install -D tailwindcss postcss autoprefixer
```

2. **Create Configuration Files:**

`tailwind.config.js`:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',  // Enable class-based dark mode
  theme: {
    extend: {},
  },
  plugins: [],
}
```

`postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

3. **Update index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Part 2: Create Theme Context (20 mins)

`src/contexts/ThemeContext.jsx`:
```jsx
import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    // Load saved theme on mount
    const savedTheme = localStorage.getItem('theme') || 'light'
    setTheme(savedTheme)
    document.documentElement.classList.toggle('dark', savedTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

### Part 3: Apply Tailwind Classes (30 mins)

Key patterns to teach:

**Spacing:**
- `p-4` = padding 1rem
- `m-2` = margin 0.5rem
- `space-x-4` = horizontal spacing between children

**Colors:**
- `bg-white` = white background
- `text-gray-900` = dark gray text
- `dark:bg-gray-800` = gray background in dark mode

**Layout:**
- `flex` = flexbox container
- `grid grid-cols-2` = 2-column grid
- `container mx-auto` = centered container

**Responsive:**
- `md:grid-cols-2` = 2 columns on medium+ screens
- `lg:text-xl` = larger text on large+ screens

## Common Issues and Solutions

### Issue 1: Tailwind Styles Not Applied
**Symptom:** Page looks unstyled
**Solution:**
- Check if `index.css` has Tailwind directives
- Verify `tailwind.config.js` content paths
- Restart dev server after config changes

### Issue 2: Dark Mode Not Working
**Symptom:** Toggle button doesn't change theme
**Solution:**
- Ensure `darkMode: 'class'` in Tailwind config
- Check if ThemeProvider wraps App component
- Verify `document.documentElement.classList` is being toggled

### Issue 3: Theme Doesn't Persist
**Symptom:** Theme resets on page refresh
**Solution:**
- Check localStorage in DevTools
- Ensure useEffect reads localStorage on mount
- Verify localStorage key matches in get/set

### Issue 4: Build Size Concerns
**Symptom:** Large CSS bundle
**Solution:**
- Tailwind only includes used classes in production
- Run `npm run build` to see actual size
- Use PurgeCSS is automatically configured

## Testing Checklist

### Visual Testing
- [ ] Header has gradient background
- [ ] Cards have shadows and rounded corners
- [ ] Loading spinner animates
- [ ] Success/error states have appropriate colors
- [ ] Buttons have hover effects

### Dark Mode Testing
- [ ] Toggle button switches between moon/sun icons
- [ ] Background changes from light to dark
- [ ] Text colors invert appropriately
- [ ] Cards maintain readability in both modes
- [ ] No flashing on page load

### Responsive Testing
- [ ] Info cards stack on mobile
- [ ] Header remains readable on small screens
- [ ] Container has appropriate padding
- [ ] No horizontal scroll on mobile

### Functionality Testing
- [ ] API connection still works
- [ ] Refresh button functions
- [ ] No console errors
- [ ] Theme persists across sessions

## Code Quality Checks

### Before Moving to Next Step
1. Remove unused CSS files (App.css)
2. No inline styles remaining
3. Consistent Tailwind class ordering
4. Dark mode classes next to light equivalents
5. Semantic HTML maintained

### Performance Considerations
- Tailwind generates minimal CSS (only used classes)
- Dark mode adds ~0 runtime overhead
- Theme toggle is instant (no reload needed)
- LocalStorage operations are synchronous but fast

## Extension Activities

### For Advanced Students
1. Add more theme options (system preference, high contrast)
2. Create custom Tailwind color palette
3. Add transition animations for theme switch
4. Implement keyboard shortcut for theme toggle

### Additional Challenges
1. Add theme-aware loading skeleton
2. Create reusable Tailwind components
3. Implement auto dark mode based on time
4. Add theme preference to user profile (later)

## Assessment Points

### Understanding Check
Ask students to:
1. Explain difference between `bg-gray-50` and `dark:bg-gray-900`
2. Show where theme preference is stored
3. Demonstrate adding a new dark mode style
4. Explain why we use Context for theme

### Practical Skills
Students should be able to:
1. Add Tailwind to any element
2. Make any component theme-aware
3. Debug theme switching issues
4. Use responsive Tailwind classes

## Connecting to Next Steps

This step prepares for:
- STEP-004: Database models will have theme-aware forms
- STEP-005: Auth forms will use consistent Tailwind styling
- STEP-006: File upload UI will follow theme patterns

## Resources for Students

### Tailwind Documentation
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Dark Mode Guide](https://tailwindcss.com/docs/dark-mode)
- [Responsive Design](https://tailwindcss.com/docs/responsive-design)

### React Context
- [Context API Docs](https://react.dev/learn/passing-data-deeply-with-context)
- [useContext Hook](https://react.dev/reference/react/useContext)

### Tools
- [Tailwind Play](https://play.tailwindcss.com/) - Online playground
- [Headwind](https://github.com/heybourn/headwind) - VS Code extension for class sorting

## Notes for Instructors

### Time Management
- Tailwind installation: 10 mins
- Context implementation: 20 mins
- Converting styles: 30 mins
- Testing and debugging: 20 mins
- Q&A and exercises: 40 mins

### Common Misconceptions
1. "Tailwind is just inline styles" - Explain utility class benefits
2. "Dark mode slows down the app" - Show it's just CSS classes
3. "Tailwind makes large bundles" - Demonstrate production build

### Teaching Tips
1. Show before/after comparison of CSS vs Tailwind
2. Use DevTools to demonstrate class toggling
3. Build a component together using only Tailwind
4. Emphasize mobile-first responsive approach

## Troubleshooting Script

```bash
# Check if Tailwind is working
npm list tailwindcss

# Rebuild Tailwind
npm run dev

# Check for CSS conflicts
grep -r "\.css" src/

# Verify dark mode class
# In browser console:
document.documentElement.classList.contains('dark')

# Check localStorage
localStorage.getItem('theme')
```

## Summary

By completing STEP-003, students have:
✅ Replaced traditional CSS with Tailwind utilities
✅ Implemented persistent dark mode
✅ Learned Context API for global state
✅ Applied responsive design principles
✅ Improved app aesthetics significantly

The app now has a modern, professional appearance with smooth theme switching, setting a solid foundation for the more complex features to come.