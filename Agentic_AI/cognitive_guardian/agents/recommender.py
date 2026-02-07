def recommend(text, hobby=""):
    text_l = text.lower()
    hobby_l = hobby.lower().strip() if hobby else ""

    # Emotion detection
    sad = any(x in text_l for x in ["sad", "depressed", "hopeless", "lonely", "tired"])
    anxious = any(x in text_l for x in ["stress", "pressure", "anxious", "worried"])

    hobby_phrase = f" related to {hobby_l}" if hobby_l else ""

    if sad:
        return {
        "emotional_summary": "It sounds like you're feeling emotionally drained or discouraged right now.",
        "support_message": (
            "You're not alone in feeling this way. Everyone goes through phases where motivation drops or "
            "life feels heavier than usual. Try not to judge yourself too harshly — even small positive steps "
            "count as progress. Give yourself permission to slow down and recover emotionally."
        ),
        "movie_recommendation": "The Pursuit of Happyness",
        "song_recommendation": "Hall of Fame – The Script",
        "activity_recommendation": f"Spend at least 15–20 minutes doing something that genuinely relaxes or excites you{hobby_phrase}.",
        "youtube_recommendation": f"inspiring motivational video about overcoming struggles and rebuilding confidence{hobby_phrase}"
    }


    if anxious:
        return {
        "emotional_summary": "Your text shows signs of stress, mental pressure, or anxiety.",
        "support_message": (
            "When your mind feels overloaded, your nervous system may be stuck in fight-or-flight mode. "
            "Slowing your breathing, grounding your body, and stepping away from screens for a few minutes "
            "can calm your system surprisingly fast. You don’t need to solve everything today — focus on "
            "stability first."
        ),
        "movie_recommendation": "Peaceful Warrior",
        "song_recommendation": "Weightless – Marconi Union",
        "activity_recommendation": f"Try slow breathing, light stretching, or a short walk{hobby_phrase}.",
        "youtube_recommendation": f"guided breathing exercise to calm anxiety and clear the mind{hobby_phrase}"
    }


    return {
    "emotional_summary": "You appear emotionally stable and reflective at the moment.",
    "support_message": (
        "That’s a great place to be mentally. Maintaining balance, consistency, and healthy routines "
        "helps build long-term confidence and clarity. Keep moving forward steadily, but also remember "
        "to enjoy the process instead of only chasing outcomes."
    ),
    "movie_recommendation": "Forrest Gump",
    "song_recommendation": "Beautiful Day – U2",
    "activity_recommendation": f"Do a small enjoyable activity that refreshes your mind{hobby_phrase}.",
    "youtube_recommendation": f"positive mindset self growth and motivation video{hobby_phrase}"
    }



# ✅ Fallback wrapper used by UI
def recommend_with_fallback(text: str, hobby: str = "") -> dict:
    text_l = text.lower()
    hobby_l = hobby.lower().strip()

    sad = any(x in text_l for x in ["sad", "depressed", "hopeless", "lonely", "tired"])
    anxious = any(x in text_l for x in ["stress", "pressure", "anxious", "worried", "panic"])
    sleep = any(x in text_l for x in ["sleep", "insomnia", "can't sleep", "sleepless"])

    # ----------------------------
    # 🎯 Primary problem intent
    # ----------------------------

    if sleep:
        base_query = "how to sleep better naturally guided relaxation breathing for sleep"
        emotional = "Your message suggests difficulty sleeping or mental fatigue."
        support = "Improving sleep often starts with calming your nervous system and building a consistent routine."
        movie = "Inception"
        song = "Weightless – Marconi Union"
        activity = "Dim lights, avoid screens before bed, and practice slow breathing for 5 minutes."

    elif anxious:
        base_query = "guided breathing for anxiety calm nervous system mindfulness grounding"
        emotional = "Your text shows signs of stress or anxiety."
        support = "Slowing your breathing and grounding your body helps your nervous system stabilize quickly."
        movie = "Peaceful Warrior"
        song = "Weightless – Marconi Union"
        activity = "Light stretching, breathing exercises, or a short walk."

    elif sad:
        base_query = "motivational video overcoming sadness rebuilding confidence mindset"
        emotional = "Your text suggests emotional heaviness or low motivation."
        support = "Small positive actions rebuild emotional momentum. Be patient with yourself."
        movie = "The Pursuit of Happyness"
        song = "Hall of Fame – The Script"
        activity = "Do one small enjoyable activity that lifts your mood."

    else:
        base_query = "positive mindset mental clarity focus habits self improvement"
        emotional = "You appear emotionally stable and reflective."
        support = "Maintaining balance and consistency builds long-term clarity and confidence."
        movie = "Forrest Gump"
        song = "Beautiful Day – U2"
        activity = "Do a small activity that refreshes your mind."

    # ----------------------------
    # 🥈 Hobby-enhanced query
    # ----------------------------

    hobby_query = None
    if hobby_l:
        hobby_query = f"{base_query} {hobby_l}"

    return {
        "emotional_summary": emotional,
        "support_message": support,
        "movie_recommendation": movie,
        "song_recommendation": song,
        "activity_recommendation": activity,
        "youtube_primary_query": base_query,     # 🎯 priority
        "youtube_hobby_query": hobby_query       # 🥈 optional
    }
