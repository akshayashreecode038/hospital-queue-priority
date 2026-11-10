"""
Hospital Emergency Patient Queue Management System
---------------------------------------------------
DSA concepts used (all implemented from scratch, no heapq / queue module):
  * Min-Heap Priority Queue  -> waiting patients, most critical first
  * Hash Map (dict)          -> O(1) lookup by patient ID, name index for search
  * Singly Linked List       -> history of completed patients
  * Queue (linked, FIFO)     -> recent activity log
  * Merge Sort               -> sorted queue display / history reports

Run:  python hospital_queue.py
"""

from datetime import datetime

# ----------------------------------------------------------------------------
# Priority levels (lower number = more urgent)
# ----------------------------------------------------------------------------
PRIORITY_LABELS = {
    1: "CRITICAL   (Resuscitation)",
    2: "EMERGENT   (Very urgent)",
    3: "URGENT",
    4: "LESS URGENT",
    5: "NON-URGENT",
}


# ----------------------------------------------------------------------------
# Step 1: Patient record structure
# ----------------------------------------------------------------------------
class Patient:
    def __init__(self, pid, name, age, condition, priority, seq):
        self.pid = pid
        self.name = name
        self.age = age
        self.condition = condition
        self.priority = priority
        self.seq = seq                      # arrival order, breaks priority ties (FIFO)
        self.arrival_time = datetime.now()
        self.attended_time = None
        self.status = "WAITING"

    def wait_minutes(self):
        end = self.attended_time or datetime.now()
        return (end - self.arrival_time).total_seconds() / 60

    def __repr__(self):
        return f"Patient({self.pid}, {self.name}, P{self.priority})"


# ----------------------------------------------------------------------------
# Step 3: Min-Heap based Priority Queue
# Order key = (priority, arrival seq). Keeps a position map so that any
# patient can be removed/updated in O(log n).
# ----------------------------------------------------------------------------
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.pos = {}                       # pid -> index in heap (hash map)

    @staticmethod
    def _key(p):
        return (p.priority, p.seq)

    def _less(self, i, j):
        return self._key(self.heap[i]) < self._key(self.heap[j])

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.pos[self.heap[i].pid] = i
        self.pos[self.heap[j].pid] = j

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._less(i, parent):
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.heap)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and self._less(left, smallest):
                smallest = left
            if right < n and self._less(right, smallest):
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    # Step 4: insert according to priority -------------------------------
    def push(self, patient):
        self.heap.append(patient)
        self.pos[patient.pid] = len(self.heap) - 1
        self._sift_up(len(self.heap) - 1)

    def peek(self):
        return self.heap[0] if self.heap else None

    def pop(self):
        if not self.heap:
            return None
        top = self.heap[0]
        self._remove_at(0)
        return top

    def _remove_at(self, i):
        last = len(self.heap) - 1
        removed = self.heap[i]
        if i != last:
            self._swap(i, last)
        self.heap.pop()
        del self.pos[removed.pid]
        if i < len(self.heap):
            self._sift_down(i)
            self._sift_up(i)
        return removed

    # Step 5: removal of an arbitrary patient (cancel / left without being seen)
    def remove(self, pid):
        if pid not in self.pos:
            return None
        return self._remove_at(self.pos[pid])

    def update_priority(self, pid, new_priority):
        if pid not in self.pos:
            return False
        i = self.pos[pid]
        self.heap[i].priority = new_priority
        self._sift_up(i)
        self._sift_down(self.pos[pid])
        return True

    def __len__(self):
        return len(self.heap)

    def items(self):
        return list(self.heap)


# ----------------------------------------------------------------------------
# Step 6: Linked list for history of completed patients
# ----------------------------------------------------------------------------
class _Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):                 # O(1) using tail pointer
        node = _Node(data)
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self.size += 1

    def to_list(self):
        out, cur = [], self.head
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out

    def __len__(self):
        return self.size


# ----------------------------------------------------------------------------
# FIFO Queue (linked) - used as a bounded recent-activity log
# ----------------------------------------------------------------------------
class Queue:
    def __init__(self, capacity=6):
        self.front = None
        self.rear = None
        self.size = 0
        self.capacity = capacity

    def enqueue(self, data):
        node = _Node(data)
        if self.rear:
            self.rear.next = node
        else:
            self.front = node
        self.rear = node
        self.size += 1
        if self.size > self.capacity:       # drop oldest
            self.dequeue()

    def dequeue(self):
        if not self.front:
            return None
        data = self.front.data
        self.front = self.front.next
        if not self.front:
            self.rear = None
        self.size -= 1
        return data

    def to_list(self):
        out, cur = [], self.front
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out


