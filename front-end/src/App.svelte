<script>
  import { UNDEFINED_ID } from "./constants.js"
  import Auth from "./Auth.svelte"
  import Main from "./Main.svelte"
  import Router from "svelte-spa-router"
  import routes from "./routes"
  import { id } from "./store"
  import Modal from "svelte-simple-modal"
</script>

<Router {routes} />

{#if $id === UNDEFINED_ID}
  <Auth />
{:else}
  <Modal>
    <Main />
  </Modal>
{/if}
