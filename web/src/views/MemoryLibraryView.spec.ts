import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import MemoryLibraryView from './MemoryLibraryView.vue'
import type { MapOverview, VisitedCity } from '../types'

const city: VisitedCity = {
  adcode: '350200',
  name_zh: '厦门市',
  name_en: 'Xiamen',
  province_zh: '福建省',
  longitude: 118.0894,
  latitude: 24.4798,
  first_visited_at: '2025-06-01',
  last_visited_at: '2026-06-08',
  memory_count: 2,
  check_in_source: 'manual',
}
const overview: MapOverview = {
  username: 'explicit-unit-fixture',
  map_center: [104, 35],
  default_zoom: 4,
  stats: { lit_cities: 2, memories: 2, photos: 0, vlog_minutes: 0 },
  visited_cities: [
    city,
    {
      ...city,
      adcode: '440100',
      name_zh: '广州市',
      name_en: 'Guangzhou',
      province_zh: '广东省',
      memory_count: 0,
    },
  ],
  year_summaries: [
    {
      year: 2025,
      stats: { lit_cities: 1, memories: 1, photos: 0, vlog_minutes: 0 },
      cities: [{ adcode: city.adcode, memory_count: 1 }],
    },
  ],
}

describe('城市记忆索引（明确本地测试输入）', () => {
  it('空档案不编造记忆或封面，记录与整理故事均需主动点击', async () => {
    const wrapper = mount(MemoryLibraryView, {
      props: {
        overview: {
          ...overview,
          visited_cities: [],
          stats: { lit_cities: 0, memories: 0, photos: 0, vlog_minutes: 0 },
        },
      },
    })
    expect(wrapper.findAll('.memory-city-card')).toHaveLength(0)
    expect(wrapper.findAll('img')).toHaveLength(0)
    expect(wrapper.emitted('manualCheckIn')).toBeUndefined()
    await wrapper.get('.memory-library-empty button').trigger('click')
    expect(wrapper.emitted('manualCheckIn')).toEqual([[]])
    await wrapper.get('.journey-hero button').trigger('click')
    expect(wrapper.emitted('compose')).toEqual([[]])
  })
  it('城市／省份搜索、已有记忆和年份筛选使用真实活动数量，清除后恢复', async () => {
    const wrapper = mount(MemoryLibraryView, { props: { overview } })
    expect(wrapper.findAll('.memory-city-card')).toHaveLength(2)
    await wrapper.get('input[aria-label="搜索记忆中的城市"]').setValue('福建')
    expect(wrapper.findAll('.memory-city-card')).toHaveLength(1)
    await wrapper.get('select').setValue('2025')
    expect(wrapper.get('.memory-card-bottom').text()).toContain(
      '1 段2025年记忆',
    )
    await wrapper.get('input[type=checkbox]').setValue(true)
    await wrapper
      .get('input[aria-label="搜索记忆中的城市"]')
      .setValue('不存在的城市')
    expect(wrapper.findAll('.memory-city-card')).toHaveLength(0)
    await wrapper.get('.memory-library-empty button').trigger('click')
    expect(wrapper.findAll('.memory-city-card')).toHaveLength(2)
    expect(
      wrapper.get<HTMLInputElement>('input[type=checkbox]').element.checked,
    ).toBe(false)
  })
  it('打开城市只发出选城事件，年份失效后恢复全部城市', async () => {
    const wrapper = mount(MemoryLibraryView, { props: { overview } })
    await wrapper.get('[aria-label="打开厦门市的城市记忆"]').trigger('click')
    expect(wrapper.emitted('selectCity')?.[0]).toEqual([city])
    expect(wrapper.emitted('compose')).toBeUndefined()
    await wrapper.get('select').setValue('2025')
    await wrapper.setProps({ overview: { ...overview, year_summaries: [] } })
    expect(wrapper.findAll('.memory-city-card')).toHaveLength(2)
  })
})
