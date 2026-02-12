# Hometab Changelog

> **Project:** Hometab  
> **Version:** 1.0.0  
> **Last Updated:** 2026-02-12

---

## [1.0.0] - 2026-02-12

### Added
- Unified `build.py` combining bookmark parsing and HTML generation
- Graceful error handling throughout the build pipeline
- CLI argument support for custom bookmark file paths
- XSS protection — HTML-escaping of app names, URLs, and icons in both build and runtime
- Wallpaper URL sanitization in runtime settings
- Broken favicon fallback — failed `<img>` icons degrade to 🌐
- `escapeHtml()` utility in `script.js` for runtime XSS protection
- `README.md`, `DEVELOPMENT.md`, `CHANGELOG.md`, `LICENSE.md`, `TASKS.md`

### Changed
- Restructured project: all code files moved to `src/`
- Replaced all `location.reload()` calls with in-place `syncAppsFromConfig()` re-render
- Merged duplicate `.app-icon` CSS rules into single definition
- Page title changed from "Tablet OS Mimic" to "Hometab"

### Fixed
- `ReferenceError` from undefined `hqFaviconsSelect` / `faviconSourceSelect` variables in Settings
- Drag-and-drop not swapping `data-icon` / `data-original-icon` metadata
- Duplicate `googleaistudio` ID collision in bookmark parsing
- `wallapapers` typo → `wallpapers` in settings, gitignore, and directory name

### Security
- App names and URLs are HTML-escaped at build time (`html.escape()`) and runtime (`escapeHtml()`)
- Wallpaper URL stripped of special characters before CSS injection

### Removed
- Separate `bookmarks.py` (merged into `build.py`)
- Old `build.py` (replaced by unified version in `src/`)
