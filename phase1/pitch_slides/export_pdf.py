import os
import sys
import json
import time
import base64
import socket
import asyncio
import subprocess
import urllib.request
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def start_http_server(directory, port):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    server = HTTPServer(('127.0.0.1', port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

async def export_pdf(output_path=None):
    chrome_path = None
    for p in CHROME_PATHS:
        if os.path.exists(p):
            chrome_path = p
            break
    
    if not chrome_path:
        print("Error: No Chrome or Edge browser found.")
        sys.exit(1)

    print(f"Using browser: {chrome_path}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    http_port = find_free_port()
    server = start_http_server(current_dir, http_port)
    print(f"HTTP Server started on http://127.0.0.1:{http_port}")

    cdp_port = find_free_port()
    user_data_dir = os.path.join(current_dir, ".chrome_pdf_profile")
    
    cmd = [
        chrome_path,
        "--headless=new",
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={user_data_dir}",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--allow-file-access-from-files",
        "--enable-logging",
        "about:blank"
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        # Wait for CDP endpoint
        page_ws_url = None
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json/list", timeout=1) as resp:
                    pages = json.loads(resp.read().decode())
                    for page in pages:
                        if page.get("type") == "page" and page.get("webSocketDebuggerUrl"):
                            page_ws_url = page.get("webSocketDebuggerUrl")
                            break
                    if page_ws_url:
                        break
            except Exception:
                await asyncio.sleep(0.3)

        if not page_ws_url:
            print("Failed to find target page CDP endpoint.")
            sys.exit(1)

        print(f"Connected to Page CDP endpoint: {page_ws_url}")

        async with websockets.connect(page_ws_url, max_size=100_000_000) as ws:
            msg_id = 0
            
            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method}
                if params:
                    payload["params"] = params
                await ws.send(json.dumps(payload))
                while True:
                    res = json.loads(await ws.recv())
                    if res.get("id") == payload["id"]:
                        return res.get("result", {})

            # Enable Page
            await send_cmd("Page.enable")
            await send_cmd("DOM.enable")

            target_url = f"http://127.0.0.1:{http_port}/index.html"
            print(f"Navigating to {target_url}...")
            await send_cmd("Page.navigate", {"url": target_url})

            # Wait for load event
            await asyncio.sleep(2.0)

            # Wait for document.fonts.ready and images
            await send_cmd("Runtime.evaluate", {
                "expression": "document.fonts.ready.then(() => Promise.all(Array.from(document.images).map(img => img.complete ? null : new Promise(res => img.onload = res))))",
                "awaitPromise": True
            })
            await asyncio.sleep(1.0)

            print("Generating PDF with Page.printToPDF...")
            # 1280px by 720px at 96 DPI: 13.333333 in x 7.5 in
            pdf_result = await send_cmd("Page.printToPDF", {
                "landscape": True,
                "displayHeaderFooter": False,
                "printBackground": True,
                "preferCSSPageSize": True,
                "paperWidth": 13.333333,
                "paperHeight": 7.5,
                "marginTop": 0,
                "marginBottom": 0,
                "marginLeft": 0,
                "marginRight": 0,
                "generateTaggedPDF": True,
                "transferMode": "ReturnAsBase64"
            })

            pdf_data = base64.b64decode(pdf_result["data"])
            if not output_path:
                output_path = os.path.join(current_dir, "DATA_WHERE_HOUSE_Pitch_Slides.pdf")
            with open(output_path, "wb") as f:
                f.write(pdf_data)

            print(f"Successfully exported PDF to: {output_path} ({len(pdf_data):,} bytes)")

    finally:
        proc.terminate()
        server.shutdown()
        # Clean up temp profile
        try:
            import shutil
            if os.path.exists(user_data_dir):
                shutil.rmtree(user_data_dir, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(export_pdf())
