import { createRouter, createWebHistory, type RouterHistory } from 'vue-router'
import type { AppView } from './types'

export const viewPaths: Record<AppView, string> = {
  discover: '/',
  journeys: '/plan',
  map: '/journey/map',
  memories: '/journey/stories',
  studio: '/studio',
  profile: '/account',
}
export function createProductRouter(history: RouterHistory = createWebHistory()) {
  return createRouter({
    history,
    routes: [
      ...Object.entries(viewPaths).map(([name, path]) => ({
        name,
        path,
        component: { render: () => null },
      })),
      { path: '/:pathMatch(.*)*', redirect: '/' },
    ],
  })
}
