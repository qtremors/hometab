import json
import re
from pathlib import Path

def parse_bookmarks(file_path):
    content = Path(file_path).read_text(encoding='utf-8')
    
    # Simple regex to find bookmark lines: <DT><A HREF="..." ...>Title</A>
    # Also capture ICON if present: ICON="data:..."
    pattern = re.compile(r'<DT><A HREF="(?P<url>[^"]+)"(?:[^>]*?ICON="(?P<icon>[^"]+)")?[^>]*>(?P<name>.*?)</A>', re.IGNORECASE)
    
    apps = []
    for match in pattern.finditer(content):
        data = match.groupdict()
        
        # Clean title (handle &amp; etc)
        name = data['name'].replace('&amp;', '&').replace('&quot;', '"').strip()
        
        # Shorten ID from name
        app_id = re.sub(r'[^a-z0-9]', '', name.lower())[:15]
        if not app_id:
            app_id = f"app_{len(apps)}"
            
        apps.append({
            "id": app_id,
            "name": name,
            "icon": data['icon'] if data['icon'] else "🌐",
            "url": data['url'],
            "docked": False
        })
        
    return apps

if __name__ == "__main__":
    bookmark_file = "assets/bookmarks/bookmarks.html"
    output_file = "apps.json"
    
    if Path(bookmark_file).exists():
        extracted_apps = parse_bookmarks(bookmark_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_apps, f, indent=4)
        print(f"Successfully extracted {len(extracted_apps)} apps to {output_file}")
    else:
        print(f"Error: {bookmark_file} not found.")
