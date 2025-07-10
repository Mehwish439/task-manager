import { createRouter, createWebHistory } from 'vue-router'
import Signup from '../components/Signup.vue'
import Login from '../components/Login.vue'
import CreateTask from '../components/CreateTask.vue'
import AssignedTasks from '../components/AssignedTasks.vue'
 import TaskList from '../components/TaskList.vue'

const routes = [
  { path: '/', redirect: { name: 'Login' } }, // redirect to login by name
  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },
  { path: '/create-task', name: 'CreateTask', component: CreateTask },
  { path: '/assigned-tasks', name: 'AssignedTasks', component: AssignedTasks },
   { path: '/task-list', name: 'TaskList', component: TaskList },
  { path: '/:catchAll(.*)', redirect: { name: 'Login' } } // optional fallback
 


 
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
