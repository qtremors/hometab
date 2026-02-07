import json
import os

def build_index():
    settings_path = 'settings.json'
    apps_path = 'apps.json'
    output_path = 'index.html'

    # Load settings
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            base_config = json.load(f)
    else:
        print(f"Error: {settings_path} not found.")
        return

    # Load bookmark apps
    bookmark_apps = []
    if os.path.exists(apps_path):
        with open(apps_path, 'r', encoding='utf-8') as f:
            bookmark_apps = json.load(f)

    # Merge and Clean apps (settings.json apps + apps.json bookmarks)
    all_apps = base_config.get('apps', []) + bookmark_apps
    
    # Ensure 'Settings' app exists if not already present
    if not any(app.get('id') == 'settings' for app in all_apps):
        all_apps.append({
            "id": "settings",
            "name": "Settings",
            "icon": "⚙️",
            "url": "#",
            "docked": True,
            "position": 999
        })

    # Simple deduplication and filtering of "fake" apps
    seen_urls = set()
    unique_apps = []
    for app in all_apps:
        name = str(app.get('name', '')).strip()
        url = str(app.get('url', '')).strip()
        
        # Filter: Skip if name is empty or url is internal system (except settings)
        if (not name or not url or url.startswith('chrome://') or url == '#') and app.get('id') != 'settings':
            continue
            
        if url not in seen_urls:
            unique_apps.append(app)
            seen_urls.add(url if url != '#' else f"internal://{app['id']}")

    # Sort apps for the drawer (alphabetical, case-insensitive)
    drawer_apps = sorted(unique_apps, key=lambda x: str(x.get('name', '')).lower())
    
    # Sort apps for the dock (by position)
    docked_apps = sorted([a for a in unique_apps if a.get('docked')], key=lambda x: x.get('position', 0))

    def get_icon_html(icon_val):
        if icon_val.startswith('data:image'):
            return f'<img src="{icon_val}" alt="icon">'
        if any(icon_val.endswith(ext) for ext in ['.svg', '.png', '.jpg', '.jpeg', '.webp']):
            return f'<img src="{icon_val}" alt="icon">'
        return icon_val

    # Generate HTML strings
    dock_html = ""
    for app in docked_apps:
        icon_html = get_icon_html(app["icon"])
        display_name = app["name"]
        display_url = app.get("url", "#")
        icon_val = app["icon"]
        icon_attr = f' data-icon="{icon_val}"'
        orig_icon_attr = f' data-original-icon="{icon_val}"'
        tooltip = f"{display_name}\n{display_url}"
        dock_html += f'                <div class="dock-item" draggable="true" data-id="{app["id"]}" data-url="{display_url}" data-name="{display_name}"{icon_attr}{orig_icon_attr} title="{tooltip}">{icon_html}</div>\n'

    drawer_html = ""
    for app in drawer_apps:
        icon_html = get_icon_html(app["icon"])
        display_name = app["name"]
        display_url = app.get("url", "#")
        icon_val = app["icon"]
        icon_attr = f' data-icon="{icon_val}"'
        orig_icon_attr = f' data-original-icon="{icon_val}"'
        tooltip = f"{display_name}\n{display_url}"
        drawer_html += f'''                <div class="app-icon thin dock-style" data-id="{app["id"]}" data-url="{display_url}" data-name="{display_name}"{icon_attr}{orig_icon_attr} title="{tooltip}">
                    <div class="icon-wrapper">{icon_html}</div>
                    <span class="app-label">{display_name}</span>
                </div>\n'''

    # Read template from file
    template_path = 'template.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        print(f"Error: {template_path} not found.")
        return
    
    # Get settings
    settings = base_config.get('settings', {})
    wallpaper_url = settings.get('wallpaper', '')
    clock_pos = settings.get('clock_position', {'top': '40px', 'left': '50%'})
    wallpaper_style = f'style="background-image: url(\'{wallpaper_url}\');"'
    clock_style = f'style="top: {clock_pos["top"]}; left: {clock_pos["left"]}; transform: translateX(-50%); position: absolute;"'

    final_html = template.replace("{DOCK_CONTENT}", dock_html).replace("{DRAWER_CONTENT}", drawer_html)
    final_html = final_html.replace("WALLPAPER_STYLE_PLACEHOLDER", wallpaper_style)
    final_html = final_html.replace("CLOCK_STYLE_PLACEHOLDER", clock_style)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"Successfully built {output_path}")

if __name__ == "__main__":
    build_index()
