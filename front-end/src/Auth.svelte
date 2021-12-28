<script>
  import {
    useForm,
    validators,
    HintGroup,
    Hint,
    maxLength,
    required,
  } from "svelte-use-form"
  import Client from "./client"
  import { id } from "./store"

  const form = useForm()

  let username = ""
  let password = ""

  async function request(endpoint) {
    try {
      let res = await Client.post(endpoint, { username, password })
      id.set(res.data.id)
    } catch (e) {
      alert("An error occurred!")
    }
  }
</script>

<form use:form>
  <img class="logo" src="images/hypers.png" alt="Hypers" title="Hypers" />

  <input
    type="text"
    name="username"
    bind:value={username}
    placeholder="username"
    use:validators={[required, maxLength(20)]}
  />
  <HintGroup for="username">
    <Hint on="required">Username is required</Hint>
    <Hint on="maxLength">Username may not exceed 20 characters</Hint>
  </HintGroup>

  <br />

  <input
    type="password"
    name="password"
    bind:value={password}
    placeholder="password"
    use:validators={[required, maxLength(40)]}
  />
  <HintGroup for="password">
    <Hint on="required">Password is required</Hint>
    <Hint on="maxLength">Password may not exceed 40 characters</Hint>
  </HintGroup>

  <br />

  <button
    disabled={!$form.valid}
    on:click|preventDefault={request.bind(this, "/login")}>Login</button
  >
  <button
    disabled={!$form.valid}
    on:click|preventDefault={request.bind(this, "/register")}>Register</button
  >
</form>

<style>
  form {
    text-align: center;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  .logo {
    width: 256px;
    height: 256px;
  }
</style>
