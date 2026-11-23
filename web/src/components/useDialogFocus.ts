import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  onUnmounted,
  type Ref,
} from 'vue'

/** Keyboard focus stays in the active dialog and returns to its opener on close. */
export function useDialogFocus(
  root: Ref<HTMLElement | null>,
  close: () => void,
  options: { active?: () => boolean; initial?: string } = {},
) {
  const opener =
    document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null
  const active = () => root.value?.isConnected && (options.active?.() ?? true)
  const elements = () =>
    [
      ...(root.value?.querySelectorAll<HTMLElement>(
        'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), summary, [tabindex="0"]',
      ) ?? []),
    ].filter((el) => !el.closest('[inert]') && el.getClientRects().length > 0)
  const focusFirst = () =>
    (
      root.value?.querySelector<HTMLElement>(
        options.initial ??
          'input:not(:disabled), textarea:not(:disabled), button:not(:disabled)',
      ) ?? elements()[0]
    )?.focus()
  function keydown(event: KeyboardEvent) {
    if (!active()) return
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
      return
    }
    if (event.key !== 'Tab') return
    const items = elements(),
      first = items[0],
      last = items.at(-1)
    if (!root.value?.contains(document.activeElement)) {
      event.preventDefault()
      focusFirst()
    } else if (event.shiftKey && document.activeElement === first && last) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last && first) {
      event.preventDefault()
      first.focus()
    }
  }
  onMounted(async () => {
    document.addEventListener('keydown', keydown)
    await nextTick()
    if (active()) focusFirst()
  })
  onBeforeUnmount(() => {
    document.removeEventListener('keydown', keydown)
    if (root.value) {
      root.value.setAttribute('aria-hidden', 'true')
      root.value.inert = true
    }
  })
  onUnmounted(async () => {
    await nextTick()
    const nextDialog = document.querySelector<HTMLElement>(
      '[role="dialog"][aria-modal="true"]:not([aria-hidden="true"])',
    )
    if (nextDialog && opener && !nextDialog.contains(opener)) return
    if (opener?.isConnected && !opener.closest('[inert]')) opener.focus()
  })
}
