<script>
  import { onMount } from "svelte";
  import localforage from "localforage";

  export let slug;
  export let names;
  export let labels;

  const key = `train.motif.${slug}.v1`;

  $: labels && localforage.setItem(key, labels);

  onMount(async () => {
    labels =
      (await localforage.getItem(key)) ||
      Object.fromEntries(
        names
          .map((name) => [`${name}.motif.0`, { is_valid: false }])
          .concat(names.map((name) => [`${name}.motif.1`, { is_valid: false }]))
      );
  });
</script>
