<script>
import Client from "./client";

  import { id } from "./store"
  
  export let otherId;
  let username = ""
  let numClips = 0
  let following = isFollowing()

  function isNotViewingOwnProfile() {
    return otherId !== parseInt($id)
  }

  function getClipsString() {
    return numClips === 1 ? "clip" : "clips"
  }

  async function getUserInfo() {
    let res = await Client.get(`/user/${otherId}`)
    username = res.data.user
    numClips = res.data.numClips
  }

  async function isFollowing() {
    let res = await Client.get(`/follow/${parseInt($id)}/${otherId}`)
    following = res.data.following
  }

  async function follow() {
    let res = await Client.put(`/follow/${parseInt($id)}/${otherId}`)
    following = res.data.following
  }

  async function unfollow() {
    let res = await Client.del(`/follow/${parseInt($id)}/${otherId}`)
    following = res.data.following
  }
</script>

<div id="container">
  <img class="logo" src="images/hypers.png" alt="Hypers" title="Hypers" />

  <h1>{username}</h1>

  {#await getUserInfo() then _}
    <span class="numClips">Uploaded {numClips} {getClipsString()}</span>
  {/await}
  
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