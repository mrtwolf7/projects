<script>
  import Timeline from '$lib/timeline_faves.svelte';
</script>

<article>
  <h1>Is tennis becoming more boring?</h1>

  <p>
    Ok, I hear you out everyone "Hey tennis IS boring! And it has always been!" - well, 
    if you never found yourself lost in one of Federer's drop shots, then ok, I agree with you:
    but at that point the problem is not tennis really.
  <p>
  <p>
    Anyway what I want to answer here is if tennis is becoming MORE boring: to do so I analysed data, 
    looked at different metrics.
    I focused on ATP only, tarting by looking at Grand Slams, because arguably the most important
    tournaments.
  </p>
  <p>
    THe first angle I looked at was tournament predictability: <strong>are Grand Slam tournaments 
    more predictable these days than they were in the past? </strong>
    To do so, I started by looking at the percentage of matches won by players with the higher 
    ranking from 1975 to 2024. Higher values represent lower predictability:
  </p>

  <Timeline />
</article>

<style>
  article {
    max-width: 960px;
    margin: 3rem auto;
    padding: 0 1rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  p {
    line-height: 1.6;
    margin-bottom: 1rem;
    color: #444;
  }
</style>
