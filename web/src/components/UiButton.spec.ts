import { defineComponent } from 'vue'
import { enableAutoUnmount, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import UiButton from './UiButton.vue'

enableAutoUnmount(afterEach)

describe('共享按钮的原生表单与执行边界', () => {
  it('默认不提交表单；submit保留必填校验、form关联与loading锁定', async () => {
    const submitted = vi.fn()
    const wrapper = mount(defineComponent({
      components: { UiButton },
      template: '<form id="test-brief" @submit.prevent="submitted"><input aria-label="旅行想法" required /></form><UiButton form="test-brief" :type="kind" :loading="loading">安排旅程</UiButton>',
      data: () => ({ kind: 'button' as 'button' | 'submit', loading: false }),
      methods: { submitted },
    }), { attachTo: document.body })
    const button = wrapper.get('button')
    const input = wrapper.get('input')
    ;(button.element as HTMLButtonElement).click()
    expect(submitted).not.toHaveBeenCalled()
    await wrapper.setData({ kind: 'submit' })
    ;(button.element as HTMLButtonElement).click()
    expect(submitted).not.toHaveBeenCalled()
    await input.setValue('去看看海')
    ;(button.element as HTMLButtonElement).click()
    expect(submitted).toHaveBeenCalledTimes(1)
    await wrapper.setData({ loading: true })
    expect(button.attributes('aria-busy')).toBe('true')
    expect(button.text()).toBe('安排旅程')
    ;(button.element as HTMLButtonElement).click()
    expect(submitted).toHaveBeenCalledTimes(1)
  })

  it('原生disabled阻止重复点击，恢复后传递click与无障碍名称', async () => {
    const clicked = vi.fn()
    const wrapper = mount(UiButton, {
      props: { disabled: true },
      attrs: { onClick: clicked, 'aria-label': '确认删除选中的记忆' },
      slots: { default: '确认删除' },
      attachTo: document.body,
    })
    ;(wrapper.element as HTMLButtonElement).click()
    expect(clicked).not.toHaveBeenCalled()
    await wrapper.setProps({ disabled: false })
    ;(wrapper.element as HTMLButtonElement).click()
    expect(clicked).toHaveBeenCalledTimes(1)
    expect(wrapper.attributes('aria-label')).toBe('确认删除选中的记忆')
  })
})