# ----------------------------------------------------------------------------
# Sorting: merge sort (stable, O(n log n))
# ----------------------------------------------------------------------------
def merge_sort(items, key):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# ----------------------------------------------------------------------------
# Hospital system tying everything together
# ----------------------------------------------------------------------------
class HospitalQueueSystem:
    def __init__(self):
        self.queue = PriorityQueue()        # waiting patients (heap)
        self.records = {}                   # pid -> Patient (hash map, all patients)
        self.name_index = {}                # lowercase name -> [pids] (hash map)
        self.history = LinkedList()         # completed patients (linked list)
        self.activity = Queue(capacity=6)   # recent events (FIFO queue)
        self._next_id = 1001
        self._seq = 0

    def _log(self, msg):
        self.activity.enqueue(f"[{datetime.now():%H:%M:%S}] {msg}")

    # Step 2: register + assign priority
    def register(self, name, age, condition, priority):
        if priority not in PRIORITY_LABELS:
            raise ValueError("Priority must be between 1 and 5")
        pid = f"P{self._next_id}"
        self._next_id += 1
        self._seq += 1
        p = Patient(pid, name, age, condition, priority, self._seq)
        self.records[pid] = p
        self.name_index.setdefault(name.lower(), []).append(pid)
        self.queue.push(p)
        self._log(f"Registered {p.name} ({pid}) - priority {priority}")
        return p

    def next_patient(self):
        return self.queue.peek()

    def attend_next(self):
        p = self.queue.pop()
        if not p:
            return None
        p.attended_time = datetime.now()
        p.status = "COMPLETED"
        self.history.append(p)
        self._log(f"Attended {p.name} ({p.pid})")
        return p

    def cancel(self, pid):
        p = self.queue.remove(pid)
        if p:
            p.status = "LEFT"
            p.attended_time = datetime.now()
            self.history.append(p)
            self._log(f"Removed {p.name} ({p.pid}) from queue")
        return p

    def change_priority(self, pid, new_priority):
        if new_priority not in PRIORITY_LABELS:
            return False
        ok = self.queue.update_priority(pid, new_priority)
        if ok:
            self._log(f"Priority of {pid} changed to {new_priority}")
        return ok

    # Search: by ID (O(1)) or by name (hash index, partial match fallback)
    def search_by_id(self, pid):
        return self.records.get(pid.upper())

    def search_by_name(self, name):
        name = name.lower().strip()
        if name in self.name_index:
            return [self.records[i] for i in self.name_index[name]]
        results = []
        for key, pids in self.name_index.items():
            if name in key:
                results.extend(self.records[i] for i in pids)
        return results

    def waiting_sorted(self):
        """Heap is only partially ordered, so merge-sort a copy for display."""
        return merge_sort(self.queue.items(), key=lambda p: (p.priority, p.seq))

    def history_sorted_by_wait(self):
        return merge_sort(self.history.to_list(), key=lambda p: -p.wait_minutes())


# ----------------------------------------------------------------------------
# Step 7: Console dashboard
# ----------------------------------------------------------------------------
LINE = "=" * 78


def show_dashboard(sys_):
    waiting = sys_.waiting_sorted()
    print("\n" + LINE)
    print(" HOSPITAL EMERGENCY QUEUE DASHBOARD".center(78))
    print(LINE)
    counts = {k: 0 for k in PRIORITY_LABELS}
    for p in waiting:
        counts[p.priority] += 1
    print(f" Waiting: {len(waiting)}   |   Completed/Closed: {len(sys_.history)}"
          f"   |   Total registered: {len(sys_.records)}")
    print(" By priority: " + "  ".join(f"P{k}={v}" for k, v in counts.items()))
    print("-" * 78)

    nxt = sys_.next_patient()
    if nxt:
        print(f" >> NEXT TO BE ATTENDED: {nxt.name} ({nxt.pid}), age {nxt.age}, "
              f"{nxt.condition} [P{nxt.priority}]")
    else:
        print(" >> NEXT TO BE ATTENDED: none, queue is empty")
    print("-" * 78)

    print(f" {'#':<3}{'ID':<8}{'Name':<18}{'Age':<5}{'Condition':<20}{'Pri':<5}{'Waiting':<8}")
    print(" " + "-" * 66)
    if not waiting:
        print(" (no patients waiting)")
    for i, p in enumerate(waiting, 1):
        print(f" {i:<3}{p.pid:<8}{p.name[:16]:<18}{p.age:<5}{p.condition[:18]:<20}"
              f"{p.priority:<5}{p.wait_minutes():>5.1f}m")
    print("-" * 78)
    print(" Recent activity:")
    for line in sys_.activity.to_list() or ["(none)"]:
        print("   " + line)
    print(LINE)


