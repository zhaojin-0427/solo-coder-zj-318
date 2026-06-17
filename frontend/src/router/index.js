import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/photos'
  },
  {
    path: '/photos',
    name: 'Photos',
    component: () => import('@/views/PhotosPage.vue'),
    meta: { title: '照片归档', icon: 'Picture', step: 1 }
  },
  {
    path: '/persons',
    name: 'Persons',
    component: () => import('@/views/PersonsPage.vue'),
    meta: { title: '人物关系补注', icon: 'User', step: 2 }
  },
  {
    path: '/memories',
    name: 'Memories',
    component: () => import('@/views/MemoriesPage.vue'),
    meta: { title: '回忆片段整理', icon: 'Document', step: 3 }
  },
  {
    path: '/confirm',
    name: 'Confirm',
    component: () => import('@/views/ConfirmPage.vue'),
    meta: { title: '家庭确认台', icon: 'CircleCheck', step: 4 }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/StatsPage.vue'),
    meta: { title: '数据统计', icon: 'DataAnalysis', step: 5 }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta?.title ? `${to.meta.title} - 家族回忆共编平台` : '家族回忆共编平台'
  next()
})

export default router
