"""
Quality Scorer — Scores agent output against ground truth criteria

Takes the agent's final answer and checks it against predefined
ground truth criteria from scenarios.json. Uses keyword/phrase
matching for the prototype.

Returns a score out of 10 with per-criterion breakdown.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class QualityScorer:
    def __init__(self, scenarios_path: str = None):
        if scenarios_path is None:
            scenarios_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "scenarios.json"
            )
        with open(scenarios_path) as f:
            self.scenarios = json.load(f)

    def score(self, session_id: int, final_answer: str) -> dict:
        """
        Score the agent's final answer against ground truth.

        Args:
            session_id: Which session (1-5)
            final_answer: The agent's complete final answer text

        Returns:
            dict with:
                - score: float 0-10
                - max_score: 10
                - criteria_results: per-criterion breakdown
                - matched_criteria: count of matched criteria
                - total_criteria: total criteria count
        """
        session = self._get_session(session_id)
        if not session:
            return {
                "score": 0,
                "max_score": 10,
                "criteria_results": {},
                "matched_criteria": 0,
                "total_criteria": 0,
                "error": f"No session found for id {session_id}",
            }

        criteria = session.get("ground_truth_score_criteria", {})
        answer_lower = final_answer.lower()

        results = {}
        total_weight = 0
        earned_weight = 0

        for criterion_name, criterion in criteria.items():
            keywords = criterion.get("keywords", [])
            weight = criterion.get("weight", 1)
            total_weight += weight

            # Check if ANY keyword is found in the answer
            matched_keywords = [
                kw for kw in keywords if kw.lower() in answer_lower
            ]
            met = len(matched_keywords) > 0

            if met:
                earned_weight += weight

            results[criterion_name] = {
                "description": criterion.get("description", ""),
                "met": met,
                "weight": weight,
                "matched_keywords": matched_keywords,
            }

        # Normalize to 0-10 scale
        score = (earned_weight / total_weight * 10) if total_weight > 0 else 0

        matched_count = sum(1 for r in results.values() if r["met"])

        return {
            "score": round(score, 1),
            "max_score": 10,
            "criteria_results": results,
            "matched_criteria": matched_count,
            "total_criteria": len(criteria),
        }

    def _get_session(self, session_id: int) -> dict | None:
        for session in self.scenarios.get("sessions", []):
            if session["id"] == session_id:
                return session
        return None