def show_patient(p):
    print(f"  ID: {p.pid} | Name: {p.name} | Age: {p.age}")
    print(f"  Condition: {p.condition}")
    print(f"  Priority: {p.priority} - {PRIORITY_LABELS[p.priority]}")
    print(f"  Status: {p.status} | Arrived: {p.arrival_time:%Y-%m-%d %H:%M:%S}"
          f" | Wait: {p.wait_minutes():.1f} min")


def show_history(sys_):
    items = sys_.history.to_list()
    print("\n--- PATIENT WAITING HISTORY ---")
    if not items:
        print("  No history yet.")
        return
    print("  1) In order of completion   2) Longest wait first")
    choice = input("  Choose view [1]: ").strip() or "1"
    if choice == "2":
        items = sys_.history_sorted_by_wait()
    print(f"\n  {'ID':<8}{'Name':<18}{'Pri':<5}{'Status':<11}{'Waited (min)':<13}")
    print("  " + "-" * 55)
    for p in items:
        print(f"  {p.pid:<8}{p.name[:16]:<18}{p.priority:<5}{p.status:<11}{p.wait_minutes():<13.2f}")
    avg = sum(p.wait_minutes() for p in items) / len(items)
    print(f"\n  Average wait: {avg:.2f} min over {len(items)} patient(s)")


def read_int(prompt, lo, hi):
    while True:
        try:
            v = int(input(prompt))
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        print(f"  Please enter a number between {lo} and {hi}.")


def register_flow(sys_):
    print("\n--- REGISTER NEW PATIENT ---")
    name = input("  Name: ").strip()
    if not name:
        print("  Name cannot be empty.")
        return
    age = read_int("  Age: ", 0, 120)
    condition = input("  Condition / complaint: ").strip() or "Not specified"
    print("  Priority levels:")
    for k, v in PRIORITY_LABELS.items():
        print(f"    {k} = {v}")
    pr = read_int("  Priority (1-5): ", 1, 5)
    p = sys_.register(name, age, condition, pr)
    print(f"  Registered! Patient ID: {p.pid}")


def search_flow(sys_):
    print("\n--- SEARCH PATIENT RECORDS ---")
    q = input("  Enter patient ID (e.g. P1001) or name: ").strip()
    if not q:
        return
    p = sys_.search_by_id(q)
    results = [p] if p else sys_.search_by_name(q)
    if not results:
        print("  No matching patient found.")
        return
    for r in results:
        print("  " + "-" * 50)
        show_patient(r)


def load_sample_data(sys_):
    samples = [
        ("Ravi Kumar", 54, "Chest pain", 1),
        ("Anita Sharma", 29, "Fractured arm", 3),
        ("Mohammed Ali", 8, "High fever", 2),
        ("Priya Nair", 35, "Minor cut", 5),
        ("John Peter", 62, "Breathing difficulty", 1),
        ("Sneha Reddy", 24, "Sprained ankle", 4),
    ]
    for s in samples:
        sys_.register(*s)
    print("  Loaded 6 sample patients.")


MENU = """
 1. Register new patient          6. Cancel / remove a patient
 2. Show dashboard (queue)        7. Change a patient's priority
 3. Show next patient             8. View waiting history
 4. Attend next patient           9. Load sample data
 5. Search patient records        0. Exit
"""


def main():
    system = HospitalQueueSystem()
    print("\nWelcome to the Hospital Emergency Patient Queue Management System")
    while True:
        print(MENU)
        choice = input(" Enter choice: ").strip()
        if choice == "1":
            register_flow(system)
        elif choice == "2":
            show_dashboard(system)
        elif choice == "3":
            p = system.next_patient()
            print("\n  NEXT PATIENT:" if p else "\n  Queue is empty.")
            if p:
                show_patient(p)
        elif choice == "4":
            p = system.attend_next()
            if p:
                print(f"\n  Now attending: {p.name} ({p.pid}) - waited {p.wait_minutes():.2f} min")
            else:
                print("\n  Queue is empty.")
        elif choice == "5":
            search_flow(system)
        elif choice == "6":
            pid = input("  Patient ID to remove: ").strip().upper()
            p = system.cancel(pid)
            print(f"  Removed {p.name}." if p else "  Patient not found in waiting queue.")
        elif choice == "7":
            pid = input("  Patient ID: ").strip().upper()
            pr = read_int("  New priority (1-5): ", 1, 5)
            print("  Priority updated." if system.change_priority(pid, pr)
                  else "  Patient not found in waiting queue.")
        elif choice == "8":
            show_history(system)
        elif choice == "9":
            load_sample_data(system)
        elif choice == "0":
            print("  Goodbye!")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
