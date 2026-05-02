# Model Card — PawPal+ Nutrition Advisor

---

## Reflection

**What this project taught me about AI and problem-solving:**

Building PawPal+ made me see AI not as a black box that replaces thinking, but as a layer that requires deliberate design around it. The nutrition advisor only works well because of the RAG architecture — without the curated knowledge base, the same LLM would give generic, one-size-fits-all advice. Designing *what the AI should know before it speaks* turned out to be the most important engineering decision.

I also learned that the deterministic and probabilistic parts of a system have very different failure modes. The scheduler either works or it doesn't — tests prove it. The AI advisor can produce plausible-sounding but subtly wrong output, and tests can't catch that. This made me appreciate prompt engineering as a genuine discipline: structuring the prompt into explicit sections (Meal Recommendation, Portion Guidance, Ingredient Spotlight) and instructing the model to "tie every recommendation back to this dog's profile" were small changes that dramatically improved the output's usefulness.

Finally, designing system classes before writing a single line of code (Owner → Pet → Task → Scheduler) made the later AI integration straightforward. The `DogProfile` dataclass with computed properties (`size_category`, `age_group`, `daily_calories_estimate`) was a direct translation of that design discipline into the AI layer. Good software architecture and good AI product design reinforce each other.

---

## Responsible AI Reflection

### Limitations and biases

**Knowledge base coverage is narrow and static.** The RAG retrieval scores against a hand-curated JSON file of 15 entries. Any breed, condition, or dietary concern not tagged in that file receives a lower-confidence retrieval and falls back to generic facts. A Basenji, a dog with a rare metabolic disorder, or a concern like "kidney disease" will get a response grounded in the wrong context — and the model may not signal that clearly to the user.

**The LLM can hallucinate with high confidence.** LLaMA 3.3-70B occasionally produces specific-sounding numbers (e.g., "feed 2.3 cups twice daily") that have no grounding in the retrieved facts or the RER formula. The model is not penalised for inventing plausible figures, and a non-expert user has no way to distinguish a hallucinated portion size from a calculated one.

**The calorie formula is a population-level estimate.** The RER formula (`70 × weight_kg^0.75`) is a veterinary approximation for average healthy adult dogs. It does not account for individual metabolic variation, neutered/intact status, health conditions, or body condition score. A dog owner who takes the output as medical precision rather than a rough starting point could inadvertently under- or overfeed their dog.

**Breed classification inherits keyword bias.** `size_category` is derived by checking if a known keyword appears anywhere in the breed string. "Miniature Schnauzer" is correctly tagged `small`, but "Giant Miniature Pinscher" (a hypothetical mixed name) would incorrectly fall into `small` before the weight fallback corrects it. The lookup is fragile against non-standard or hyphenated breed names.

---

### Misuse potential and safeguards

**Most plausible misuse:** A user treats the AI meal plan as a veterinary prescription, ignores the disclaimer, and uses it to manage a dog with a serious medical condition (e.g., renal failure, pancreatitis, food allergies with anaphylaxis risk). The system has no mechanism to detect "this dog needs a vet, not an app."

**Safeguards already in place:**
- The prompt instructs the model to produce practical starting-point advice, not clinical prescriptions, and every generated plan includes implicit framing as a "recommendation" rather than a diagnosis.
- The retrieved-knowledge expander lets the user see exactly what facts grounded the AI's response, making it easy to spot if the model went off-script.

**Safeguards that should be added:**
- A hard disclaimer visible above every generated plan: *"This is a general starting-point guide only. Consult your veterinarian before making significant changes to your dog's diet, especially if your dog has a diagnosed health condition."*
- If a dietary concern like `kidney_health`, `liver_health`, or `diabetes` were added to the options, those inputs should automatically suppress the LLM plan and instead display a message directing the user to a vet, since those conditions require clinical diet prescription.

---

### What surprised me during reliability testing

The confidence scoring revealed something that manual testing had missed: an unknown mixed-breed dog with no dietary concerns and a `moderate` activity level scores **0.33** confidence — meaning only 1 of its 3 profile tags (`moderate` activity) is actually covered by any entry in the knowledge base. The retrieval falls back to generic entries, and the LLM generates a plausible but entirely ungrounded response. Before adding the score, this failure was invisible. The model's output read confidently regardless of whether the retrieval matched well or not.

A second surprise: the logging showed that `retrieval_confidence` reaches 1.0 only when the profile has exactly the tags that exist in the knowledge base (e.g., `large` + `senior` + `joint_health`). As soon as a rare concern or unusual combination is added, the score drops sharply — yet the LLM response does not become noticeably less confident. This mismatch between retrieval quality and model tone is a genuine reliability gap that confidence scoring made visible.

---

### Collaboration with AI during this project

AI assistance (Claude) was used throughout development — for generating the initial `dog_nutrition_facts.json` knowledge base entries, drafting the structured prompt template, writing boilerplate test stubs, and debugging the double-conflict-message bug in the UI.

**One instance where AI was genuinely helpful:** When I asked for help structuring the RAG prompt, the AI suggested splitting the response into three explicit labeled sections (Meal Recommendation, Portion Guidance, Ingredient Spotlight) with the instruction to "tie every recommendation back to this dog's profile." That was not something I had thought of. The structured output format made the responses dramatically easier to read and evaluate, and the grounding instruction reduced generic filler significantly.

**One instance where AI's suggestion was flawed:** Early on, the AI suggested using cosine similarity over sentence embeddings for the RAG retrieval step, calling it "more robust than tag matching." For a knowledge base of 15 entries, this was wrong advice — it would have added a heavy dependency (`sentence-transformers` or an embedding API call), introduced non-determinism, made the retrieval harder to debug, and would not have improved results at this data scale. The tag-overlap approach is simpler, faster, fully deterministic, and easy to reason about. The AI was optimising for a large-scale use case and missed the context that simplicity was the right tradeoff here.
