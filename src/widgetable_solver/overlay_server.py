from __future__ import annotations

import argparse
import base64
import json
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from widgetable_solver.piggy_push.runner import (
    DEFAULT_GRID_HEIGHT,
    DEFAULT_GRID_WIDTH,
    analyze_image,
)


MAX_UPLOAD_BYTES = 12 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 10.0


class OverlayServerError(ValueError):
    pass


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Widgetable Overlay</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #eef7d4;
      color: #223018;
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr;
    }
    header {
      padding: 18px 24px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      border-bottom: 1px solid rgba(34, 48, 24, 0.14);
      background: rgba(255, 255, 255, 0.56);
      backdrop-filter: blur(12px);
    }
    h1 {
      margin: 0;
      font-size: 18px;
      line-height: 1.2;
      font-weight: 760;
    }
    main {
      display: grid;
      grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
      min-height: 0;
    }
    aside {
      padding: 20px;
      border-right: 1px solid rgba(34, 48, 24, 0.14);
      background: rgba(255, 255, 255, 0.34);
    }
    #dropzone {
      display: grid;
      place-items: center;
      min-height: 180px;
      padding: 20px;
      text-align: center;
      border: 2px dashed rgba(34, 48, 24, 0.28);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.48);
      cursor: pointer;
    }
    #dropzone.dragover {
      border-color: #ef4444;
      background: rgba(255, 255, 255, 0.78);
    }
    input[type="file"] {
      inline-size: 100%;
      margin-top: 16px;
    }
    .controls {
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }
    label {
      display: grid;
      gap: 4px;
      font-size: 12px;
      font-weight: 650;
    }
    select {
      min-height: 36px;
      padding: 6px 8px;
      border: 1px solid rgba(34, 48, 24, 0.2);
      border-radius: 6px;
      background: white;
      color: inherit;
      font: inherit;
    }
    button {
      min-height: 38px;
      border: 0;
      border-radius: 6px;
      background: #ef4444;
      color: white;
      font: inherit;
      font-weight: 750;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.5;
      cursor: wait;
    }
    #status {
      margin-top: 14px;
      min-height: 20px;
      font-size: 13px;
      color: #526143;
    }
    .viewer {
      min-width: 0;
      min-height: 0;
      padding: 18px;
      overflow: auto;
    }
    #overlay {
      display: none;
      max-width: 100%;
      height: auto;
      background: white;
      border: 1px solid rgba(34, 48, 24, 0.14);
      border-radius: 8px;
    }
    #empty {
      display: grid;
      place-items: center;
      min-height: 60vh;
      color: #68785a;
      text-align: center;
    }
    @media (max-width: 820px) {
      main {
        grid-template-columns: 1fr;
      }
      aside {
        border-right: 0;
        border-bottom: 1px solid rgba(34, 48, 24, 0.14);
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>Widgetable Overlay</h1>
    <span id="summary"></span>
  </header>
  <main>
    <aside>
      <div id="dropzone" tabindex="0">Paste, drop, or choose a screenshot</div>
      <input id="file" type="file" accept="image/*">
      <div class="controls">
        <label>Strategy
          <select id="strategy">
            <option value="fast" selected>fast</option>
            <option value="hybrid">hybrid</option>
            <option value="exact">exact</option>
          </select>
        </label>
        <label>
          <span><input id="debug" type="checkbox"> Raw detections</span>
        </label>
        <button id="rerun" disabled>Run Again</button>
      </div>
      <div id="status">Ready</div>
    </aside>
    <section class="viewer">
      <div id="empty">Overlay will appear here</div>
      <img id="overlay" alt="Solved overlay">
    </section>
  </main>
  <script>
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file");
    const overlay = document.getElementById("overlay");
    const empty = document.getElementById("empty");
    const status = document.getElementById("status");
    const summary = document.getElementById("summary");
    const rerun = document.getElementById("rerun");
    let lastDataUrl = null;

    function setStatus(text) {
      status.textContent = text;
    }

    function readFile(file) {
      if (!file || !file.type.startsWith("image/")) {
        setStatus("Use an image file");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => analyze(reader.result);
      reader.onerror = () => setStatus("Could not read image");
      reader.readAsDataURL(file);
    }

    async function analyze(dataUrl) {
      lastDataUrl = dataUrl;
      rerun.disabled = true;
      setStatus("Analyzing...");
      const payload = {
        image: dataUrl,
        strategy: document.getElementById("strategy").value,
        debug_detections: document.getElementById("debug").checked
      };
      try {
        const response = await fetch("/analyze", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error || "Analyze failed");
        }
        overlay.src = result.overlay;
        overlay.style.display = "block";
        empty.style.display = "none";
        summary.textContent = `${result.pig_count} pigs · ${result.move_count} moves`;
        setStatus("Ready");
      } catch (error) {
        setStatus(error.message);
      } finally {
        rerun.disabled = !lastDataUrl;
      }
    }

    document.addEventListener("paste", (event) => {
      const item = [...event.clipboardData.items].find(candidate => candidate.type.startsWith("image/"));
      if (item) readFile(item.getAsFile());
    });
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("dragover", (event) => {
      event.preventDefault();
      dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
    dropzone.addEventListener("drop", (event) => {
      event.preventDefault();
      dropzone.classList.remove("dragover");
      readFile(event.dataTransfer.files[0]);
    });
    fileInput.addEventListener("change", () => readFile(fileInput.files[0]));
    rerun.addEventListener("click", () => lastDataUrl && analyze(lastDataUrl));
  </script>
</body>
</html>
"""


def parse_image_data_url(value: str) -> bytes:
    prefix, separator, encoded = value.partition(",")
    if separator != "," or not prefix.startswith("data:image/") or ";base64" not in prefix:
        raise OverlayServerError("Expected an image data URL")
    try:
        data = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise OverlayServerError("Image data is not valid base64") from error
    if not data:
        raise OverlayServerError("Image data is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise OverlayServerError("Image is too large")
    return data


def analyze_image_bytes(
    image_bytes: bytes,
    *,
    strategy: str = "hybrid",
    grid_width: int = DEFAULT_GRID_WIDTH,
    grid_height: int = DEFAULT_GRID_HEIGHT,
    debug_detections: bool = False,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="widgetable-overlay-") as temp_dir:
        temp_path = Path(temp_dir)
        input_path = temp_path / "input.png"
        overlay_path = temp_path / "overlay.png"
        input_path.write_bytes(image_bytes)
        result = analyze_image(
            input_path,
            overlay=overlay_path,
            grid_width=grid_width,
            grid_height=grid_height,
            strategy=strategy,  # type: ignore[arg-type]
            debug_detections=debug_detections,
        )
        overlay_bytes = overlay_path.read_bytes()
    return {
        "overlay": "data:image/png;base64," + base64.b64encode(overlay_bytes).decode("ascii"),
        "pig_count": len(result.board.pigs),
        "detection_count": len(result.detections),
        "move_count": len(result.solution or ()),
        "solution": list(result.solution or ()),
    }


class OverlayRequestHandler(BaseHTTPRequestHandler):
    server_version = "WidgetableOverlay/0.1"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(REQUEST_TIMEOUT_SECONDS)

    def do_GET(self) -> None:
        if self.path not in {"/", "/index.html"}:
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        body = INDEX_HTML.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/analyze":
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > MAX_UPLOAD_BYTES * 2:
                raise OverlayServerError("Request body is too large")
            payload = json.loads(self.rfile.read(content_length))
            image_bytes = parse_image_data_url(str(payload.get("image", "")))
            response = analyze_image_bytes(
                image_bytes,
                strategy=str(payload.get("strategy", "hybrid")),
                grid_width=int(payload.get("grid_width", DEFAULT_GRID_WIDTH)),
                grid_height=int(payload.get("grid_height", DEFAULT_GRID_HEIGHT)),
                debug_detections=bool(payload.get("debug_detections", False)),
            )
        except (json.JSONDecodeError, OverlayServerError, ValueError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        except (TimeoutError, OSError):
            return
        self._send_json(response, HTTPStatus.OK)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class OverlayThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


def serve(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    server = OverlayThreadingHTTPServer((host, port), OverlayRequestHandler)
    print(f"Widgetable overlay server: http://{host}:{server.server_port}")
    server.serve_forever()
    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m widgetable_solver.overlay_server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    serve(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
