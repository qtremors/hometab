# Hometab Changelog

> **Project:** Hometab  
> **Version:** 1.2.0  
> **Last Updated:** 2026-03-09

---

## [1.2.0] - 2026-03-09

### Added
- **High-Resolution Icon System**: Automated build-time downloader for crisp app logos.
- **Enhanced Favicon Picker**: Added high-quality sources including Clearbit and Icon Horse with "HQ" visual badges.
- **Auto-fetch Setting**: New toggle in Settings to control automated icon downloading during build.
- **CLI Flag**: Added `--fetch-icons` to `build.py` for manual high-res icon retrieval.
- **Local Icon Storage**: Icons are now saved to and served from `src/assets/icons/`.

### Changed
- **Smarter UI Sync**: Dashboard now automatically detects high-res icons in the build and overrides blurry cached versions in `localStorage`.
- **Improved Build Script**: Enhanced CLI argument parsing and modularized icon processing.

### Fixed
- Blurry icons persisting in the UI even after a re-build with high-res sources.
- Domain parsing issues for certain icon API requests.

---

## [1.1.0] - 2026-03-09

### Added
- **Interactive Selection Mode**: A new UI feature to visually pick which bookmarks to keep as apps.
- **Selection Extraction**: Export chosen apps to `bookmarks_clean.json` directly from the dashboard.
- **Selection Mode UI**: Sticky banner with item count and "Extract Selection" button.
- **Reset Layout Button**: "Reset App Layout" option in Settings to clear cache and reload from the latest build.

### Changed
- **Smart Build Pipeline**: `src/build.py` now prioritizes `bookmarks_clean.json` as the input source if present.
- **Intelligent UI Sync**: Dashboard now merges new build data into `localStorage` automatically.
- **Documentation Refactor**: Updated `README.md` and `DEVELOPMENT.md` with the new selection workflow.

### Fixed
- Stale `localStorage` preventing new apps from appearing after a rebuild.
- Build script failing to save `apps.json` if sources were partially missing.

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
