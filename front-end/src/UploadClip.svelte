<script>
  import { id } from "./store"
  import Client from "./client"

  let clipSelector
  let title
  let description
  let videoFile

  function refreshPage() {
    window.location.reload()
  }

  function setVideoFile(e) {
    videoFile = e.target.files[0]
  }

  async function uploadClip() {
    if (title === undefined || title === "") {
      alert("Title is required.")
      return
    }

    if (videoFile === undefined) {
      alert("Video file is required.")
      return
    }

    let formData = new FormData()
    formData.append("authorId", parseInt($id))
    formData.append("title", title)
    formData.append("description", description)
    formData.append("file", videoFile)

    await Client.put("/clips", formData)
    refreshPage()
  }
</script>

<div id="container">

  <img class="logo" src="images/hypers.png" alt="Hypers" title="Hypers" />

  <form>
    <label for="title">Title:</label>
    <input type="text" id="title" name="title" bind:value={title} />
    <label for="description">Description:</label>
    <input
      type="text"
      id="description"
      name="description"
      bind:value={description}
    />
  </form>

  <button on:click={() => clipSelector.click()}>Choose clip</button>
  {#if videoFile !== undefined}
    {videoFile.name}
  {/if}

  <input
    type="file"
    accept=".mp4"
    on:input|preventDefault={setVideoFile}
    bind:this={clipSelector}
  />

  <br />
  <button on:click={() => uploadClip()}>Upload clip</button>
</div>

<style>
  input[type="file"] {
    display: none;
  }

  #container {
    margin-left: auto;
    margin-right: auto;
    display: block;
    width: 50%;
  }

  .logo {
    width: 128px;
    height: 128px;
  }
</style>
