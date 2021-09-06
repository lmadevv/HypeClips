<script>
	import { id } from "./store"

  function logout() {
    $id = "undefined"
  }
</script>

<h1>You are logged in! The user ID is {$id}</h1>

<button on:click={logout}>Log out</button>