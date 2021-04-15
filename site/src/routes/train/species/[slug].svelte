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
  import Table from "./Table.svelte";
  import localforage from "localforage";

  export let slug;
  export let examples = [];

  const key = `train.motif.${slug}.v1`;
  let info = {};
  let metadata = [];
  let labels;

  $: labels && localforage.setItem(key, labels);

  onMount(async () => {
    let resp;
    resp = await fetch(`/data/metadata/${slug}/info.json`);
    info = await resp.json();
    resp = await fetch(`/data/metadata/${slug}/metadata.json`);
    metadata = await resp.json();

    labels =
      (await localforage.getItem(key)) ||
      Object.fromEntries(examples.map((name) => [name, { is_valid: True }]));
  });

  $: data = metadata.filter((row) => examples.includes(row.name));
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

{#if data.length}
  <Table {slug} {data} paginationSize={10} />
{/if}
