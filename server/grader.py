def grade_query(ai_query: str, task: dict, db_connection):
    max_scores = {"easy": 0.3, "medium": 0.6, "hard": 1.0}
    difficulty = task.get("difficulty", "medium").lower()
    max_score = max_scores.get(difficulty, 0.6)

    total_score = 0.0
    feedback_msgs = []

    try:
        cursor = db_connection.cursor()
        cursor.execute(ai_query)
        ai_result = cursor.fetchall()
        total_score += max_score * 0.20
        feedback_msgs.append("Query executed successfully")
    except Exception as exc:
        return {"score": 0.0, "feedback": f"SQL Error: {exc}"}

    correct_output = task.get("correct_output", [])
    ai_sorted = sorted(tuple(row) for row in ai_result)
    correct_sorted = sorted(tuple(row) for row in correct_output)

    if ai_sorted == correct_sorted:
        total_score += max_score * 0.50
        feedback_msgs.append("Output matched")
    else:
        ai_set, correct_set = set(ai_sorted), set(correct_sorted)
        if ai_set.intersection(correct_set):
            total_score += max_score * 0.25
            feedback_msgs.append("Partial output match")
        else:
            feedback_msgs.append("No match")

    query_lower = ai_query.lower()

    required_tables = task.get("required_tables", [])
    if required_tables:
        tables_used = sum(1 for table in required_tables if table.lower() in query_lower)
        total_score += (tables_used / len(required_tables)) * (max_score * 0.20)
        if tables_used < len(required_tables):
            feedback_msgs.append("Missing tables")
    else:
        total_score += max_score * 0.20

    required_keywords = task.get("required_keywords", [])
    if required_keywords:
        keywords_used = sum(1 for keyword in required_keywords if keyword.lower() in query_lower)
        total_score += (keywords_used / len(required_keywords)) * (max_score * 0.10)
        if keywords_used < len(required_keywords):
            feedback_msgs.append("Missing keywords")
    else:
        total_score += max_score * 0.10

    return {
        "score": round(min(total_score, max_score), 2),
        "feedback": " | ".join(feedback_msgs),
    }

