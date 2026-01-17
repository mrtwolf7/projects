<script>
  import Timeline from '$lib/timeline_faves.svelte';
  import TimelineRounds from '$lib/timeline_faves_round.svelte';
  import AvgWinnerGames from '$lib/winner_games.svelte';
  import AvgDiffGames from '$lib/games_diff.svelte';
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
    (from round of 16 onwards) - come on, let's be honest, these are the games we are more interested in:
  </p>
  <TimelineRounds />
  <p>
    On average, the favourites ratio is between 0.05-0-1 higher in these tournaments rounds than in the overall tournament,
    meaning the earliest rounds are where surprising results are more likely to happen.
  </p>
  <p>
    There is not a big difference between the R16, QF, SF and F - values are very similar, between
    0.68 up to 0.77. There is not any notable difference in the tournaments either: Roland Garros seems to
    be slightly more unpredictable than the other across the 80s and 90s, then this role is played by the 
    Australian Open in the 00s and US Open in the 10s.
    Roughly speaking this means that <strong> from R16 onwards the player with the highest ranking wins the match 
    around 70% or more of the time </strong>.
  </p>
  <p>
    Ok, the matches are usually won by the player with the higher ranking, but are they interesting? 
    Are they tight?
  </p>
  <p>
    To answer this question, I have computed what is the average number of games won by the winner for every match.
    The minimum is 18 (it's the result of a three set match) and every number close to it shows no much competitiveness
    in the match:
  </p>
  <AvgWinnerGames />
  <p>
    <strong>The average across the tournaments across the decades is very similar and stable around 21 games </strong>, meaning that
    it takes on average more than 3 sets for the winner to win the match.
    Ok, but how tight were this sets? There is quite a big difference if a set is 6-0 or 6-4 and this metric does not 
    catch it.
  </p>
  <p>
    To find out about it, I have analysed the average games difference:
  </p>
  <AvgDiffGames />
  <p>
    While there was quite a relevant difference between the tournaments during the 80s,
    this become very small in the 90s and 00s when all the Grand Slam tournaments were following 
    a very similar behaviour.
    The US Open and Wimbledon are the ones showing more stable trends of a decreasing games difference
    across the decades: this is true for Roland Garros and Australian Open as well, but they show
    less stable trends.
    <strong> Overall the games difference is decreasing </strong> for the Grand Slam tournaments, going from more
    than 7 games difference in the 70s to 6 (or even less) in the 20s: this suggests that <strong> the matches
    are becoming tighter and tighter. </strong>
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
