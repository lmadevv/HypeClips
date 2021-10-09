<script>
  import { id } from "./store"
  import Client from "./client"
  import VideoPlayer from "svelte-video-player"

  let clipSelector

  function refreshPage() {
    window.location.reload()
  }

  async function uploadClip(e) {
    let videoFile = e.target.files[0]

    let formData = new FormData()
    formData.append("file", videoFile)
    formData.append("authorId", parseInt($id))

    await Client.put("/clips", formData)
    refreshPage()
  }

  async function deleteClip(id) {
    await Client.del(`/clips/${id}`)
    refreshPage()
  }

  async function getClipIds() {
    let res = await Client.get("/clips")
    return res.data
  }

  function logout() {
    $id = "undefined"
  }
</script>

<div id="container">
  <h1>Hypers</h1>

  <img
    on:click={() => clipSelector.click()}
    class="big-icon"
    src="images/upload.png"
    alt="Upload clip"
  />
  <input
    type="file"
    accept=".mp4"
    on:input|preventDefault={uploadClip}
    bind:this={clipSelector}
  />

  <img
    on:click={logout}
    class="big-icon"
    src="images/logout.png"
    alt="Log out"
  />

  {#await getClipIds() then clipIds}
    {#each clipIds as clipId}
      <div class="clip">
        <VideoPlayer source="{Client.serverUrl}clips/{clipId}" />
        <img
          on:click={() => deleteClip(clipId)}
          class="small-icon"
          src="images/delete.png"
          alt="Delete clip"
        />
      </div>
    {/each}
  {/await}
</div>

<style>
  .clip {
    padding: 1em;
  }

  .big-icon {
    width: 48px;
    height: 48px;
    cursor: pointer;
  }

  .small-icon {
    width: 32px;
    height: 32px;
    cursor: pointer;
  }

  #container {
    text-align: center;
    padding: 1em;
    max-width: 720px;
    margin: 0 auto;
  }

  input[type="file"] {
    display: none;
  }

  h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-weight: 100;
  }

  h1 {
    font-size: 4em;
  }
</style>
