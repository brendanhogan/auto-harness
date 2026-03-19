was curious about Poetiq's "meta-system" approach — they claim you can take any frontier model and make it dramatically better by building intelligence on top of it rather than into it. so i threw together a quick experiment to test the basic idea. can you automatically build a harness around a small model (Qwen 7B) to make it solve math competition problems it can't solve alone?

used AIME 2024 as the benchmark — 30 problems, split 15 train / 15 test. these are hard competition math problems, the kind where even strong models struggle.

three stages, each one layering on top of the last:

**stage 1 — baseline.** just prompt Qwen 7B with "solve this AIME problem, think step by step." run it 20 times per problem. result on the test set: 0%. literally zero. out of 300 completions across 15 problems, not a single correct answer. 7B models just can't do AIME.

**stage 2 — meta-prompt optimization.** have GPT-5.2 look at where Qwen fails on the training problems and iteratively rewrite the prompt. it came up with a structured prompt: restate the problem first, name the math topic, define variables before doing algebra, if you're stuck after 12 lines switch approach, verify by plugging back in. ran 3 iterations of this. result: 1.7% on test — still bad, but the model is now occasionally producing correct answers in its 20 attempts. importantly, the prompt gains didn't transfer well from train to test, which is interesting in itself.

**stage 3 — auto-harness.** this is the interesting one. GPT-5.2 designs a complete solving function that can call Qwen as many times as it wants (budget of ~40 calls per problem). critically, it uses the optimized prompt from stage 2 as the base — so it's building on top of, not replacing, the prompt work.

what GPT-5.2 came up with is a five-phase pipeline:
- first, sample 20 answers with the optimized prompt and count votes
- if there's a strong majority (11+ out of 20 agree), go straight to a verification step
- if not, reprompt from four different angles — algebraic ("keep it symbolic"), counting ("define the sample space"), geometry ("use coordinates"), and a checklist approach ("restate, derive, solve, check, re-check")
- then run a forced-choice tournament: "here are the top candidates, which is correct?"
- finally verify the winner by asking the model to re-solve and check

result: 13.3% on test — 2/15 problems solved. from zero to two, without changing the model at all.

key thing i found: when i accidentally ran stage 3 with a generic prompt instead of the optimized one from stage 2, it got 0%. the harness only works because the prompt optimization gives the model enough signal to occasionally produce correct answers. the layers are multiplicative, not independent.

the biggest insight is that reprompting from different angles is way more powerful than just picking from existing completions. majority vote over 20 answers also gets 0% on test — the correct answer is never the most popular one. but when you reprompt with "try an algebraic approach" or "use coordinates," you generate genuinely new attempts that can break out of whatever failure mode the model is stuck in.

obviously 2/15 is modest. for 13 of the 15 test problems, the model just doesn't have the mathematical capacity no matter what you do. but the principle is clear: smarter scaffolding extracts latent capability the model has but can't reliably access on its own. with a stronger base model, the effect would be much larger — which is presumably why Poetiq's approach works so well with frontier models.

code: github.com/brendanhogan/auto-harness
