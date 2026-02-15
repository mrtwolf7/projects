<script lang="ts">
  import { projects } from '$lib/data/projects';
  import ProjectCard from '$lib/components/ProjectCard.svelte';
</script>

<h1>Tiziano Lupo</h1>
<p> Hi, this is just my space where I like to answer questions by using data</p>


<h2>Projects</h2>

{#each projects as project}
  <ProjectCard {project} />
{/each}

<style>
  h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
  }

  h2 {
    margin-top: 2rem;
  }

  p {
    font-size: 1.2rem;
    color: #555;
  }
</style>