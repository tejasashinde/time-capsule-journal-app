import Alpine from 'alpinejs'

window.createCapsuleForm = () => ({
  custom: false,
  selectCustom() {
    this.custom = true
  },
  clearCustom() {
    this.custom = false
  },
})

window.cardCarousel = () => ({
  canScrollLeft: false,
  canScrollRight: false,
  init() {
    this.updateScrollState()
    this.$nextTick(() => this.updateScrollState())
    window.addEventListener('resize', () => this.updateScrollState())
  },
  updateScrollState() {
    const rail = this.$refs.rail
    if (!rail) return
    this.canScrollLeft = rail.scrollLeft > 8
    const remaining = rail.scrollWidth - rail.clientWidth - rail.scrollLeft
    this.canScrollRight = remaining > 8
  },
  scrollLeft() {
    const rail = this.$refs.rail
    if (!rail) return
    rail.scrollBy({ left: -Math.max(rail.clientWidth * 0.8, 320), behavior: 'smooth' })
    window.setTimeout(() => this.updateScrollState(), 350)
  },
  scrollRight() {
    const rail = this.$refs.rail
    if (!rail) return
    rail.scrollBy({ left: Math.max(rail.clientWidth * 0.8, 320), behavior: 'smooth' })
    window.setTimeout(() => this.updateScrollState(), 350)
  },
})

window.countdown = (targetIso) => ({
  label: '',
  timerId: null,
  init() {
    this.update()
    this.timerId = window.setInterval(() => this.update(), 1000)
  },
  update() {
    const diff = new Date(targetIso) - new Date()

    if (diff <= 0) {
      this.label = 'Unlocked now'
      if (this.timerId) {
        window.clearInterval(this.timerId)
        this.timerId = null
      }
      return
    }

    const totalSeconds = Math.floor(diff / 1000)
    const days = Math.floor(totalSeconds / 86400)
    const hours = Math.floor((totalSeconds % 86400) / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60

    this.label = `${days}d ${hours}h ${minutes}m ${seconds}s`
  },
  destroy() {
    if (this.timerId) {
      window.clearInterval(this.timerId)
      this.timerId = null
    }
  },
})

window.Alpine = Alpine

Alpine.start()
