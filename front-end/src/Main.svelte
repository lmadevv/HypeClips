<script>
  import { id } from "./store"
  import Client from "./client"
  import VideoPlayer from "svelte-video-player"
  import UploadClip from "./UploadClip.svelte"
  import Profile from "./Profile.svelte"
  import { getContext } from "svelte"

  const { open } = getContext("simple-modal")

  function refreshPage() {
    window.location.reload()
  }

  function openUploadClipModal() {
    open(UploadClip)
  }

  function openProfileModal() {
    open(Profile, { otherId: 123 })
  }

  function formatDateString(dateString) {
    // Treat the date string as UTC.
    dateString += ` GMT+00:00`

    const date = new Date(dateString)
    const time =
      date.getHours() >= 13
        ? `${date.getHours() - 12}:${date.getMinutes()} PM`
        : `${date.getHours()}:${date.getMinutes()} AM`
    return `${date.toDateString().substring(4)}, ${time}`
  }

  async function deleteClip(id) {
    await Client.del(`/clips/${id}`)
    refreshPage()
  }

  async function getClipIds() {
    let res = await Client.get("/clips")
    return res.data
  }

  async function getClipInfo(id) {
    let res = await Client.get(`/clips/info/${id}`)
    return res.data
  }

  function logout() {
    $id = "undefined"
  }
</script>

<div id="container">
  <h1>Hypers</h1>

  <img
    on:click={openUploadClipModal}
    class="big-icon"
    src="images/upload.png"
    alt="Upload clip"
    title="Upload clip"
  />

  <img
    on:click={logout}
    class="big-icon"
    src="images/logout.png"
    alt="Log out"
    title="Log out"
  />

  {#await getClipIds() then clipIds}
    {#each clipIds as clipId}
      <div class="clip">
        {#await getClipInfo(clipId) then clipInfo}
          <h2>{clipInfo.title}</h2>
          <p>{clipInfo.description}</p>
          <span class="date">{formatDateString(clipInfo.date)}</span>
          <span class="author" on:click={openProfileModal}>@{clipInfo.author}</span>
        {/await}

        <VideoPlayer source="{Client.serverUrl}clips/{clipId}" />

        <img
          on:click={() => deleteClip(clipId)}
          class="small-icon"
          src="images/delete.png"
          alt="Delete clip"
          title="Delete clip"
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

  h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-weight: 100;
    font-size: 4em;
  }

  .date {
    color: gray;
  }

  .author {
    color: #ff3e00;
    cursor: pointer;
  }
</style>
