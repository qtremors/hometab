"""
Hometab Build Script
Parses browser bookmark exports and generates index.html.

Usage:
    python build.py                          # Uses default paths
    python build.py path/to/bookmarks.html   # Custom bookmarks file
"""

import json
import html
import re
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


# ── Bookmark Parsing ──────────────────────────────────────────────────────────

def parse_bookmarks(file_path):
    """Parse a browser bookmarks HTML export into a list of app dicts."""
    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"  Error: Bookmark file not found: {file_path}")
        return []
    except UnicodeDecodeError:
        print(f"  Error: Could not decode {file_path} as UTF-8")
        return []

    # Regex to find bookmark lines: <DT><A HREF="..." ...>Title</A>
    # Also capture ICON if present: ICON="data:..."
    pattern = re.compile(
        r'<DT><A HREF="(?P<url>[^"]+)"(?:[^>]*?ICON="(?P<icon>[^"]+)")?[^>]*>(?P<name>.*?)</A>',
        re.IGNORECASE
    )

    apps = []
    seen_ids = set()

    for match in pattern.finditer(content):
        data = match.groupdict()

        # Clean title (handle &amp; etc)
        name = data['name'].replace('&amp;', '&').replace('&quot;', '"').strip()
        if not name:
            continue

        # Generate unique ID from name
        app_id = re.sub(r'[^a-z0-9]', '', name.lower())[:15]
        if not app_id:
            app_id = f"app_{len(apps)}"

        # Handle ID collisions
        original_id = app_id
        counter = 1
        while app_id in seen_ids:
            app_id = f"{original_id[:12]}{counter}"
            counter += 1
        seen_ids.add(app_id)

        apps.append({
            "id": app_id,
            "name": name,
            "icon": data['icon'] if data['icon'] else "🌐",
            "url": data['url'],
            "docked": False
        })

    return apps


# ── HTML Generation ───────────────────────────────────────────────────────────

def get_icon_html(icon_val):
    """Convert an icon value into an HTML string with broken-image fallback."""
    onerror = "this.replaceWith(document.createTextNode('🌐'))"
    if icon_val.startswith('data:image'):
        return f'<img src="{icon_val}" alt="icon" onerror="{onerror}">'
    if any(icon_val.endswith(ext) for ext in ['.svg', '.png', '.jpg', '.jpeg', '.webp']):
        return f'<img src="{html.escape(icon_val)}" alt="icon" onerror="{onerror}">'
    return html.escape(icon_val)


def build_index(apps_data, settings_path, template_path, output_path):
    """Generate index.html from template, apps data, and settings."""

    # Load settings
    if not os.path.exists(settings_path):
        print(f"  Error: Settings file not found: {settings_path}")
        return False

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            base_config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  Error: Invalid JSON in {settings_path}: {e}")
        return False

    # Merge apps: settings.json apps (if any) + parsed bookmark apps
    all_apps = base_config.get('apps', []) + apps_data

    # Ensure 'Settings' app exists
    if not any(app.get('id') == 'settings' for app in all_apps):
        all_apps.append({
            "id": "settings",
            "name": "Settings",
            "icon": "⚙️",
            "url": "#",
            "docked": True,
            "position": 999
        })

    # Deduplicate by URL and filter system pages
    seen_urls = set()
    unique_apps = []
    for app in all_apps:
        name = str(app.get('name', '')).strip()
        url = str(app.get('url', '')).strip()

        if (not name or not url or url.startswith('chrome://') or url == '#') and app.get('id') != 'settings':
            continue

        if url not in seen_urls:
            unique_apps.append(app)
            seen_urls.add(url if url != '#' else f"internal://{app['id']}")

    # Sort: drawer = alphabetical, dock = by position
    drawer_apps = sorted(unique_apps, key=lambda x: str(x.get('name', '')).lower())
    docked_apps = sorted([a for a in unique_apps if a.get('docked')], key=lambda x: x.get('position', 0))

    # Generate dock HTML
    dock_html = ""
    for app in docked_apps:
        icon_html = get_icon_html(app["icon"])
        display_name = html.escape(app["name"])
        display_url = html.escape(app.get("url", "#"))
        icon_val = html.escape(app["icon"])
        tooltip = f"{display_name}\n{display_url}"
        dock_html += (
            f'                <div class="dock-item" draggable="true" '
            f'data-id="{html.escape(app["id"])}" data-url="{display_url}" '
            f'data-name="{display_name}" data-icon="{icon_val}" '
            f'data-original-icon="{icon_val}" title="{tooltip}">'
            f'{icon_html}</div>\n'
        )

    # Generate drawer HTML
    drawer_html = ""
    for app in drawer_apps:
        icon_html = get_icon_html(app["icon"])
        display_name = html.escape(app["name"])
        display_url = html.escape(app.get("url", "#"))
        icon_val = html.escape(app["icon"])
        tooltip = f"{display_name}\n{display_url}"
        drawer_html += (
            f'                <div class="app-icon thin dock-style" '
            f'data-id="{html.escape(app["id"])}" data-url="{display_url}" '
            f'data-name="{display_name}" data-icon="{icon_val}" '
            f'data-original-icon="{icon_val}" title="{tooltip}">\n'
            f'                    <div class="icon-wrapper">{icon_html}</div>\n'
            f'                    <span class="app-label">{display_name}</span>\n'
            f'                </div>\n'
        )

    # Read template
    if not os.path.exists(template_path):
        print(f"  Error: Template file not found: {template_path}")
        return False

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"  Error: Could not read template: {e}")
        return False

    # Get settings for wallpaper and clock
    settings = base_config.get('settings', {})
    wallpaper_url = settings.get('wallpaper', '')
    clock_pos = settings.get('clock_position', {'top': '40px', 'left': '50%'})
    wallpaper_style = f'style="background-image: url(\'{wallpaper_url}\');"'
    clock_style = f'style="top: {clock_pos["top"]}; left: {clock_pos["left"]}; transform: translateX(-50%); position: absolute;"'

    # Assemble final HTML
    final_html = template.replace("{DOCK_CONTENT}", dock_html).replace("{DRAWER_CONTENT}", drawer_html)
    final_html = final_html.replace("WALLPAPER_STYLE_PLACEHOLDER", wallpaper_style)
    final_html = final_html.replace("CLOCK_STYLE_PLACEHOLDER", clock_style)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
    except Exception as e:
        print(f"  Error: Could not write output: {e}")
        return False

    return True


