# Hometab - Developer Documentation

> Comprehensive documentation for developers working on Hometab.

**Version:** 1.0.0 | **Last Updated:** 2026-02-12

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Key Components](#key-components)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Architecture Overview

Hometab follows a **static build pipeline** architecture:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Build Layer (Python)                              │
│   Parses bookmarks.html OR bookmarks_clean.json → apps.json → index.html     │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────┐
│                    Template Layer (HTML)                      │
│   template.html + settings.json + apps data → index.html    │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                   Runtime Layer (JS + CSS)                    │
│   localStorage state, drag-drop, settings, drawer, dock     │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Static HTML (no server) | Opens instantly as browser homepage via `file://` protocol |
| localStorage for runtime state | No server needed; state persists across sessions |
| Python build step | Parses browser bookmark exports (HTML format) or clean JSON selections and bakes data into HTML |
| Single-file output | Browser homepage must be a single `index.html` with embedded CSS/JS references |
| Glassmorphic UI | Modern, visually appealing tablet-like experience |

---

## Project Structure

```
hometab/
├── src/
│   ├── build.py              # Unified bookmark parser + HTML generator
│   ├── template.html         # HTML template with placeholders
│   ├── script.js             # Client-side logic (~580 lines)
│   ├── style.css             # Glassmorphic styles (~580 lines)
│   ├── settings.json         # Build-time configuration
│   ├── apps.json             # Generated bookmark data (gitignored)
│   ├── index.html            # Generated output (gitignored)
│   └── assets/
│       ├── home.svg          # App icon
│       ├── wallpapers/       # Wallpaper images
│       └── bookmarks/        # Place bookmarks.html here
├── README.md                 # User-facing documentation
├── DEVELOPMENT.md            # This file
├── CHANGELOG.md              # Version history
├── TASKS.md                  # Roadmap
├── LICENSE.md                # License terms
└── .gitignore
```

---

## Configuration

### settings.json

| Setting | Default | Description |
|---------|---------|-------------|
| `wallpaper` | `"assets/wallpapers/Giselle.jpeg"` | Path to wallpaper image (relative to `src/`) |
| `clock_format` | `"12h"` | Clock display format (`12h` or `24h`) |
| `transparency` | `0.3` | Glass element transparency (0-1) |
| `blur_amount` | `"50px"` | Backdrop blur radius |
| `clock_position.top` | `"40px"` | Clock vertical position |
| `clock_position.left` | `"30%"` | Clock horizontal position |

---

## Key Components

### build.py

The unified build script handles the entire pipeline:

| Function | Description |
|----------|-------------|
| `parse_bookmarks(file_path)` | Parses browser bookmark HTML export or `bookmarks_clean.json` into app dicts |
| `get_icon_html(icon_val)` | Converts icon values to HTML with broken-image fallback |
| `build_index(apps, settings, template, output)` | Generates final `index.html` from template and data |
| `main()` | CLI entry point with path resolution and error handling |

### script.js (Runtime)

| Component | Description |
|-----------|-------------|
| `syncAppsFromConfig()` | Rebuilds dock and drawer UI from localStorage config |
| `saveCurrentConfig()` | Persists current app state to localStorage |
| `applySettings(s)` | Applies wallpaper, blur, transparency, clock settings |
| `toggleSettings()` | Opens/closes the settings modal |
| `handleDrop(e)` | Drag-and-drop swap handler for dock items |
| `escapeHtml(str)` | XSS protection for runtime-injected content |

---

## Deployment

### Browser Homepage Setup

1. Run `python src/build.py` to generate `src/index.html`
2. Set `file:///absolute/path/to/hometab/src/index.html` as your browser's homepage
3. For new-tab replacement, use a "Custom New Tab" browser extension

### Production Checklist

- [ ] Bookmarks exported and placed at `src/assets/bookmarks/bookmarks.html`
- [ ] Wallpaper image placed in `src/assets/wallpapers/`
- [ ] `settings.json` configured with correct wallpaper path
- [ ] Build runs without errors
- [ ] Homepage opens in browser without console errors

---

## Commands

### `build.py`

Parse bookmarks and generate `index.html`.

```bash
# Default (uses src/assets/bookmarks/bookmarks.html)
python src/build.py

# Custom bookmarks file
python src/build.py /path/to/my/bookmarks.html
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"No bookmarks file found"** | Place your exported `bookmarks.html` at `src/assets/bookmarks/bookmarks.html` |
| **Broken favicon images** | Icons auto-fallback to 🌐; re-run build or change favicon via right-click menu |
| **Settings lost after rebuild** | Export config from Settings before rebuilding; import after |
| **Blank page on homepage** | Check that `index.html` path in browser settings is correct and absolute |
| **Clock position resets** | Clock position is saved in localStorage; clearing site data resets it |

---

## Contributing

### Code Style

- Vanilla JS only — no frameworks or build tools
- CSS follows glassmorphic design tokens in `:root`
- Python uses standard library only — no pip dependencies
- All user-controlled strings must be HTML-escaped

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/feature-name`)
3. Make your changes
4. Run `python src/build.py` to verify the build
5. Commit with clear messages
6. Push and create a Pull Request

### Project Standards

- No external dependencies (stdlib only for Python, vanilla for JS/CSS)
- HTML-escape all user content (XSS protection)
- Graceful error handling — never crash silently

---

<p align="center">
  <a href="README.md">← Back to README</a>
</p>
