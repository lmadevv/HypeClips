<script>
  import { id } from "./store"
  import Client from "./client"

  let clipSelector
  let clipName = ""

  function uploadClip(e) {
    let videoFile = e.target.files[0]
    clipName = videoFile.name

    let formData = new FormData()
    formData.append("file", videoFile)

    Client.put("/clips", formData)
  }

  function logout() {
    $id = "undefined"
  }
</script>
<div id="container">
  <h1>Hypers</h1>
  <h2>You are logged in! The user ID is {$id}</h2>

  <button on:click={() => clipSelector.click()}>Upload clip</button>
  <input
    type="file"
    accept=".mp4"
    on:input|preventDefault={uploadClip}
    bind:this={clipSelector}
  />
  {#if clipName}
    <p>Uploaded clip {clipName}</p>
  {/if}

  <button on:click={logout}>Log out</button>
</div>

<style>
  #container {
    text-align: center;
    padding: 1em;
    max-width: 720px;
    margin: 0 auto;
  }

  input[type="file"] {
    display: none;
  }

  h1, h2 {
    color: #ff3e00;
    text-transform: uppercase;
    font-weight: 100;
  }

  h1 {
    font-size: 4em;
  }
</style>
