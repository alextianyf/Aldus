# Aldus — TODOs

## Current Status

Phase 1 and Phase 2 are complete. The core pipeline and basic UI are working.

---

## Phase 3 — Configuration UI

### Banner Editor
- [ ] UI panel to enter ASCII art lines and preview the rendered banner PNG
- [ ] Upload a custom banner image (PNG/JPG) from the UI
- [ ] When a file is loaded, detect if it has an existing banner and prompt the user:
      - "Use existing banner / Replace it / Remove it"
- [ ] When no banner is detected, prompt: "No banner found — want to add one?"
- [ ] Save banner choice (lines or image path) to `config.json`
- [ ] Banner persists and auto-applies to future conversions

### More Themes
- [ ] Add at least 2-3 more themes (e.g. dark, minimal, warm)
- [ ] Each theme is a separate CSS file in `backend/themes/`
- [ ] Theme selector in UI updates live preview when switched

### Footer Config
- [ ] UI field to set the footer format
- [ ] Author name already configurable — make sure it saves and persists correctly
- [ ] Option to toggle footer on/off

---

## Phase 4 — Polish

### UX
- [ ] Loading spinner / progress bar during conversion
- [ ] Folder conversion: show "Converting 3 / 12 files..." live progress (needs WebSocket or SSE)
- [ ] Clearer error messages with actionable hints
- [ ] Drag and drop file/folder onto the UI instead of typing the path
- [ ] "Open PDF" button after conversion to open the file in system viewer
- [ ] "Open folder" button to reveal the output PDF in file explorer

### Stability
- [ ] Handle markdown files with no H1 heading gracefully (footer should not break)
- [ ] Handle missing `images/` folder gracefully (no crash if folder doesn't exist)
- [ ] Timeout handling if Puppeteer takes too long
- [ ] Validate file path input before sending to backend

---

## Phase 5 — Tauri Desktop App

- [ ] Install Tauri CLI and set up `src-tauri/`
- [ ] Replace browser file path input with native OS file/folder picker dialog
- [ ] Bundle backend (Python + Node.js) with the app — research options:
      - Option A: Ship Python as a sidecar process
      - Option B: Rewrite backend logic in Rust (longer term)
- [ ] Package as Windows installer (.msi or .exe)
- [ ] Test on Windows 11
- [ ] Mac/Linux support (later)

---

## Future / Backlog

- [ ] Migrate existing study guide markdown files from backtick math to LaTeX notation
- [ ] Custom theme builder in UI (color pickers, font size, etc.)
- [ ] Export to HTML in addition to PDF
- [ ] Multi-file view — show all converted PDFs in a list with re-convert buttons
- [ ] User accounts + cloud storage for the web version
- [ ] Public web deployment
