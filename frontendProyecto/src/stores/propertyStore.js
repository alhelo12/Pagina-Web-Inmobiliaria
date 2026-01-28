import { defineStore } from 'pinia'

export const usePropertyStore = defineStore('properties', {
  state: () => ({
    list: []
  }),
  actions: {
    load(properties) {
      this.list = properties
    }
  }
})
