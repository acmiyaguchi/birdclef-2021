<script context="module">
  export async function load({ page, fetch }) {
    const { slug } = page.params;
    const res = await fetch(`/train/species/${slug}.json`);
    if (res.ok) {
      return {
        props: {
          slug: slug,
          examples: await res.json()
        }
      };
    }
    return {
      status: res.status,
      error: new Error(`Could not load data for ${slug}`)
    };
  }
</script>

<script>
  import { onMount } from "svelte";
  export let slug;
  export let examples;
  export let info = {};
  export let metadata = [];

  onMount(async () => {
    let resp;
    resp = await fetch(`/data/metadata/${slug}/info.json`);
    info = await resp.json();
    resp = await fetch(`/data/metadata/${slug}/metadata.json`);
    metadata = await resp.json();
  });
</script>

<svelte:head>
  <title>train: {slug}</title>
</svelte:head>

<h1>{slug}</h1>
<p>
  Common Name: <a href="https://www.wikipedia.org/wiki/{info.common_name}" target="_blank"
    >{info.common_name}</a
  >
</p>
<p>Scientific Name: {info.scientific_name}</p>

<a href="/train">back to species</a>

<table>
  <thead>
    <tr>
      <th>name</th>
      <th>motif</th>
      <th>motif pair</th>
    </tr>
  </thead>
  <tbody>
    {#each examples as example}
      <tr>
        <td>{example}</td>
        <td>
          <audio
            preload="none"
            controls
            src="/data/motif/train_short_audio/{slug}/{example}/motif.0.ogg"
          /></td
        >
        <td>
          <audio
            preload="none"
            controls
            src="/data/motif/train_short_audio/{slug}/{example}/motif.1.ogg"
          /></td
        >
      </tr>
    {/each}
  </tbody>
</table>

<style>
  table,
  th,
  td {
    border: 1px solid black;
  }
  table {
    border-collapse: collapse;
  }
</style>
