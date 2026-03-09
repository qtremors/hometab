<p align="center">
  <img src="src/assets/home.svg" alt="Hometab Logo" width="120"/>
</p>

<h1 align="center"><a href="https://github.com/qtremors/hometab">Hometab</a></h1>

<p align="center">
  A browser homepage replacement that displays your bookmarks as apps — like a tablet home screen.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-TSL-red" alt="License">
</p>

> [!NOTE]
> **Personal Project** 🎯 I built this because browsers don't offer a good way to view and organize bookmarks visually. This replaces the default new-tab page with a clean, glassmorphic app launcher.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📱 **App Drawer** | Scroll down to reveal all bookmarks as app icons, with fuzzy search |
| 🖱️ **Selection Mode** | Interactively pick which bookmarks to keep; exports a clean JSON for the build script |
| 🔲 **Dock** | Pin frequently used apps to a macOS-style dock with magnification on hover |
| 🔄 **Drag & Drop** | Reorder dock items by dragging |
| 📋 **Context Menu** | Right-click to pin/unpin, delete, change favicon, or restore original icon |
| 🕐 **Live Clock** | Draggable clock widget with 12h/24h support |
| ⚙️ **Settings** | Configurable wallpaper, blur, transparency, and clock format |
| 📤 **Import/Export** | Export config as JSON; import bookmarks or configs at runtime |
| 🔒 **Fully Offline** | No server. Just a local HTML file opened by your browser |

---

## 🚀 Quick Start

```bash
# Clone and navigate
git clone https://github.com/qtremors/hometab.git
cd hometab
```

### 1. Add your bookmarks

Export your bookmarks from your browser (Bookmarks → Bookmark Manager → Export) and place the file at:

```
src/assets/bookmarks/bookmarks.html
```

### 2. Build (Initial)

```bash
python src/build.py
```

This parses your bookmarks and generates `src/index.html`.

### 3. Clean up (Selection Mode)

If you have too many bookmarks and want to pick only a few:
1. Open `src/index.html` in your browser.
2. Go to **Settings** → Toggle **Selection Mode**.
3. Click the apps you want to keep.
4. Click **Extract Selection** to download `bookmarks_clean.json`.
5. Move `bookmarks_clean.json` to `src/assets/bookmarks/`.
6. Run `python src/build.py` again.

### 4. Set as homepage

- **Chrome/Brave**: Settings → On startup → Open a specific page → Add `file:///path/to/hometab/src/index.html`
- Or use a "Custom New Tab" extension to point to the file.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Markup** | HTML5 |
| **Styling** | CSS3 (glassmorphism, animations) |
| **Logic** | Vanilla JavaScript |
| **Build** | Python 3 (bookmark parser + HTML generator) |
| **Storage** | localStorage (runtime state) |

---

## 📁 Project Structure

```
hometab/
├── src/
│   ├── build.py          # Bookmark parser + HTML generator
│   ├── template.html     # HTML template with placeholders
│   ├── script.js         # Client-side logic (drawer, dock, settings)
│   ├── style.css         # Glassmorphic styles
│   ├── settings.json     # Build-time settings (wallpaper, clock)
│   ├── apps.json         # Generated bookmark data (gitignored)
│   ├── index.html        # Generated output (gitignored)
│   └── assets/
│       ├── wallpapers/   # Wallpaper images
│       └── bookmarks/    # Place bookmarks.html here
├── DEVELOPMENT.md        # Developer documentation
├── CHANGELOG.md          # Version history
├── TASKS.md              # Project roadmap
├── LICENSE.md            # License terms
└── README.md
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Architecture, project structure, configuration |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [TASKS.md](TASKS.md) | Roadmap and planned features |
| [LICENSE.md](LICENSE.md) | License terms and attribution |

---

## 📄 License

**Tremors Source License (TSL) Version 2.0** - Source-available license allowing viewing, forking, and derivative works with **mandatory attribution**. Commercial use requires written permission.

See [LICENSE.md](LICENSE.md) for full terms.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/qtremors">Tremors</a>
</p>
