<script>
  import { id } from "./store"
  import Client from "./client"
  import VideoPlayer from "svelte-video-player"
  import { getContext } from "svelte"
  import UploadClip from "./UploadClip.svelte"
  import Comments from "./Comments.svelte"
  import Profile from "./Profile.svelte"
  import formatDateString from "./utils"

  const { open } = getContext("simple-modal")

  let isHomeFeed = true

  function refreshPage() {
    window.location.reload()
  }

  function openUploadClipModal() {
    open(UploadClip)
  }

  function openProfileModal() {
    open(Profile, { otherId: 123 })
  }

  function openCommentsModal(clipId) {
    open(Comments, { clipId })
  }

  function toggleFeed() {
    isHomeFeed = !isHomeFeed
  }

  async function deleteClip(id) {
    await Client.del(`/clips/${id}`)
    refreshPage()
  }

  async function getClipIds() {
    let endpoint = isHomeFeed ? "/clips" : `/follow/clips/${parseInt($id)}`  
    let res = await Client.get(endpoint)
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
  <img class="logo" src="images/hypers.png" alt="Hypers" title="Hypers" />

  <br />

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

  <br />
  <br />

  {#if isHomeFeed}
    <img class="big-icon" src="images/home-feed.png" on:click={toggleFeed} title="View latest clips" alt="View latest clips" />
  {:else}
    <img class="big-icon" src="images/follow-feed.png" on:click={toggleFeed} title="View latest clips from users you are following" alt="View latest clips from users you are following" />
  {/if}

  <!-- Duplicated code here for simplicity. To remove code duplication, create a new Svelte component and send in clip info as props. -->
  {#if isHomeFeed}
    {#await getClipIds() then clipIds}
      {#each clipIds as clipId}
        <div class="clip">
          {#await getClipInfo(clipId) then clipInfo}
            <h2>{clipInfo.title}</h2>
            <p>{clipInfo.description}</p>
            <span class="date"
              >{formatDateString(clipInfo.date)} by
            </span><span class="author" on:click={openProfileModal}>@{clipInfo.author}</span>
          {/await}

          <VideoPlayer source="{Client.serverUrl}clips/{clipId}" />

          <img
            on:click={() => openCommentsModal(clipId)}
            class="small-icon"
            src="images/comment.png"
            alt="View clip comments"
            title="View clip comments"
          />
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
  {:else}
    {#await getClipIds() then clipIds}
      {#each clipIds as clipId}
        <div class="clip">
          {#await getClipInfo(clipId) then clipInfo}
            <h2>{clipInfo.title}</h2>
            <p>{clipInfo.description}</p>
            <span class="date"
              >{formatDateString(clipInfo.date)} by
            </span><span class="author" on:click={openProfileModal}>@{clipInfo.author}</span>
          {/await}

          <VideoPlayer source="{Client.serverUrl}clips/{clipId}" />

          <img
            on:click={() => openCommentsModal(clipId)}
            class="small-icon"
            src="images/comment.png"
            alt="View clip comments"
            title="View clip comments"
          />
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
  {/if}
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

  .logo {
    width: 256px;
    height: 256px;
  }

  .date {
    color: gray;
  }

  .author {
    color: #ff3e00;
    cursor: pointer;
  }
</style>
