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
  import Table from "../../../lib/Table.svelte";
  export let slug;
  export let examples;
  export let info = {};
  export let metadata;

  onMount(async () => {
    let resp;
    resp = await fetch(`/data/metadata/${slug}/info.json`);
    info = await resp.json();
    resp = await fetch(`/data/metadata/${slug}/metadata.json`);
    metadata = await resp.json();
  });

  $: columns = [
    {
      name: "name"
    },
    {
      name: "motif",
      format: (row) => {
        return `<audio
            preload="none"
            controls
            src="/data/motif/train_short_audio/${slug}/${row.name}/motif.0.ogg"
          />`;
      },
      html: true
    },
    {
      name: "motif pair",
      format: (row) => {
        return `<audio
            preload="none"
            controls
            src="/data/motif/train_short_audio/${slug}/${row.name}/motif.1.ogg"
          />`;
      },
      html: true
    }
  ];
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

{#if metadata}
  <Table data={metadata} {columns} paginationSize={10} />
{/if}
