<script lang="ts">
    import FstReconstruction from "./FstReconstruction.svelte";
    import type { FstComparison } from "./types";
    import VirtualList from "@sveltejs/svelte-virtual-list";

    export let data: FstComparison;
    export let langsUnderStudy: string[];

    // The titles of our chapters. Don't know why the server doesn't just return these...
    let chapterTitles = {i:'Initials', m:'Medials', r:'Rimes', t:'Tones'};

    // Allows us to set the background color as necessary for visual status updates
    const getBg = (status: string) => {
        if (status === "smiling") {
            return "lightgreen"
        } else if (status === "frowning") {
            return "lightcoral"
        } else {
            return "white"
        }
    }
    
    // While testing, useful to know what we should be seeing.
    //console.log(data);

    // Construct data into a format that works well for virtual lists
    let listData = [];

    $: if (data) {
        const baseList = [].concat(...Object.keys(data.chapters).map(id => {
            return [{ isTitle: true, title: chapterTitles[id] }, ...data.chapters[id]];
        }));

        if (data.missing_transducers.length > 0) {
            const missingIndices = data.missing_transducers.map(n => langsUnderStudy.indexOf(n));
            listData = baseList.map(item => {
                if (item.isTitle) {
                    return item;
                }
                const clonedRows = item.rows.map(row => {
                    const oldRecs = [...row.old_reconstructions];
                    const newRecs = [...row.new_reconstructions];
                    for (const missingIndex of missingIndices) {
                        if (missingIndex >= 0) {
                            oldRecs.splice(missingIndex, 0, "");
                            newRecs.splice(missingIndex, 0, "");
                        }
                    }
                    return { ...row, old_reconstructions: oldRecs, new_reconstructions: newRecs };
                });
                return { ...item, rows: clonedRows };
            });
        } else {
            listData = baseList;
        }
    }

    //console.log('listData', listData)
</script>

<div>
    <!-- Goes through each chapter (i, m, r, t) and its sections as one big list -->
    <!-- Using a virtual list means we save a LOT of performance -->
    <VirtualList items={listData} let:item >
        {#if item.isTitle}
        <h1>{item.title}</h1>
        {:else}
        <h2>{item.title}</h2>
        <!-- Lay it out in a big table... -->
        <table>
            <tr>
                <th>Gloss</th>
                {#each langsUnderStudy as lang}
                    <th>{lang}</th>
                {/each}
            </tr>
            {#each item.rows as row}
            <tr style="background-color:{getBg(row.status)};">
                <td>{row.gloss ? `"${row.gloss}"` : ""}</td>
                {#each row.ipas as ipa}
                <td class="sourceipa"><b>{ipa}</b></td>
                {/each}
            </tr>
            <tr style="background-color:{getBg(row.status)};">
                <td>{row.old_reconstruction ? row.old_reconstruction : ""}</td>
                {#each row.old_reconstructions as recs}
                    <td>
                        <FstReconstruction recs={recs.length > 0 ? recs.split(", "): []} />
                    </td>
                {/each}
            </tr>
            <tr class="last" style="background-color:{getBg(row.status)};">
                <td>{row.new_reconstruction ? row.new_reconstruction : ""}</td>
                {#each row.new_reconstructions as recs}
                    <td>
                        <FstReconstruction recs={recs.length > 0 ? recs.split(", "): []} />
                    </td>
                {/each}
                <td>
                    {(row.status == "smiling") ? '😊' : (row.status == "frowning") ? '🙁' : ''}
                </td>
            </tr>
            {/each}
        </table>
        {/if}
    </VirtualList>
</div>


<style>
    table {
        border-collapse: collapse;
        width: 100%;
    }

    table, th {
        border: solid black;
        border-width: 1px 0 1px 0;
    }

    tr.last > td {
        padding-bottom: 1em;
    }

    td {
        text-align: center;
    }

    div {
        overflow: auto;
        height: 100%;
    }

    h2 {
        text-align: center;
    }
</style>
