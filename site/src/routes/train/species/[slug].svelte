<script context="module">
  export async function load({ page, fetch }) {
    const url = `/train/species/${page.params.slug}.json`;
    const res = await fetch(url);
    if (res.ok) {
      return {
        props: {
          slug: page.params.slug,
          examples: await res.json()
        }
      };
    }
    return {
      status: res.status,
      error: new Error(`Could not load ${url}`)
    };
  }
</script>

<script>
  export let slug;
  export let examples;
</script>

<svelte:head>
  <title>train: {slug}</title>
</svelte:head>

<h1>{slug}</h1>

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
