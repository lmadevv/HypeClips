<script>
  import { id } from "./store"
  import Client from "./client"

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
      comment
    })
    // refreshPage()
  }

  async function getComments() {
    let res = await Client.get(`/comments/${clipId}`)
    return res.data
  }
</script>

<div id="container">
  <form>
    <textarea type="text" id="comment" name="comment" placeholder="Add a comment..." bind:value={comment} />
    <br>
  </form>
  <button on:click={postComment}>Post comment</button>

  {#await getComments() then comments}
    {#each comments as comment}
      <p>{comment.comment}</p>
    {/each}
  {/await}
</div>

<style>
</style>
