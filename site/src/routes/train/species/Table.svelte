<script>
  import { chunk } from "lodash";
  import Labels from "./Labels.svelte";

  export let slug;
  export let data = [];
  export let paginationSize = null;

  let idx = 0;
  $: chunked = paginationSize ? chunk(data, paginationSize) : [data];
  $: total = data.length;
  $: pages = chunked.length;

  let labels;
  $: names = data.map((row) => row.name);

  function prev() {
    idx > 0 ? idx-- : null;
  }
  function next() {
    idx < pages - 1 ? idx++ : null;
  }
</script>

<Labels {slug} {names} bind:labels />

<div>
  <table cellpadding="5">
    <thead>
      <tr>
        <th>name</th>
        <th>label (valid)</th>
        <th>motif</th>
        <th>motif pair</th>
        <th>source audio</th>
        <th>date</th>
        <th>rating</th>
        <th>type</th>
        <th>secondary labels</th>
      </tr></thead
    >
    <tbody>
      {#each chunked[idx] as row}
        <tr>
          <td>
            <a href={row.url} target="_blank">{row.name}</a>
          </td>
          <td>
            {#if labels}
              <div
                style={labels[`${row.name}.motif.0`]["timestamp"] ? "background:lightgreen" : null}
              >
                <label
                  ><input
                    type="checkbox"
                    bind:checked={labels[`${row.name}.motif.0`]["is_valid"]}
                    onchange={() => (labels = { ...labels })}
                  />
                  motif</label
                >
              </div>
              <div
                style={labels[`${row.name}.motif.1`]["timestamp"] ? "background:lightgreen" : null}
              >
                <label>
                  <input
                    type="checkbox"
                    bind:checked={labels[`${row.name}.motif.1`]["is_valid"]}
                    onchange={() => (labels = { ...labels })}
                  />pair</label
                >
              </div>
            {/if}
          </td>
          <td>
            <!-- svelte-ignore a11y-media-has-caption -->
            <audio
              preload="none"
              controls
              on:play={() =>
                (labels[`${row.name}.motif.0`]["timestamp"] = new Date().toISOString())}
              src="/data/motif/train_short_audio/{slug}/{row.name}/motif.0.ogg"
            /></td
          >
          <td>
            <!-- svelte-ignore a11y-media-has-caption -->
            <audio
              preload="none"
              controls
              on:play={() =>
                (labels[`${row.name}.motif.1`]["timestamp"] = new Date().toISOString())}
              src="/data/motif/train_short_audio/{slug}/{row.name}/motif.1.ogg"
            />
          </td>
          <td>
            <details>
              <!-- svelte-ignore a11y-media-has-caption -->
              <audio
                preload="none"
                controls
                src="/data/input/train_short_audio/{slug}/{row.name}.ogg"
              />
            </details>
          </td>
          <td>{row.date}</td>
          <td>{row.rating}</td>
          <td>{row.type}</td>
          <td>{row.secondary_labels}</td>
        </tr>
      {/each}
    </tbody>
  </table>
  <div>
    {#if pages > 1}
      <button disabled={!(idx > 0)} on:click={prev}>Prev</button>
      <button disabled={!(idx < pages - 1)} on:click={next}>Next</button>
      <span>{total} rows - page {idx + 1} of {pages}</span>
    {/if}
  </div>
</div>

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
