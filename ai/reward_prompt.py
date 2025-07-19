# ai/reward_prompt.py

def get_adaptive_prompt(score):
    base = (
        "You are an expert AI book writer. Rewrite the chapter in modern, engaging prose. "
        "Preserve the original meaning. Be clear and vivid."
    )

    if score <= 2:
        return base + (
            " Prior rewrites were unclear. Focus on simplicity, coherence, and sentence structure. "
            "Avoid archaic or ambiguous phrasing."
        )
    elif score == 3:
        return base + (
            " Prior rewrites were average. Improve pacing and paragraph breaks. Make scenes more vivid."
        )
    elif score >= 4:
        return base + (
            " Prior feedback was positive. You're allowed more stylistic freedom, but preserve clarity and narrative."
        )

    return base
