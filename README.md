# Hospital Emergency Patient Queue Management System

A web-based emergency-room queue built on core data structures.
Backend: Python (standard library only). Front end: HTML, CSS and JavaScript.

## How to run

1. Install Python 3.8 or newer (no other installs needed).
2. Clone the repository and open its folder:

       git clone https://github.com/<your-username>/hospital-emergency-queue.git
       cd hospital-emergency-queue

3. Start the server:

       python server.py

4. The browser opens at http://localhost:8000. Stop the server with Ctrl+C.

A console-only version is also included: `python hospital_queue.py`

## Project structure

    hospital-emergency-queue/
    |-- hospital_queue.py   Data structures + system logic (+ console version)
    |-- server.py           JSON API and static file server
    |-- LICENSE             MIT license
    `-- static/
        `-- index.html      Front end (dashboard)

## DSA concepts and where they are used

| Concept | Where |
|---|---|
| Min-heap priority queue | `PriorityQueue` class: waiting patients ordered by (priority, arrival order) |
| Hash map | `records` (ID -> patient), `name_index` (name -> IDs), heap position map for O(log n) removal |
| Singly linked list | `LinkedList` class: history of seen/removed patients |
| Queue (FIFO) | `Queue` class: recent-activity log |
| Sorting | `merge_sort`: waiting list display and history sorted by longest wait |

## Complexity

| Operation | Time |
|---|---|
| Register patient (heap insert) | O(log n) |
| Call next patient (extract min) | O(log n) |
| See next patient (peek) | O(1) |
| Remove / change priority of any patient | O(log n) |
| Search by ID | O(1) average |
| Display sorted queue (merge sort) | O(n log n) |
| Add to history (tail pointer) | O(1) |

## Features

- Register patients with a priority from 1 (Critical) to 5 (Non-urgent)
- Queue arranges itself automatically; ties are served first-come-first-served
- "Next patient" panel with a live waiting timer and a Call patient button
- Remove a patient or change their priority at any time
- Search records by ID or (partial) name
- Waiting history with average wait, sortable by longest wait
- Heap structure view (tree and array) to show how the heap works
- Recent activity log

## API (used by the front end)

| Method | Path | Purpose |
|---|---|---|
| GET | /api/state | Queue, next patient, heap, history, stats, activity |
| POST | /api/register | Register a patient |
| POST | /api/attend | Call the next patient |
| POST | /api/cancel | Remove a patient from the queue |
| POST | /api/priority | Change a waiting patient's priority |
| GET | /api/search?q= | Search by ID or name |
| POST | /api/sample | Load sample patients |
| POST | /api/reset | Clear all data |

## Possible viva questions

- Why a heap and not a sorted list? Insert is O(log n) instead of O(n).
- How are equal priorities handled? The heap key is (priority, arrival sequence).
- Why is the queue merge-sorted for display? A heap only guarantees the root is smallest.
- How does removal from the middle work? The position map finds the index in O(1), then sift-up/sift-down restores the heap.
- Limitation: data is kept in memory, so it resets when the server stops.
