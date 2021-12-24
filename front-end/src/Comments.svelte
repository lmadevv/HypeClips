<script>
  import { id } from "./store"
  import Client from "./client"
  import formatDateString from "./utils"

  export let clipId

  let comment

  function refreshPage() {
    window.location.reload()
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
      {comment.comment}
      <span class="date">{formatDateString(comment.date)} by </span><span
        class="author">@{comment.author}</span
      >
    {/each}
  {/await}
</div>

<style>
  .date {
    color: gray;
  }

  .author {
    color: #ff3e00;
  }
</style>
