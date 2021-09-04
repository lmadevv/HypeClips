import { writable } from "svelte/store"
import { UNDEFINED_ID } from "./constants"

// Connecting a Svelte store to local storage: https://dev.to/danawoodman/svelte-quick-tip-connect-a-store-to-local-storage-4idi
const storedId = localStorage.getItem("id")
export const id = writable(storedId || UNDEFINED_ID)
id.subscribe(newId => localStorage.id = newId)