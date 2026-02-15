<script lang="ts">
  export let project;
</script>

<div class="card">
  <h3>{project.title}</h3>

  <p>{project.description}</p>
  <p><strong>Stack:</strong> {project.stack.join(", ")}</p>

  <div class="buttons">
    <a href={project.demoUrl} target="_blank">Live demo</a>
    <a href={project.repoUrl} target="_blank">Code</a>
  </div>
</div>

<style>
  .card {
    padding: 1.5rem;
    border: 1px solid #ddd;
    border-radius: 12px;
    margin-bottom: 1rem;
  }

  .buttons a {
    margin-right: 1rem;
    font-weight: bold;
  }
</style>
