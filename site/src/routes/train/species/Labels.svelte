<script>
  import { onMount } from "svelte";
  import localforage from "localforage";
  import filesaver from "file-saver";
  import { sortBy, mapValues } from "lodash";

  export let slug;
  export let names;
  export let labels;

  const key = `train.motif.${slug}.v1`;

  $: labels && localforage.setItem(key, labels);

  onMount(async () => {
    labels = mapValues(
      (await localforage.getItem(key)) ||
        Object.fromEntries(
          names
            .map((name) => [`${name}.motif.0`, {}])
            .concat(names.map((name) => [`${name}.motif.1`, {}]))
        ),
      (value) => ({
        is_valid: true,
        timestamp: null,
        ...value
      })
    );
  });

  function save(labels) {
    let data = sortBy(
      Object.entries(labels).map(([key, value]) => ({
        name: key,
        ...value
      })),
      ["name"]
    );
    let blob = new Blob([JSON.stringify(data)], { type: "application/json" });
    filesaver.saveAs(blob, `${key}.labels.json`);
  }
</script>

<button on:click={() => save(labels)}>Save labels</button>
