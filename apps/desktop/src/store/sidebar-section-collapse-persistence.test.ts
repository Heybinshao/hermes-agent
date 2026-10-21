import { beforeEach, describe, expect, it, vi } from 'vitest'

// The Pinned / Sessions headers in the left sidebar are the only collapsible
// sections whose open state lives in a plain in-memory atom, so a reload (⌘R
// or an app restart) silently re-expands a section the user had collapsed.
// Cron (below), the messaging platform groups, and the date dividers all
// persist; these two sit next to them and should behave the same way.

async function loadLayout() {
  const layout = await import('./layout')

  return layout
}

const reload = () => vi.resetModules()

describe('sidebar section collapse persistence (Pinned / Sessions)', () => {
  beforeEach(() => {
    window.localStorage.clear()
    vi.resetModules()
  })

  it('keeps the Pinned section collapsed across a reload', async () => {
    const s1 = await loadLayout()
    expect(s1.$sidebarPinsOpen.get()).toBe(true)

    s1.setSidebarPinsOpen(false)
    expect(s1.$sidebarPinsOpen.get()).toBe(false)

    reload()
    const s2 = await loadLayout()

    expect(s2.$sidebarPinsOpen.get()).toBe(false)
  })

  it('keeps the Sessions section collapsed across a reload', async () => {
    const s1 = await loadLayout()
    expect(s1.$sidebarRecentsOpen.get()).toBe(true)

    s1.setSidebarRecentsOpen(false)

    reload()
    const s2 = await loadLayout()

    expect(s2.$sidebarRecentsOpen.get()).toBe(false)
  })
})
