const STORAGE_KEY = 'pcqvp-sidebar-collapsed'

const isCollapsed = ref(false)
const isMobileOpen = ref(false)

let initialized = false

export function useSidebar() {
  if (import.meta.client && !initialized) {
    initialized = true
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved !== null) {
      isCollapsed.value = saved === 'true'
    }

    watch(isCollapsed, (val) => {
      localStorage.setItem(STORAGE_KEY, String(val))
    })
  }

  function toggle() {
    isCollapsed.value = !isCollapsed.value
  }

  function openMobile() {
    isMobileOpen.value = true
  }

  function closeMobile() {
    isMobileOpen.value = false
  }

  return {
    isCollapsed,
    isMobileOpen,
    toggle,
    openMobile,
    closeMobile,
  }
}
