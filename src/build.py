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
import urllib.request
from pathlib import Path
from datetime import datetime


# ── Icon Downloading ──────────────────────────────────────────────────────────

def download_icon(url, domain, icons_dir):
    """Download an icon from a URL and save it locally."""
    if not url or url == "🌐" or url.startswith('data:'):
        return None

    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Try common extensions, fallback to .png
    ext = ".png"
    if ".svg" in url.lower(): ext = ".svg"
    elif ".ico" in url.lower(): ext = ".ico"
    elif ".webp" in url.lower(): ext = ".webp"
    
    local_path = icons_dir / f"{domain}{ext}"
    
    if local_path.exists():
        return f"assets/icons/{local_path.name}"

    try:
        print(f"    Downloading icon: {domain}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(local_path, 'wb') as f:
                f.write(response.read())
        return f"assets/icons/{local_path.name}"
    except Exception as e:
        print(f"    Warning: Could not download icon for {domain}: {e}")
        return None


def get_local_icon(domain, icons_dir):
    """Check if a local icon exists for the domain."""
    for ext in ['.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico']:
        test_path = icons_dir / f"{domain}{ext}"
        if test_path.exists():
            return f"assets/icons/{test_path.name}"
    return None


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
    clean_bookmarks_file = script_dir / "assets" / "bookmarks" / "bookmarks_clean.json"
    apps_file = script_dir / "apps.json"
    settings_file = script_dir / "settings.json"
    template_file = script_dir / "template.html"
    output_file = script_dir / "index.html"
    backup_dir = script_dir / "backups"
    icons_dir = script_dir / "assets" / "icons"

    # CLI Arguments
    fetch_icons_flag = "--fetch-icons" in sys.argv
    custom_bookmark = next((Path(arg).resolve() for arg in sys.argv[1:] if not arg.startswith('--')), None)
    if custom_bookmark:
        bookmark_file = custom_bookmark

    print("Hometab Build")
    print("─" * 40)

    # Step 0: Backup existing files
    backup_existing(apps_file, output_file, backup_dir)

    # Step 1: Parse bookmarks or load clean JSON
    apps = []
    if clean_bookmarks_file.exists():
        print(f"  Using clean selection: {clean_bookmarks_file.name}")
        try:
            with open(clean_bookmarks_file, 'r', encoding='utf-8') as f:
                apps = json.load(f)
            print(f"  Loaded {len(apps)} selected apps")
        except Exception as e:
            print(f"  Error: Could not read {clean_bookmarks_file.name}: {e}")
            return 1
    elif bookmark_file.exists():
        print(f"  Parsing bookmarks: {bookmark_file.name}")
        apps = parse_bookmarks(str(bookmark_file))
        print(f"  Found {len(apps)} bookmarks")
    
    # Load settings to check for auto_fetch_icons
    auto_fetch = fetch_icons_flag
    if not auto_fetch and settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f).get('settings', {})
                auto_fetch = settings_data.get('auto_fetch_icons', False)
        except: pass

    # Step 2: High-Resolution Icon Processing
    if apps and (auto_fetch or any(get_local_icon(re.sub(r'^https?://(www\.)?', '', app.get('url', '')).split('/')[0], icons_dir) for app in apps)):
        print("  Processing high-res icons...")
        icons_dir.mkdir(parents=True, exist_ok=True)
        for app in apps:
            url = app.get('url', '')
            if not url or url == '#': continue
            
            domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
            if not domain: continue

            # Check for local override first
            local_icon = get_local_icon(domain, icons_dir)
            
            if local_icon:
                app['icon'] = local_icon
            elif auto_fetch:
                # Try to download from Clearbit or Google if no local icon
                hq_url = f"https://logo.clearbit.com/{domain}?size=256"
                downloaded = download_icon(hq_url, domain, icons_dir)
                if not downloaded:
                    # Fallback to Google HQ
                    hq_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=256"
                    downloaded = download_icon(hq_url, domain, icons_dir)
                
                if downloaded:
                    app['icon'] = downloaded

    # Save apps.json for the runtime
    if apps:
        try:
            with open(apps_file, 'w', encoding='utf-8') as f:
                json.dump(apps, f, indent=4)
            print(f"  Saved: {apps_file.name}")
        except Exception as e:
            print(f"  Warning: Could not save {apps_file.name}: {e}")
    elif apps_file.exists():
        # No bookmarks file, but apps.json exists from a previous run
        print(f"  No source found, using existing {apps_file.name}")
        try:
            with open(apps_file, 'r', encoding='utf-8') as f:
                apps = json.load(f)
            print(f"  Loaded {len(apps)} apps")
        except Exception as e:
            print(f"  Error: Could not read {apps_file.name}: {e}")
            return 1
    else:
        print("  No bookmarks source found.")
        print(f"  Place your bookmarks export at: {bookmark_file}")
        print(f"  Or export selection to: {clean_bookmarks_file}")
        print("  Building with Settings app only...")

    # Step 3: Build index.html
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