# ── Backup ────────────────────────────────────────────────────────────────────

def backup_existing(apps_file, output_file, backup_dir):
    """Backup existing apps.json and index.html before overwriting."""
    if not apps_file.exists() and not output_file.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / timestamp

    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        copied = []
        for src in [apps_file, output_file]:
            if src.exists():
                shutil.copy2(src, backup_path / src.name)
                copied.append(src.name)
        if copied:
            print(f"  Backup: {', '.join(copied)} → backups/{timestamp}/")
    except Exception as e:
        print(f"  Warning: Could not create backup: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Resolve paths relative to this script's location
    script_dir = Path(__file__).parent.resolve()

    bookmark_file = script_dir / "assets" / "bookmarks" / "bookmarks.html"
    apps_file = script_dir / "apps.json"
    settings_file = script_dir / "settings.json"
    template_file = script_dir / "template.html"
    output_file = script_dir / "index.html"
    backup_dir = script_dir / "backups"

    # Allow custom bookmark path via CLI arg
    if len(sys.argv) > 1:
        bookmark_file = Path(sys.argv[1]).resolve()

    print("Hometab Build")
    print("─" * 40)

    # Step 0: Backup existing files
    backup_existing(apps_file, output_file, backup_dir)

    # Step 1: Parse bookmarks
    apps = []
    if bookmark_file.exists():
        print(f"  Parsing bookmarks: {bookmark_file.name}")
        apps = parse_bookmarks(str(bookmark_file))
        print(f"  Found {len(apps)} bookmarks")

        # Save apps.json
        try:
            with open(apps_file, 'w', encoding='utf-8') as f:
                json.dump(apps, f, indent=4)
            print(f"  Saved: {apps_file.name}")
        except Exception as e:
            print(f"  Warning: Could not save {apps_file.name}: {e}")
    elif apps_file.exists():
        # No bookmarks file, but apps.json exists from a previous run
        print(f"  No bookmarks file found, using existing {apps_file.name}")
        try:
            with open(apps_file, 'r', encoding='utf-8') as f:
                apps = json.load(f)
            print(f"  Loaded {len(apps)} apps")
        except Exception as e:
            print(f"  Error: Could not read {apps_file.name}: {e}")
            return 1
    else:
        print("  No bookmarks file or apps.json found.")
        print(f"  Place your bookmarks export at: {bookmark_file}")
        print("  Building with Settings app only...")

    # Step 2: Build index.html
    print(f"  Building: {output_file.name}")
    success = build_index(apps, str(settings_file), str(template_file), str(output_file))

    if success:
        size_kb = output_file.stat().st_size / 1024
        print(f"  Output: {output_file.name} ({size_kb:.0f} KB)")
        print("─" * 40)
        print("  Done! Set index.html as your browser homepage.")
        return 0
    else:
        print("  Build failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
