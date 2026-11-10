# 🏥 Hospital Emergency Patient Queue Management System

A web-based Hospital Emergency Patient Queue Management System designed to manage patients efficiently based on the severity of their medical conditions.

The system uses **Data Structures and Algorithms (DSA)** to prioritize patients, manage waiting queues, maintain patient records, and track hospital activity.

Unlike a traditional first-come-first-served queue, this system ensures that patients with more critical conditions receive attention first, while maintaining FIFO order for patients with the same priority.

## ✨ Features

- **Patient Registration:** Register patients with their name, age, medical condition, and priority level.
- **Priority-Based Queue:** Automatically arranges patients based on the severity of their condition.
- **Automatic Patient Allocation:** Identifies the next patient who should be attended.
- **Priority Management:** Update a patient's priority while they are waiting.
- **Patient Cancellation:** Remove patients from the waiting queue.
- **Patient Search:** Search patient records using patient ID or name.
- **Waiting History:** Maintain records of completed and removed patients.
- **Waiting Time Tracking:** Calculate patient waiting times and average waiting time.
- **Heap Visualization:** Display the underlying min-heap as a tree and array.
- **Recent Activity:** Track recent hospital queue activities.
- **Interactive Dashboard:** View patient statistics and queue information through a web interface.

## 🚦 Priority Levels

Patients are assigned one of five priority levels:

| Priority | Category | Description |
|---|---|---|
| 1 | Critical | Requires immediate attention |
| 2 | Emergent | Needs very urgent medical attention |
| 3 | Urgent | Serious but stable condition |
| 4 | Less Urgent | Can wait for a short period |
| 5 | Non-Urgent | Minor conditions |

**Note:** A lower priority number represents a higher medical urgency. Patients with the same priority are attended in their order of arrival.

## 🧠 Data Structures and Algorithms Used

This project demonstrates the practical implementation of multiple DSA concepts.

| DSA Concept | Application |
|---|---|
| Min-Heap | Manages the priority-based patient waiting queue. |
| Hash Maps | Stores patient records and enables efficient searching using patient IDs and names. |
| Singly Linked List | Maintains the history of completed and removed patients. |
| FIFO Queue | Stores the six most recent hospital activities. |
| Merge Sort | Sorts patients for queue display and waiting history reports. |

### Time Complexity

| Operation | Time Complexity |
|---|---|
| Register Patient | O(log n) |
| Attend Next Patient | O(log n) |
| View Next Patient | O(1) |
| Remove Patient | O(log n) |
| Change Patient Priority | O(log n) |
| Search by Patient ID | O(1) average |
| Display Sorted Queue | O(n log n) |
| Add Patient to History | O(1) |

## 🛠️ Technologies Used

- **Python** – Backend logic and DSA implementation.
- **HTML5** – Frontend structure.
- **CSS3** – Styling and responsive dashboard.
- **JavaScript** – Interactive frontend and API communication.
- **Python HTTP Server** – Backend server and REST API.

The project uses Python's standard library for the backend and does not require additional Python package installations.

## 📂 Project Structure

```text
Hospital-Emergency-Queue/
│
├── hospital_queue.py    # DSA implementation and console version
│
├── server.py            # Backend server and REST API
│
├── static/
│   └── index.html       # Frontend dashboard
│
├── README.md            # Project documentation
│
├── LICENSE              # MIT License
│
└── .gitignore
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.8 or above
- Git
- A modern web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

### Step 2: Navigate to the Project Folder

```bash
cd YOUR-REPOSITORY
```

### Step 3: Run the Application

```bash
python server.py
```

### Step 4: Open the Application

The application automatically opens in your default browser.

Alternatively, visit:

```text
http://localhost:8000
```

To stop the server, press `Ctrl + C` in the terminal.

### Running the Console Version

A console-based version is also available:

```bash
python hospital_queue.py
```

## 🔌 API Endpoints

The backend provides the following API endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/state` | Retrieves queue information, statistics, history, and activity. |
| POST | `/api/register` | Registers a new patient. |
| POST | `/api/attend` | Attends the next patient in the queue. |
| POST | `/api/cancel` | Removes a patient from the waiting queue. |
| POST | `/api/priority` | Updates a patient's priority. |
| GET | `/api/search?q=` | Searches patient records. |
| POST | `/api/sample` | Loads sample patient records. |
| POST | `/api/reset` | Resets the queue system. |

## 🎯 Learning Outcomes

Through this project, the following concepts are demonstrated:

- Practical implementation of non-linear data structures.
- Understanding priority queues and min-heap operations.
- Efficient searching using hash maps.
- Managing historical records using linked lists.
- Understanding FIFO queue operations.
- Applying sorting algorithms to real-world problems.
- Connecting backend logic with a web-based frontend.
- Designing and implementing API-based communication.

## 🚀 Future Improvements

- Database integration for permanent patient record storage.
- User authentication for hospital staff.
- Separate dashboards for doctors and administrators.
- Patient notifications when their turn approaches.
- Advanced analytics and hospital performance reports.

## ⚠️ Disclaimer

This project is developed for educational and academic purposes to demonstrate Data Structures and Algorithms. It is not intended for actual medical diagnosis, emergency triage, or real-world hospital operations.

## 👩‍💻 Author

Developed as a Data Structures and Algorithms project to demonstrate the practical application of fundamental data structures and algorithms in a real-world inspired hospital management scenario.

---

⭐ If you find this project interesting, consider giving this repository a star!
