"""
main.py
FastAPI backend for Aldus.
"""

import os
import json
import glob
import subprocess
import sys
from pathlib import Path
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from converter import convert, build_html

app = FastAPI(title='Aldus', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

DEFAULT_CONFIG = {
    'author': 'Alex Tian',
    'theme': 'default',
    'banner_lines': [],
    'banner_image_path': '',
}

def load_config() -> dict:
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(data: dict):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


# ── Request models ────────────────────────────────────────────────────────────
class ConvertRequest(BaseModel):
    file_path: str
    theme: str | None = None
    author: str | None = None
    banner_lines: list[str] | None = None
    banner_image_path: str | None = None
    include_footer: bool = True

class ConvertFolderRequest(BaseModel):
    folder_path: str
    theme: str | None = None
    author: str | None = None
    banner_lines: list[str] | None = None
    banner_image_path: str | None = None
    include_footer: bool = True

class ConfigModel(BaseModel):
    author: str | None = None
    theme: str | None = None
    banner_lines: list[str] | None = None
    banner_image_path: str | None = None


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/config')
def get_config():
    return load_config()


@app.post('/config')
def update_config(body: ConfigModel):
    config = load_config()
    if body.author is not None:
        config['author'] = body.author
    if body.theme is not None:
        config['theme'] = body.theme
    if body.banner_lines is not None:
        config['banner_lines'] = body.banner_lines
    if body.banner_image_path is not None:
        config['banner_image_path'] = body.banner_image_path
    save_config(config)
    return config


@app.get('/themes')
def get_themes():
    themes_dir = os.path.join(os.path.dirname(__file__), 'themes')
    themes = [
        Path(f).stem
        for f in glob.glob(os.path.join(themes_dir, '*.css'))
    ]
    return {'themes': sorted(themes)}


@app.post('/convert')
def convert_file(body: ConvertRequest):
    if not os.path.isfile(body.file_path):
        raise HTTPException(status_code=404, detail=f'File not found: {body.file_path}')

    config = load_config()
    try:
        pdf_path = convert(
            md_path=body.file_path,
            theme=body.theme or config['theme'],
            banner_lines=body.banner_lines or config['banner_lines'] or None,
            banner_image_path=body.banner_image_path or config['banner_image_path'] or None,
            author=body.author or config['author'],
            include_footer=body.include_footer,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {'pdf_path': pdf_path}


@app.post('/convert-folder')
def convert_folder(body: ConvertFolderRequest):
    if not os.path.isdir(body.folder_path):
        raise HTTPException(status_code=404, detail=f'Folder not found: {body.folder_path}')

    md_files = glob.glob(
        os.path.join(body.folder_path, '**', '*.md'),
        recursive=True
    )

    if not md_files:
        raise HTTPException(status_code=404, detail='No markdown files found in folder')

    config = load_config()
    results = []

    for md_file in md_files:
        try:
            pdf_path = convert(
                md_path=md_file,
                theme=body.theme or config['theme'],
                banner_lines=body.banner_lines or config['banner_lines'] or None,
                banner_image_path=body.banner_image_path or config['banner_image_path'] or None,
                author=body.author or config['author'],
                include_footer=body.include_footer,
            )
            results.append({'file': md_file, 'pdf': pdf_path, 'status': 'ok'})
        except Exception as e:
            results.append({'file': md_file, 'pdf': None, 'status': 'error', 'error': str(e)})

    return {
        'total': len(md_files),
        'success': sum(1 for r in results if r['status'] == 'ok'),
        'failed': sum(1 for r in results if r['status'] == 'error'),
        'results': results,
    }


@app.get('/pick-file')
def pick_file():
    """Open a native OS file picker and return the selected path."""
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    path = filedialog.askopenfilename(
        title='Select a Markdown file',
        filetypes=[('Markdown files', '*.md'), ('All files', '*.*')]
    )
    root.destroy()
    return {'path': path or ''}


@app.get('/pick-folder')
def pick_folder():
    """Open a native OS folder picker and return the selected path."""
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    path = filedialog.askdirectory(title='Select a folder')
    root.destroy()
    return {'path': path or ''}


@app.post('/convert-upload')
async def convert_upload(
    file: UploadFile,
    theme: str = Form('default'),
    author: str = Form('Alex Tian'),
    include_footer: bool = Form(True),
    img_dir: str = Form(''),
):
    """Accept a .md file upload, convert to PDF, return the PDF directly."""
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail='Only .md files are supported')

    config = load_config()
    content = await file.read()

    with tempfile.NamedTemporaryFile(
        suffix='.md', delete=False, mode='wb',
        prefix=os.path.splitext(file.filename)[0] + '_'
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        pdf_path = convert(
            md_path=tmp_path,
            theme=theme or config['theme'],
            author=author or config['author'],
            include_footer=include_footer,
            img_dir=img_dir.strip() or None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return FileResponse(pdf_path, media_type='application/pdf', filename=file.filename.replace('.md', '.pdf'))


@app.get('/preview')
def preview_pdf(file_path: str):
    """Return a generated PDF file for preview."""
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail='PDF not found')
    return FileResponse(file_path, media_type='application/pdf')


@app.post('/open')
def open_file(body: dict):
    """Open a file in the system default application."""
    path = body.get('path', '')
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail='File not found')
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])
    return {'ok': True}


@app.post('/open-folder')
def open_folder(body: dict):
    """Reveal a file in the system file explorer."""
    path = body.get('path', '')
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail='File not found')
    if sys.platform == 'win32':
        subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', '-R', path])
    else:
        subprocess.Popen(['xdg-open', os.path.dirname(path)])
    return {'ok': True}
