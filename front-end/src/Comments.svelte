<script>
  import { id } from "./store"
  import Client from "./client"
  import formatDateString from "./utils"
  import { getContext } from "svelte"
  import Profile from "./Profile.svelte"

  const { open } = getContext("simple-modal")

  export let clipId

  let comment

  function refreshPage() {
    window.location.reload()
  }

  function openProfileModal(clickedId) {
    open(Profile, { otherId: clickedId })
  }

  async function postComment() {
    if (comment === undefined || comment === "") {
      alert("Comment is required.")
      return
    }

    await Client.put(`/comments/${clipId}`, {
      authorId: parseInt($id),
      comment,
    })
    refreshPage()
  }

  async function getComments() {
    let res = await Client.get(`/comments/${clipId}`)
    console.log(res.data)
    return res.data
  }
</script>

<div id="container">
  <img class="logo" src="images/hypers.png" alt="Hypers" title="Hypers" />

  <form>
    <textarea
      type="text"
      id="comment"
      name="comment"
      placeholder="Add a comment..."
      bind:value={comment}
    />
    <br />
  </form>
  <button on:click={postComment}>Post comment</button>

  <br />
  <br />

  {#await getComments() then comments}
    {#each comments as comment}
      <div class="comment">
        {comment.comment}
        <br />
        <span class="date">{formatDateString(comment.date)} by </span><span
          class="author" on:click={openProfileModal.bind(this, comment.authorId)}>@{comment.author}</span>
      </div>
      <br />
    {/each}
  {/await}
</div>

<style>
  #container {
    margin-left: auto;
    margin-right: auto;
    display: block;
    width: 50%;
    word-wrap: break-word;
  }

  .logo {
    width: 128px;
    height: 128px;
  }

  .date {
    color: gray;
  }

  .author {
    color: #ff3e00;
    cursor: pointer;
  }
</style>
