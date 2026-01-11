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
    The first angle I looked at was tournament predictability: <strong>are Grand Slam tournaments 
    more predictable these days than they were in the past? </strong>
    To do so, I started by looking at the ratio of matches won by players with the higher 
    ranking from 1975 to 2024. Higher values represent lower predictability:
  </p>

  <Timeline />

  <p>
    Looking at the plot, you can see that the "favourite players" ratio increases significantly
    from the 1970s up to 1990s, it continues to increase slower up to 2010s and then it softly decreases.
    In numbers, while on average in the 70s the ratio was around 0.3 - meaning the 70% of the matches
    were won by players with lower ranking - it went up to 0.5 in the 80s, up to almost 0.75 in the 10s
    and then decrease to 0.7 in the 20s.
  </p>
  <p>
    While this is already telling us something about historical trends for all matches in the tournaments
    I wanted to take a closer look at the tournament predictability by analysing only the matches in the second week
    (from round of 16 onwards) - come on, let's be honest, these are the games we are more interested in.
  </p>

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
