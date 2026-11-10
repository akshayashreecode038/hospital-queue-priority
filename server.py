"""
Web server for the Hospital Emergency Patient Queue Management System.

Uses only the Python standard library (no pip install needed).
The data structures (heap, linked list, hash maps, queue, merge sort)
live in hospital_queue.py; this file exposes them as a small JSON API
and serves the front end in /static.

Run:  python server.py        then open http://localhost:8000
"""

import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from hospital_queue import HospitalQueueSystem

HOST, PORT = "127.0.0.1", 8000
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

SHORT_LABELS = {1: "Critical", 2: "Emergent", 3: "Urgent", 4: "Less urgent", 5: "Non-urgent"}

LOCK = threading.Lock()
SYSTEM = HospitalQueueSystem()

SAMPLE_PATIENTS = [
    ("Ravi Kumar", 54, "Chest pain", 1),
    ("Anita Sharma", 29, "Fractured arm", 3),
    ("Mohammed Ali", 8, "High fever", 2),
    ("Priya Nair", 35, "Minor cut", 5),
    ("John Peter", 62, "Breathing difficulty", 1),
    ("Sneha Reddy", 24, "Sprained ankle", 4),
]


def patient_json(p):
    end = p.attended_time or None
    return {
        "pid": p.pid,
        "name": p.name,
        "age": p.age,
        "condition": p.condition,
        "priority": p.priority,
        "label": SHORT_LABELS[p.priority],
        "status": p.status,
        "arrived": p.arrival_time.strftime("%H:%M:%S"),
        "attended": end.strftime("%H:%M:%S") if end else None,
        "wait_seconds": round(p.wait_minutes() * 60, 1),
    }


def build_state(history_sort):
    s = SYSTEM
    waiting = s.waiting_sorted()                       # merge sort over heap copy
    history = s.history_sorted_by_wait() if history_sort == "wait" else s.history.to_list()
    done = [p for p in s.history.to_list() if p.status == "COMPLETED"]
    left = [p for p in s.history.to_list() if p.status == "LEFT"]
    by_priority = {k: 0 for k in SHORT_LABELS}
    for p in waiting:
        by_priority[p.priority] += 1
    avg = (sum(p.wait_minutes() for p in s.history.to_list()) * 60 / len(s.history)) if len(s.history) else 0
    nxt = s.next_patient()
    return {
        "waiting": [patient_json(p) for p in waiting],
        "next": patient_json(nxt) if nxt else None,
        "heap": [{"pid": p.pid, "name": p.name, "priority": p.priority} for p in s.queue.heap],
        "history": [patient_json(p) for p in history],
        "activity": s.activity.to_list(),
        "stats": {
            "waiting": len(waiting),
            "completed": len(done),
            "left": len(left),
            "total": len(s.records),
            "avg_wait_seconds": round(avg, 1),
            "by_priority": by_priority,
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):          # quieter console
        pass

    # ---- helpers ---------------------------------------------------------
    def _json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, message, status=400):
        self._json({"error": message}, status)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    # ---- GET -------------------------------------------------------------
    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if url.path in ("/", "/index.html"):
            return self._serve_file("index.html", "text/html; charset=utf-8")

        if url.path == "/api/state":
            sort = (query.get("history_sort") or ["order"])[0]
            with LOCK:
                return self._json(build_state(sort))

        if url.path == "/api/search":
            q = (query.get("q") or [""])[0].strip()
            if not q:
                return self._json({"results": []})
            with LOCK:
                hit = SYSTEM.search_by_id(q)                  # hash map, O(1)
                results = [hit] if hit else SYSTEM.search_by_name(q)
                return self._json({"results": [patient_json(p) for p in results]})

        self._error("Not found", 404)

    def _serve_file(self, name, content_type):
        path = os.path.join(STATIC_DIR, name)
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError:
            return self._error("File not found", 404)
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---- POST ------------------------------------------------------------
    def do_POST(self):
        global SYSTEM
        path = urlparse(self.path).path
        data = self._body()
        if data is None:
            return self._error("Invalid JSON")

        with LOCK:
            if path == "/api/register":
                name = str(data.get("name", "")).strip()
                condition = str(data.get("condition", "")).strip() or "Not specified"
                try:
                    age = int(data.get("age"))
                    priority = int(data.get("priority"))
                except (TypeError, ValueError):
                    return self._error("Age and priority must be numbers.")
                if not name:
                    return self._error("Enter the patient's name.")
                if not 0 <= age <= 120:
                    return self._error("Age must be between 0 and 120.")
                if priority not in SHORT_LABELS:
                    return self._error("Priority must be between 1 and 5.")
                p = SYSTEM.register(name[:60], age, condition[:80], priority)
                return self._json({"patient": patient_json(p)})

            if path == "/api/attend":
                p = SYSTEM.attend_next()
                if not p:
                    return self._error("The queue is empty.")
                return self._json({"patient": patient_json(p)})

            if path == "/api/cancel":
                p = SYSTEM.cancel(str(data.get("pid", "")).upper())
                if not p:
                    return self._error("Patient is not in the waiting queue.", 404)
                return self._json({"patient": patient_json(p)})

            if path == "/api/priority":
                try:
                    priority = int(data.get("priority"))
                except (TypeError, ValueError):
                    return self._error("Priority must be a number.")
                if not SYSTEM.change_priority(str(data.get("pid", "")).upper(), priority):
                    return self._error("Patient is not in the waiting queue.", 404)
                return self._json({"ok": True})

            if path == "/api/sample":
                for s in SAMPLE_PATIENTS:
                    SYSTEM.register(*s)
                return self._json({"ok": True})

            if path == "/api/reset":
                SYSTEM = HospitalQueueSystem()
                return self._json({"ok": True})

        self._error("Not found", 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"Hospital Emergency Queue running at {url}  (Ctrl+C to stop)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
