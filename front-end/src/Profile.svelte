<script>
  import { id } from "./store"
  
  export let otherId;
  let username = "Foo"
  let numClips = 0
  let following = false

  function isNotViewingOwnProfile() {
    // TODO: Compare stored user ID and otherId.
    return true
  }

  function follow() {
    // TODO: Make API call.
    following = true
  }

  function unfollow() {
    // TODO: Make API call.
    following = false
  }

  function getClipsString() {
    return numClips === 1 ? "clip" : "clips"
  }
</script>

<div id="container">
  <img class="logo" src="images/hypers.png" alt="Hypers" title="Hypers" />

  <h1>{username}</h1>
  <span class="numClips">Uploaded {numClips} {getClipsString()}</span>
  
  <br />
  <br />
  
  <!-- Do not show the follow button if a user is viewing their own profile. -->
  {#if isNotViewingOwnProfile()}
    {#if !following}
      <button
        on:click|preventDefault={follow}>Follow</button
      >
    {:else}
      <button
        on:click|preventDefault={unfollow}>Unfollow</button
      >
    {/if}
  {/if}  
</div>

<style>
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

  h1 {
    color: #ff3e00;
    padding: 0;
    margin: 0;
    font-weight: normal;
  }

  .numClips {
    color: gray;
  }
</style>