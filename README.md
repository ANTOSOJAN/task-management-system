# 🚀 Collaborative Task Management System

A cloud-based multi-user task management platform built using **Python**, **Google App Engine**, **Firebase Authentication**, and **Google Firestore**.

The application enables teams to create shared task boards, assign tasks, collaborate in real time, and manage project workflows securely through role-based access controls.

---

## 📌 Project Overview

This project was developed as part of the **Cloud Platforms & Applications** module and demonstrates modern cloud-native application development using Firebase and Google Cloud technologies.

The system supports:

* Secure Firebase Authentication
* Multi-user collaboration
* Shared task boards
* Task assignment and tracking
* Board ownership permissions
* Real-time Firestore data management
* Cloud deployment architecture

---

## ✨ Key Features

### 🔐 Secure Authentication

* Firebase Login & Logout
* Token-based Authentication
* Session Validation
* Protected Routes
* Access Control Enforcement

### 📋 Task Board Management

* Create Task Boards
* Rename Boards
* Delete Boards
* View Shared Boards
* Board Ownership Controls

### 👥 User Collaboration

* Invite Users to Boards
* Remove Users from Boards
* Shared Board Access
* Team Collaboration Support

### ✅ Task Management

* Create Tasks
* Edit Tasks
* Delete Tasks
* Assign Multiple Users
* Due Date Management
* Mark Tasks Complete
* Track Completion Timestamp

### 📊 Productivity Monitoring

* Active Task Counter
* Completed Task Counter
* Total Task Counter
* Board Statistics Dashboard

---

## 🏗️ System Architecture

```text
Client Browser
      │
      ▼
Firebase Authentication
      │
      ▼
Google App Engine
(Python Backend)
      │
      ▼
Google Firestore
(Database)
      │
      ▼
Task Boards & Tasks
```

---

## 🛠️ Technology Stack

| Category        | Technology              |
| --------------- | ----------------------- |
| Backend         | Python                  |
| Cloud Platform  | Google App Engine       |
| Authentication  | Firebase Authentication |
| Database        | Google Firestore        |
| Frontend        | HTML, CSS, JavaScript   |
| Template Engine | Jinja2                  |
| Version Control | Git                     |

---

## 📂 Core Functionality

### Board Management

Users can:

* Create new boards
* View owned boards
* View boards shared with them
* Rename existing boards
* Delete empty boards

### User Management

Board creators can:

* Add users by email
* Remove users
* Manage board membership
* Control board access

### Task Management

Board members can:

* Create tasks
* Update task information
* Mark tasks complete
* Delete tasks
* Assign tasks to users

---

## 🔒 Access Control Rules

The application implements role-based authorization:

### Board Owner Permissions

✔ Create Board

✔ Rename Board

✔ Delete Board

✔ Add Users

✔ Remove Users

### Board Member Permissions

✔ View Board

✔ Create Tasks

✔ Edit Tasks

✔ Complete Tasks

✔ Delete Tasks

### Restricted Actions

✖ Non-owners cannot rename boards

✖ Non-owners cannot delete boards

✖ Non-owners cannot remove users

✖ Boards cannot be deleted while users remain

✖ Boards cannot be deleted while tasks remain

---

## 📊 Database Design

### Users Collection

```text
users
│
└── user_id
```

### Boards Collection

```text
boards
│
├── title
├── description
├── created_by
└── members
```

### Tasks Subcollection

```text
boards
│
└── tasks
    ├── title
    ├── due_date
    ├── assignees
    ├── completed
    └── completed_at
```

---

## 🔄 Application Workflow

1. User authenticates using Firebase.
2. User creates a task board.
3. Board owner invites collaborators.
4. Team members create tasks.
5. Tasks are assigned to users.
6. Users update task status.
7. Completed tasks are tracked with timestamps.
8. Board statistics update dynamically.

---

## 🎯 Learning Outcomes

This project demonstrates practical experience with:

* Cloud Application Development
* Firebase Authentication
* Google Firestore
* Access Control & Authorization
* Multi-user Collaboration Systems
* RESTful Backend Design
* NoSQL Database Modelling
* Secure Session Management
* Full Application Lifecycle Development

---

## 🚀 Future Enhancements

* Real-Time Notifications
* Email Invitations
* Activity Logs
* Board Templates
* Task Priority Levels
* Kanban Board View
* File Attachments
* Mobile Application Support
* Cloud Monitoring Dashboard

---

## 👨‍💻 Author

**Anto Sojan Illickal**

MSc Big Data Management & Analytics

Griffith College Dublin

GitHub: https://github.com/ANTOSOJAN

LinkedIn: https://www.linkedin.com/in/anto-s-illickal-3400721bb

---

## 📄 License

This project is provided for educational, learning, and portfolio purposes.
