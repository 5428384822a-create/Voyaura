export interface DiscoveryIntent {
  cityAdcode?: string
  goal: string
  interests?: string[]
  pace?: 'relaxed' | 'balanced'
  days?: number
}

export type TravelMood = 'all' | 'sea' | 'culture' | 'slow'
export const destinations = [
  {
    id: 'xiamen',
    name: '厦门',
    adcode: '350200',
    english: 'XIAMEN',
    image: '/discover/xiamen-card.webp',
    imageAlt: '厦门鼓浪屿的海岸与岛上建筑',
    headline: '把时间，交给海风',
    description: '海岸、街巷与一段不赶路的时光。',
    tags: ['海边慢游', '街巷漫步'],
    moods: ['sea', 'culture', 'slow'],
    interests: ['海边', '历史街区'],
    goal: '想去厦门旅行两天，看看海，走走老街，安排轻松一点。',
  },
  {
    id: 'hangzhou',
    name: '杭州',
    adcode: '330100',
    english: 'HANGZHOU',
    image: '/discover/hangzhou.webp',
    imageAlt: '杭州西湖的湖面与湖畔景色',
    headline: '在湖光里，慢下来',
    description: '沿着湖边散步，留一点时间看风景。',
    tags: ['湖畔漫步', '自然风光'],
    moods: ['culture', 'slow'],
    interests: ['公园', '历史'],
    goal: '想去杭州旅行两天，沿西湖散步，看看自然风景，节奏轻松一点。',
  },
  {
    id: 'chengdu',
    name: '成都',
    adcode: '510100',
    english: 'CHENGDU',
    image: '/discover/chengdu.webp',
    imageAlt: '成都大熊猫繁育研究基地的大熊猫',
    headline: '和可爱，偶然相遇',
    description: '看看熊猫，走进一座城的日常。',
    tags: ['熊猫时光', '城市漫游'],
    moods: ['culture', 'slow'],
    interests: ['公园', '美食'],
    goal: '想去成都旅行两天，看看熊猫，感受街巷和美食，行程不要太赶。',
  },
] as const

export const searchableCities = [
  ...destinations.map((d) => ({ name: d.name, adcode: d.adcode })),
  { name: '广州', adcode: '440100' },
  { name: '上海', adcode: '310000' },
  { name: '北京', adcode: '110000' },
]

export function destinationIntent(id: string): DiscoveryIntent {
  const city = destinations.find((d) => d.id === id) ?? destinations[0]
  return {
    cityAdcode: city.adcode,
    goal: city.goal,
    interests: [...city.interests],
    pace: 'relaxed',
    days: 2,
  }
}

export function matchCities(query: string) {
  return searchableCities.filter((city) => query.includes(city.name))
}
