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

{species}
