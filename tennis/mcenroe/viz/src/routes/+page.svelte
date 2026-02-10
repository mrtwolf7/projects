<script>
  import SecMatchesWTime from '$lib/sec_matches_w_time.svelte';
  import PercOverall from '$lib/perc_overall.svelte';
  import PercOverallWon from '$lib/perc_overall_w.svelte';
</script>

<article>
  <h1>Serve like McEnroe</h1>
  <p> <em> "Sarei disposto ad avere 37.2 per tutta la vita in cambio della seconda palla di McEnroe" - Giuseppe Viola </em><br>
  <em>(Roughly translates to "I'd be happy to be under the weather my whole life if I could serve a second ball like McEnroe")<em>
  </p>
  <p> 
    This is what in the 80s, a famous italian sport journalist once said about John McEnroe. Among the other things, the tennis
    player was know to have a phenomal second serve, which is usually when tennis players have to serve safe not to conceed a point to the opponents, 
    being then a very stressful situation for who serves the ball. <br>
    Now, I do not have the data to prove if this affirmation is true and to what extent (I only have data from 1991 onwards), like is it true for all the years,
    is it true for all the surfaces etc, etc, however, I have enough data to answer another question:
    <strong> who is the tennis with the best second serve these days? </strong>
  </p>
  <p>
    There are multiple ways in which we can answer to this question, let's start by founding out
    who has the highest % of points won on a second serve game.
  </p>
  <PercOverall />
  <p>
    I filtered the data to the players who have played at least 300 matches and decided to show
    only the top 15.
    It is interesting to notice that the top 3 players of all time (by numbers of Grand Slam won) are not
    there. The highest percentage over all these years is 19.8%, but there is not a player who is
    clearly much better than the others. <br>
    Let's be more specific with the question: let's find out who has the highest percentage of points won with second serve
    only in won matches.
  </p>
  <PercOverallWon />

  <SecMatchesWTime />

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
