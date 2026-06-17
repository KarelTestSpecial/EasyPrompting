// Easy Prompting — background service worker.
// The toolbar button toggles a small, always-available popup window that holds
// your prompt drafts. A window (not a popup attached to the toolbar) is
// deliberate: it stays open next to your AI chat while you type and copy, so a
// stray click never makes it disappear.

const PAD_PAGE = "pad.html";

async function findPadWindow() {
    const windows = await chrome.windows.getAll({ populate: true });
    const padUrl = chrome.runtime.getURL(PAD_PAGE);
    for (const win of windows) {
        if (win.tabs && win.tabs.some(tab => tab.url === padUrl)) {
            return win;
        }
    }
    return null;
}

async function createPadWindow() {
    const defaultWidth = 380;
    const defaultHeight = 460;
    const { windowWidth, windowHeight } = await chrome.storage.local.get({
        windowWidth: defaultWidth,
        windowHeight: defaultHeight
    });

    let left, top;
    try {
        const displays = await chrome.system.display.getInfo();
        const primary = displays.find(d => d.isPrimary) || displays[0];
        if (primary) {
            left = Math.max(0, primary.bounds.width - windowWidth - 20);
            top = Math.max(0, primary.bounds.height - windowHeight - 20);
        }
    } catch (e) {
        // system.display not available — let the browser place the window.
    }

    try {
        return await chrome.windows.create({
            url: chrome.runtime.getURL(PAD_PAGE),
            type: "popup",
            width: windowWidth,
            height: windowHeight,
            left,
            top,
            focused: true
        });
    } catch (e) {
        return null;
    }
}

chrome.action.onClicked.addListener(async () => {
    const existing = await findPadWindow();
    if (existing) {
        try {
            await chrome.windows.remove(existing.id);
        } catch (e) {
            // Window was already gone — ignore.
        }
    } else {
        await createPadWindow();
    }
});

// Remember the window size the user picks, so it reopens the same size.
chrome.windows.onBoundsChanged.addListener(async (win) => {
    const padWin = await findPadWindow();
    if (padWin && padWin.id === win.id && win.width && win.height) {
        chrome.storage.local.set({ windowWidth: win.width, windowHeight: win.height });
    }
});
