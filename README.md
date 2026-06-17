# Easy Prompting

A safe scratchpad for AI chat prompts. Draft in an open window, never lose a
prompt to a stray **Enter** or **Ctrl+C**, then copy it. Nothing is ever sent from this
window — Enter just makes a new line.

A Manifest V3 Chrome extension.

## Repository layout

| Path | What |
|---|---|
| `easyprompting/` | The unpacked extension (load this folder via `chrome://extensions` → *Load unpacked*) |
| `easyprompting/LEGAL/PRIVACY.md` | Privacy policy |
| `easyprompting-1.0.zip` | Packaged build, ready for the Chrome Web Store |
| `promo/` | Store promo assets + `make_promo.py` generator |
| `STORE_LISTING.md` | Chrome Web Store listing copy |

## Features

- **Enter never sends** — a calm window where nothing is transmitted.
- **Autosave** — every keystroke is stored locally.
- **Multiple tabs** — keep a system prompt, a draft and snippets side by side.
- **One-click copy**, live word/character counter, adjustable text size.
- **Keyboard tab navigation**: `Alt+E` / `Alt+R`, `Alt+1…9`, `Alt+←/→`, `Ctrl+[ / ]`.
- **100% local & private** — no accounts, no tracking, no network requests.

## Privacy

Everything is stored on your device via `chrome.storage`. See
[`easyprompting/LEGAL/PRIVACY.md`](easyprompting/LEGAL/PRIVACY.md).

## Related

Need a clock, alarms, a screensaver and a richer research notepad too? See the
companion extension **Very Practical Clock & Notepad**.

## License

MIT — see [`easyprompting/LEGAL/LICENSE`](easyprompting/LEGAL/LICENSE).
