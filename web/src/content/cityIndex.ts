import type { CityCandidate } from '../types'

// Limited local city-centre index for user-declared visits, not device location or navigation.
export const manualCityIndex: CityCandidate[] = [
  {
    adcode: '350200',
    city_name: '厦门市',
    province_name: '福建省',
    longitude: 118.0894,
    latitude: 24.4798,
    source: 'manual',
  },
  {
    adcode: '330100',
    city_name: '杭州市',
    province_name: '浙江省',
    longitude: 120.1551,
    latitude: 30.2741,
    source: 'manual',
  },
  {
    adcode: '510100',
    city_name: '成都市',
    province_name: '四川省',
    longitude: 104.0665,
    latitude: 30.5723,
    source: 'manual',
  },
  {
    adcode: '440100',
    city_name: '广州市',
    province_name: '广东省',
    longitude: 113.2644,
    latitude: 23.1291,
    source: 'manual',
  },
  {
    adcode: '310000',
    city_name: '上海市',
    province_name: '上海市',
    longitude: 121.4737,
    latitude: 31.2304,
    source: 'manual',
  },
  {
    adcode: '110000',
    city_name: '北京市',
    province_name: '北京市',
    longitude: 116.4074,
    latitude: 39.9042,
    source: 'manual',
  },
]
export function matchManualCities(query: string) {
  const term = query.trim()
  return manualCityIndex.filter((city) =>
    `${city.city_name} ${city.province_name}`.includes(term),
  )
}
