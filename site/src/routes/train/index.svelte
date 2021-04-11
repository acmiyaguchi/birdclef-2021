<script context="module">
	export async function load({ page, fetch }) {
		const url = '/train/species.json';
		const res = await fetch(url);
		if (res.ok) {
			return {
				props: {
					species: await res.json()
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
	export let species;
</script>

<svelte:head>
	<title>training motifs</title>
</svelte:head>

<h1>training motifs</h1>
<a href="/">back to the index</a>

<ul>
	{#each species as sp}
		<li><a href="/train/species/{sp}">{sp}</a></li>
	{/each}
</ul>
