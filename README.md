 
# 🧩 Team Task Manager

A full-stack team-based task management system built with **Django (Python)** on the backend and **Vue.js** on the frontend. This application enables teams to efficiently manage tasks, assign responsibilities, track progress, and collaborate in real-time.

## 🚀 Features

- 🔐 User authentication (Login/Signup)
- 👥 Team roles (Team Lead & Team Members)
- 📝 Create, update, and delete tasks
- 📌 Assign tasks to one or more team members
- ✅ Track task status (In Progress, Completed)
- 💬 Add comments to tasks
- 🎨 Responsive UI with dynamic theme colors
- 📦 Persistent data with secure API integration

## 🛠 Tech Stack

| Layer        | Tech                             |
|--------------|----------------------------------|
| Frontend     | Vue 3, JavaScript, Axios         |
| Backend      | Django, Django REST Framework    |
| Styling      | CSS / Bootstrap / Tailwind CSS   |
| Auth         | JWT Authentication               |
| Database     | SQLite / PostgreSQL              |
| Deployment   | GitHub, Render, Netlify (optional) |

## 📂 Project Structure

```
TeamTaskManager/
│
├── backend/                # Django backend (API)
│   ├── manage.py
│   ├── todo/               # Django app with Task model & views
│   └── ...
│
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Pages like Login, Dashboard, etc.
│   │   └── App.vue
│   └── ...
│
├── README.md
└── .gitignore
```

## 🧪 Getting Started

### 🔧 Backend Setup (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate         # On Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 🌐 Frontend Setup (Vue)

```bash
cd frontend
npm install
npm run serve
```

> Ensure both servers are running and frontend is configured to communicate with the Django backend API.

## 🔑 Environment Variables

### Backend (`.env`)
```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### Frontend (`.env`)
```
VUE_APP_API_URL=http://127.0.0.1:8000/api/
```

## ✅ API Endpoints (Django DRF)

| Method | Endpoint                  | Description                |
|--------|---------------------------|----------------------------|
| POST   | `/api/login/`             | User login (JWT)           |
| POST   | `/api/register/`          | User registration          |
| GET    | `/api/tasks/`             | List all tasks             |
| POST   | `/api/tasks/create/`      | Create a task              |
| PUT    | `/api/tasks/<id>/update/` | Update a task              |
| DELETE | `/api/tasks/<id>/delete/` | Delete a task              |
| POST   | `/api/tasks/<id>/assign/` | Assign task to user(s)     |

## 📸 Screenshots

_(Include screenshots of your app’s UI here)_

## 📌 TODO / Future Enhancements

- [ ] Drag-and-drop task reordering
- [ ] Email notifications on assignment
- [ ] Due dates and reminders
- [ ] User profile with avatar
- [ ] Activity log / history tracking

## 📃 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with improvements or bug fixes.

## 📬 Contact

**Mehwish Shakoor**  
📧 mehwishshakoor5@gmail.com  
📍 Islamabad, Pakistan
