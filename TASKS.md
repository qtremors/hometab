# Hometab - Tasks

> **Project:** Hometab  
> **Version:** 1.0.0  
> **Last Updated:** 2026-02-12

---

## 📋 To Do

### High Priority
- [ ] Split `script.js` into ES modules (`clock.js`, `drawer.js`, `dock.js`, `settings.js`)

### Medium Priority
- [ ] Add bookmark folder support → map folders to app categories/sections
- [ ] Add theme presets (dark, light, custom blur levels)
- [ ] Auto-focus search bar when drawer opens
- [ ] Add keyboard shortcut to open drawer (e.g., `Space` or `/`)

### Low Priority
- [ ] Responsive grid breakpoints for ultrawide/narrow screens
- [ ] Click on homepage background to close drawer (not just scroll)
- [ ] Auto-backup localStorage before importing new config

---

## 💡 Ideas / Future

- Fetch favicons on-demand from Google/DuckDuckGo APIs instead of storing base64
- Browser extension wrapper for seamless new-tab replacement
- Optional cloud sync for settings (Firebase, GitHub Gist)
- Widget support (weather, quick notes, calendar)

---

## 🏗️ Architecture Notes

- `index.html` and `apps.json` are generated outputs — never edit them directly
- Runtime state lives in `localStorage`; build-time config lives in `settings.json`
- All user-visible strings must be HTML-escaped (build + runtime)

---
