import { createRouter, createWebHistory } from 'vue-router'

import Signup from '../components/Signup.vue'
import Login from '../components/Login.vue'
import CreateTask from '../components/CreateTask.vue'
import AssignedTasks from '../components/AssignedTasks.vue'
import TaskList from '../components/TaskList.vue'

// SaaS Pages (ONLY if file exists in components/)
const SuperAdminDashboard = () =>
  import('@/components/SuperAdminDashboard.vue')

const InviteEmployees = () =>
  import('@/components/InviteEmployees.vue')

const routes = [
  { path: '/', redirect: { name: 'Login' } },

  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },

  { path: '/create-task', name: 'CreateTask', component: CreateTask },
  { path: '/assigned-tasks', name: 'AssignedTasks', component: AssignedTasks },
  { path: '/task-list', name: 'TaskList', component: TaskList },

  // 👑 Super Admin
  {
    path: '/admin',
    name: 'SuperAdminDashboard',
    component: SuperAdminDashboard,
    meta: { requiresAuth: true, role: 'super_admin' }
  },

  // 👥 Invite Employees
  {
    path: '/invite-employees',
    name: 'InviteEmployees',
    component: InviteEmployees,
    meta: { requiresAuth: true, role: 'team_lead' }
  },

  { path: '/:catchAll(.*)', redirect: { name: 'Login' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router