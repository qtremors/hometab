document.addEventListener('DOMContentLoaded', () => {
    const screen = document.getElementById('screen');
    const clock = document.getElementById('clock');
    const dateElement = document.getElementById('date');
    const drawerGrid = document.querySelector('.drawer-grid');
    const dock = document.getElementById('dock');
    const settingsModal = document.getElementById('settings-modal');
    const closeSettings = document.getElementById('close-settings');
    const exportBtn = document.getElementById('export-json');
    const importInput = document.getElementById('import-json');
    const clockFormatSelect = document.getElementById('set-clock-format');
    const wallpaperInput = document.getElementById('set-wallpaper');
    const blurInput = document.getElementById('set-blur');
    const transparencyInput = document.getElementById('set-transparency');

    const faviconModal = document.getElementById('favicon-modal');
    const closeFaviconModal = document.getElementById('close-favicon-modal');
    const faviconGrid = document.getElementById('favicon-grid');
    const faviconModalAppName = document.getElementById('favicon-modal-app-name');

    const contextMenu = document.getElementById('context-menu');
    const menuPin = document.getElementById('menu-pin');
    const menuUnpin = document.getElementById('menu-unpin');
    const menuDelete = document.getElementById('menu-delete');
    const menuChooseFavicon = document.getElementById('menu-choose-favicon');
    const menuSrcReset = document.getElementById('menu-src-reset');

    const addAppBtn = document.getElementById('add-app-btn');
    const newAppName = document.getElementById('new-app-name');
    const newAppUrl = document.getElementById('new-app-url');
    const newAppIcon = document.getElementById('new-app-icon');

    let touchStartY = 0;
    let isDrawerOpen = false;
    let contextApp = null;
    let dragSrcEl = null;

    // --- Utilities ---
    function saveCurrentConfig() {
        const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
        const apps = [];

        // Save Clock Position
        const clockEl = document.getElementById('draggable-clock');
        if (clockEl && config.settings) {
            config.settings.clock_position = { top: clockEl.style.top, left: clockEl.style.left };
        }

        // Save Docked Apps
        document.querySelectorAll('#dock .dock-item').forEach((app, index) => {
            apps.push({
                id: app.getAttribute('data-id'),
                name: app.getAttribute('data-name'),
                url: app.getAttribute('data-url'),
                icon: app.getAttribute('data-icon'),
                original_icon: app.getAttribute('data-original-icon'),
                docked: true,
                position: index
            });
        });

        // Save Drawer Apps
        document.querySelectorAll('.drawer-grid .app-icon').forEach((app) => {
            apps.push({
                id: app.getAttribute('data-id'),
                name: app.getAttribute('data-name'),
                url: app.getAttribute('data-url'),
                icon: app.getAttribute('data-icon'),
                original_icon: app.getAttribute('data-original-icon'),
                docked: false
            });
        });

        // Deduplicate by ID and ensure strict alphabetical sort for drawer
        const uniqueAppsMap = new Map();
        apps.forEach(app => uniqueAppsMap.set(app.id, app));

        config.apps = Array.from(uniqueAppsMap.values()).sort((a, b) => {
            if (a.docked && b.docked) return (a.position || 0) - (b.position || 0);
            if (!a.docked && !b.docked) return (a.name || '').toLowerCase().localeCompare((b.name || '').toLowerCase());
            return a.docked ? -1 : 1;
        });

        localStorage.setItem('tabletConfig', JSON.stringify(config));
    }

    function syncAppsFromConfig() {
        const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
        if (!config.apps || config.apps.length === 0) return;

        const allAppItems = document.querySelectorAll('.app-icon, .dock-item');
        const itemMap = {};
        allAppItems.forEach(item => itemMap[item.getAttribute('data-id')] = item);

        const dockedApps = config.apps.filter(a => a.docked).sort((a, b) => (a.position || 0) - (b.position || 0));
        const drawerApps = config.apps.filter(a => !a.docked && a.id !== 'settings').sort((a, b) => (a.name || '').toLowerCase().localeCompare((b.name || '').toLowerCase()));

        // Helper to render icon
        const getIconHTML = (icon) => {
            if (!icon) return '🌐';
            if (icon.startsWith('data:image') || icon.includes('.') || icon.startsWith('http')) {
                return `<img src="${icon}" alt="icon">`;
            }
            return icon;
        };

        // Clear UI containers
        dock.innerHTML = '';
        drawerGrid.innerHTML = '';

        dockedApps.forEach(app => {
            const el = itemMap[app.id];
            if (el) {
                el.className = 'dock-item';
                el.setAttribute('data-id', app.id);
                el.setAttribute('data-name', app.name);
                el.setAttribute('data-url', app.url);
                el.setAttribute('data-icon', app.icon);
                el.setAttribute('data-original-icon', app.original_icon || app.icon || '🌐');

                el.innerHTML = getIconHTML(app.icon);
                dock.appendChild(el);
            }
        });

        drawerApps.forEach(app => {
            const el = itemMap[app.id];
            if (el) {
                el.className = 'app-icon thin dock-style';
                el.setAttribute('data-id', app.id);
                el.setAttribute('data-name', app.name);
                el.setAttribute('data-url', app.url);
                el.setAttribute('data-icon', app.icon);
                el.setAttribute('data-original-icon', app.original_icon || app.icon || '🌐');

                el.innerHTML = `<div class="icon-wrapper">${getIconHTML(app.icon)}</div><span class="app-label">${app.name}</span>`;
                drawerGrid.appendChild(el);
            }
        });

        // Ensure Settings App is always in the dock if it's missing
        if (!dock.querySelector('[data-id="settings"]')) {
            const settingsEl = itemMap['settings'] || document.querySelector('[data-id="settings"]');
            if (settingsEl) {
                settingsEl.className = 'dock-item';
                const iconVal = settingsEl.getAttribute('data-icon') || '⚙️';
                settingsEl.innerHTML = getIconHTML(iconVal);
                dock.appendChild(settingsEl);
            }
        }

        refreshDragEvents();
    }

    function refreshDragEvents() {
        document.querySelectorAll('.app-icon, .dock-item').forEach(item => {
            item.setAttribute('draggable', 'true');
            item.removeEventListener('dragstart', handleDragStart);
            item.removeEventListener('dragenter', handleDragEnter);
            item.removeEventListener('dragover', handleDragOver);
            item.removeEventListener('dragleave', handleDragLeave);
            item.removeEventListener('drop', handleDrop);
            item.removeEventListener('dragend', handleDragEnd);

            item.addEventListener('dragstart', handleDragStart);
            item.addEventListener('dragenter', handleDragEnter);
            item.addEventListener('dragover', handleDragOver);
            item.addEventListener('dragleave', handleDragLeave);
            item.addEventListener('drop', handleDrop);
            item.addEventListener('dragend', handleDragEnd);
        });
    }

    function initializeLocalStorage() {
        if (!localStorage.getItem('tabletConfig')) {
            saveCurrentConfig();
        }
    }

    // --- Time & Settings ---
    function updateTime() {
        const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
        const is12h = config.settings?.clock_format === '12h';
        const now = new Date();
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        let ampm = is12h ? (hours >= 12 ? ' PM' : ' AM') : '';
        if (is12h) { hours = hours % 12 || 12; } else { hours = String(hours).padStart(2, '0'); }
        clock.textContent = `${hours}:${minutes}${ampm}`;
        dateElement.textContent = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    }

    function applySettings(s) {
        if (!s) return;
        const wp = document.querySelector('.wallpaper');
        if (wp && s.wallpaper) wp.style.backgroundImage = `url('${s.wallpaper}')`;

        // Use CSS variables for real-time updates across all glass elements
        if (s.blur_amount) {
            document.documentElement.style.setProperty('--glass-blur', `blur(${s.blur_amount})`);
        }
        if (s.transparency !== undefined) {
            document.documentElement.style.setProperty('--glass-bg', `rgba(255, 255, 255, ${s.transparency})`);
            // Adjust border opacity to match
            document.documentElement.style.setProperty('--glass-border', `rgba(255, 255, 255, ${parseFloat(s.transparency) + 0.1})`);
        }
        updateTime();
    }

    function updateSetting(key, value) {
        const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
        if (!config.settings) config.settings = {};
        config.settings[key] = value;
        localStorage.setItem('tabletConfig', JSON.stringify(config));
        applySettings(config.settings);
    }

    function toggleSettings() {
        const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
        const s = config.settings || {};
        if (clockFormatSelect) clockFormatSelect.value = s.clock_format || '12h';
        if (wallpaperInput) wallpaperInput.value = s.wallpaper || '';
        if (blurInput) blurInput.value = parseInt(s.blur_amount) || 20;
        if (transparencyInput) transparencyInput.value = s.transparency || 0.1;
        if (hqFaviconsSelect) hqFaviconsSelect.value = s.hq_favicons || 'off';
        if (faviconSourceSelect) faviconSourceSelect.value = s.favicon_source || 'google';

        const isOpening = settingsModal.classList.contains('hidden');
        settingsModal.classList.toggle('hidden');

        if (isOpening) {
            document.body.classList.add('modal-open');
        } else {
            document.body.classList.remove('modal-open');
            saveCurrentConfig(); // Sync on close
        }
    }

    // --- Initialization ---
    setInterval(updateTime, 1000);
    updateTime();
    initializeLocalStorage();
    syncAppsFromConfig();
    const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
    if (config.settings) applySettings(config.settings);

    // --- Drawer Control ---
    window.addEventListener('wheel', (e) => {
        if (e.deltaY > 50 && !isDrawerOpen) openDrawer();
        else if (e.deltaY < -50 && isDrawerOpen && drawerGrid.scrollTop <= 0) closeDrawer();
    });

    window.addEventListener('touchstart', (e) => touchStartY = e.touches[0].clientY);
    window.addEventListener('touchend', (e) => {
        const diff = touchStartY - e.changedTouches[0].clientY;
        if (diff > 100 && !isDrawerOpen) openDrawer();
        else if (diff < -100 && isDrawerOpen && drawerGrid.scrollTop <= 0) closeDrawer();
    });

    function openDrawer() { screen.classList.add('drawer-open'); isDrawerOpen = true; }
    function closeDrawer() { screen.classList.remove('drawer-open'); isDrawerOpen = false; }

    // --- Search Logic ---
    const searchInput = document.querySelector('.drawer-search input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase().trim();

            // Fuzzy search regex: "ml" -> /m.*l/
            const fuzzyRegex = new RegExp(term.split('').join('.*'), 'i');

            document.querySelectorAll('.drawer-grid .app-icon').forEach(app => {
                const name = (app.getAttribute('data-name') || '').toLowerCase();
                const url = (app.getAttribute('data-url') || '').toLowerCase();

                if (fuzzyRegex.test(name) || fuzzyRegex.test(url)) {
                    app.style.display = 'flex';
                } else {
                    app.style.display = 'none';
                }
            });
        });
    }

    // --- Tooltip Logic ---
    const glassTooltip = document.getElementById('glass-tooltip');

    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('[data-name], .dock-item');
        if (target && !settingsModal.classList.contains('hidden')) return; // Disable when modal open

        if (target) {
            const name = target.getAttribute('data-name');
            const url = target.getAttribute('data-url');
            if (name) {
                glassTooltip.textContent = url && url !== '#' ? `${name}\n${url}` : name;
                glassTooltip.classList.remove('hidden');
                setTimeout(() => glassTooltip.classList.add('visible'), 10);

                // Position tooltip
                const rect = target.getBoundingClientRect();
                glassTooltip.style.left = `${rect.left + rect.width / 2}px`;
                glassTooltip.style.top = `${rect.top}px`;
            }
        }
    });

    document.addEventListener('mouseout', (e) => {
        if (e.target.closest('[data-name], .dock-item')) {
            glassTooltip.classList.remove('visible');
            setTimeout(() => {
                if (!glassTooltip.classList.contains('visible')) {
                    glassTooltip.classList.add('hidden');
                }
            }, 200);
        }
    });

    // --- Events & Navigation ---
    document.addEventListener('click', (e) => {
        const app = e.target.closest('.app-icon, .dock-item');
        if (app) {
            const id = app.getAttribute('data-id');
            if (id === 'settings') { toggleSettings(); return; }
            const url = app.getAttribute('data-url');
            if (url && url !== '#') window.open(url, '_blank');
        }
    });

    closeSettings.addEventListener('click', toggleSettings);
    if (clockFormatSelect) clockFormatSelect.addEventListener('change', (e) => updateSetting('clock_format', e.target.value));
    if (wallpaperInput) wallpaperInput.addEventListener('change', (e) => updateSetting('wallpaper', e.target.value));
    if (blurInput) blurInput.addEventListener('input', (e) => updateSetting('blur_amount', `${e.target.value}px`));
    if (transparencyInput) transparencyInput.addEventListener('input', (e) => updateSetting('transparency', parseFloat(e.target.value)));

    if (addAppBtn) {
        addAppBtn.addEventListener('click', () => {
            const name = newAppName.value.trim();
            const url = newAppUrl.value.trim();
            const icon = newAppIcon.value.trim() || '🔗';

            if (!name || !url) { alert('Please enter both Name and URL'); return; }
            const id = name.toLowerCase().replace(/[^a-z0-9]/g, '').substring(0, 15) + Math.random().toString(36).substr(2, 4);
            const newAppEl = document.createElement('div');
            newAppEl.className = 'app-icon thin dock-style';
            newAppEl.setAttribute('data-id', id);
            newAppEl.setAttribute('data-name', name);
            newAppEl.setAttribute('data-url', url);
            newAppEl.setAttribute('data-icon', icon);
            newAppEl.setAttribute('data-original-icon', icon);

            newAppEl.innerHTML = `<div class="icon-wrapper">${icon}</div><span class="app-label">${name}</span>`;
            drawerGrid.appendChild(newAppEl);
            saveCurrentConfig();
            newAppName.value = ''; newAppUrl.value = ''; newAppIcon.value = '';
            location.reload();
        });
    }

    // --- Drag & Drop ---
    function handleDragStart(e) { this.classList.add('dragging'); dragSrcEl = this; e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('data-id', this.getAttribute('data-id')); }
    function handleDragEnter(e) { this.classList.add('over'); }
    function handleDragLeave(e) { this.classList.remove('over'); }
    function handleDragOver(e) { if (e.preventDefault) e.preventDefault(); e.dataTransfer.dropEffect = 'move'; return false; }
    function handleDrop(e) {
        if (e.stopPropagation) e.stopPropagation();
        if (dragSrcEl !== this) {
            const sourceId = dragSrcEl.getAttribute('data-id');
            const targetId = this.getAttribute('data-id');
            const sourceHtml = dragSrcEl.innerHTML;
            const sourceName = dragSrcEl.getAttribute('data-name');
            const sourceUrl = dragSrcEl.getAttribute('data-url');
            dragSrcEl.innerHTML = this.innerHTML;
            dragSrcEl.setAttribute('data-id', targetId);
            dragSrcEl.setAttribute('data-name', this.getAttribute('data-name'));
            dragSrcEl.setAttribute('data-url', this.getAttribute('data-url'));
            this.innerHTML = sourceHtml;
            this.setAttribute('data-id', sourceId);
            this.setAttribute('data-name', sourceName);
            this.setAttribute('data-url', sourceUrl);
            saveCurrentConfig();
        }
        return false;
    }
    function handleDragEnd(e) { this.classList.remove('dragging'); document.querySelectorAll('.dock-item').forEach(item => item.classList.remove('over')); }

    // --- Dock Hover Effect ---
    dock.addEventListener('mousemove', (e) => {
        const rect = dock.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        document.querySelectorAll('.dock-item').forEach(item => {
            const itemRect = item.getBoundingClientRect();
            const itemX = itemRect.left + itemRect.width / 2 - rect.left;
            const distance = Math.abs(mouseX - itemX);
            const scale = distance < 150 ? 1 + 0.5 * (1 - distance / 150) : 1;
            item.style.transform = `scale(${scale})`;
            item.style.margin = `0 ${5 * (scale - 1)}px`;
        });
    });
    dock.addEventListener('mouseleave', () => document.querySelectorAll('.dock-item').forEach(item => { item.style.transform = 'scale(1)'; item.style.margin = '0'; }));

    // --- Context Menu (Pin/Unpin) ---
    document.addEventListener('contextmenu', (e) => {
        const app = e.target.closest('.app-icon, .dock-item');
        if (app) {
            e.preventDefault();
            contextApp = app;
            const isDocked = app.classList.contains('dock-item');
            menuPin.style.display = isDocked ? 'none' : 'flex';
            menuUnpin.style.display = isDocked ? 'flex' : 'none';
            contextMenu.style.display = 'block';
            contextMenu.style.left = `${e.clientX}px`;
            contextMenu.style.top = `${e.clientY}px`;
        } else {
            contextMenu.style.display = 'none';
        }
    });

    document.addEventListener('click', () => contextMenu.style.display = 'none');

    menuPin.addEventListener('click', () => {
        if (!contextApp) return;
        contextApp.className = 'dock-item';
        const wrapper = contextApp.querySelector('.icon-wrapper');
        if (wrapper) {
            contextApp.innerHTML = wrapper.innerHTML;
        }
        dock.appendChild(contextApp);
        saveCurrentConfig();
        refreshDragEvents();
    });

    menuUnpin.addEventListener('click', () => {
        if (!contextApp) return;
        contextApp.className = 'app-icon thin dock-style';
        const name = contextApp.getAttribute('data-name');
        const iconContent = contextApp.innerHTML;
        contextApp.innerHTML = `<div class="icon-wrapper">${iconContent}</div><span class="app-label">${name}</span>`;
        drawerGrid.appendChild(contextApp);
        saveCurrentConfig();
        location.reload();
    });

    menuDelete.addEventListener('click', () => {
        if (!contextApp) return;
        if (confirm(`Are you sure you want to delete ${contextApp.getAttribute('data-name')}?`)) {
            contextApp.remove();
            saveCurrentConfig();
            location.reload();
        }
    });

    menuSrcReset.addEventListener('click', () => {
        if (!contextApp) return;
        const originalIcon = contextApp.getAttribute('data-original-icon') || '🌐';
        contextApp.setAttribute('data-icon', originalIcon);
        saveCurrentConfig();
        location.reload();
    });

    const openFaviconPicker = () => {
        if (!contextApp) return;
        const url = contextApp.getAttribute('data-url');
        const name = contextApp.getAttribute('data-name');
        if (!url || url === '#') { alert('Cannot fetch favicons for this app.'); return; }

        faviconModalAppName.textContent = name;
        faviconModal.classList.remove('hidden');
        faviconGrid.innerHTML = '<div class="loading-spinner">Fetching icons...</div>';

        const domain = (new URL(url)).hostname;
        const sources = [
            { name: 'Google', url: `https://www.google.com/s2/favicons?domain=${domain}&sz=128` },
            { name: 'DuckDuckGo', url: `https://icons.duckduckgo.com/ip3/${domain}.ico` },
            { name: 'Favicon Horse', url: `https://favicon.horse/icon/${domain}` },
            { name: 'Unavatar', url: `https://unavatar.io/${domain}` }
        ];

        faviconGrid.innerHTML = '';
        sources.forEach(src => {
            const div = document.createElement('div');
            div.className = 'favicon-option glass';
            div.innerHTML = `<img src="${src.url}" alt="${src.name}"><span>${src.name}</span>`;
            div.onclick = () => {
                contextApp.setAttribute('data-icon', src.url);
                saveCurrentConfig();
                faviconModal.classList.add('hidden');
                location.reload();
            };
            faviconGrid.appendChild(div);
        });
    };

    menuChooseFavicon.addEventListener('click', openFaviconPicker);
    closeFaviconModal.addEventListener('click', () => faviconModal.classList.add('hidden'));

    // --- Clock Dragging ---
    const draggableClock = document.getElementById('draggable-clock');
    let isDraggingClock = false;
    let clockOffset = { x: 0, y: 0 };
    if (draggableClock) {
        draggableClock.addEventListener('mousedown', (e) => {
            isDraggingClock = true;
            clockOffset.x = e.clientX - draggableClock.offsetLeft;
            clockOffset.y = e.clientY - draggableClock.offsetTop;
            draggableClock.style.cursor = 'grabbing';
        });
        document.addEventListener('mousemove', (e) => {
            if (!isDraggingClock) return;
            let newX = Math.max(50, Math.min(window.innerWidth - 50, e.clientX - clockOffset.x));
            let newY = Math.max(50, Math.min(window.innerHeight - 50, e.clientY - clockOffset.y));
            draggableClock.style.left = `${newX}px`;
            draggableClock.style.top = `${newY}px`;
            draggableClock.style.transform = 'translate(-50%, -50%)';
        });
        document.addEventListener('mouseup', () => {
            if (isDraggingClock) {
                isDraggingClock = false;
                draggableClock.style.cursor = 'grab';
                saveCurrentConfig();
            }
        });
    }

    // --- Import/Export ---
    exportBtn.addEventListener('click', () => {
        saveCurrentConfig(); // Ensure latest state is captured
        const config = JSON.parse(localStorage.getItem('tabletConfig') || '{}');
        const blob = new Blob([JSON.stringify(config, null, 4)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = 'tablet-config.json'; a.click();
        URL.revokeObjectURL(url);
    });

    const importBookmarksInput = document.getElementById('import-bookmarks');
    if (importBookmarksInput) {
        importBookmarksInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(event.target.result, 'text/html');
                const links = Array.from(doc.querySelectorAll('a')).map((link, index) => ({
                    id: link.textContent.trim().toLowerCase().replace(/[^a-z0-9]/g, '').substring(0, 15) || `app_${index}`,
                    name: link.textContent.trim(),
                    url: link.getAttribute('href'),
                    icon: link.getAttribute('icon') || '🌐',
                    docked: false
                }));
                const config = JSON.parse(localStorage.getItem('tabletConfig') || '{"apps": [], "settings": {}}');
                const existingIds = config.apps.map(a => a.id);
                const newApps = links.filter(app => !existingIds.includes(app.id));
                config.apps = [...config.apps, ...newApps];
                localStorage.setItem('tabletConfig', JSON.stringify(config));
                alert(`Imported ${newApps.length} new apps!`);
                location.reload();
            };
            reader.readAsText(file);
        });
    }

    if (importInput) {
        importInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                localStorage.setItem('tabletConfig', event.target.result);
                location.reload();
            };
            reader.readAsText(file);
        });
    }
});
