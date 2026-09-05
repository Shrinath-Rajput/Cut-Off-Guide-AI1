import json
import logging
import random
from typing import List, Dict, Any, Optional
from urllib import request as urllib_request

from app.core.config import settings
from app.schemas.cutoff import (
    CutoffSearchRequest,
    CutoffResult,
    CollegePredictLLMRequest,
    CollegePredictLLMResponse,
    CollegeRecommendationItem,
)
from app.services.college_service import INDIAN_COLLEGES_SEED
from app.services.colleges_seed_data import ADDITIONAL_MAHARASHTRA_COLLEGES

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Category cutoffs adjustment relative to Open/General
CATEGORY_DELTAS = {
    "open": 0.0,
    "general": 0.0,
    "open/general": 0.0,
    "obc": -1.6,
    "ews": -1.8,
    "tfws": 0.6,
    "sc": -10.5,
    "st": -18.0,
    "nt-a": -4.0,
    "nt-b": -4.5,
    "nt-c": -3.2,
    "nt-d": -2.2,
    "sbc": -3.5,
    "pwd": -8.5,
    "defence": -6.5,
    "minority": -5.0,
    "kashmiri migrant": -12.0,
}

# Round cutoffs adjustment relative to Round 1
ROUND_DELTAS = {
    "round 1": 0.0,
    "round 2": -0.85,
    "round 3": -1.65,
}

# Branch base cutoffs benchmark offsets
BRANCH_OFFSETS = {
    "computer engineering (cse)": 0.0,
    "computer engineering": 0.0,
    "computer science & engineering": 0.0,
    "computer science": 0.0,
    "cse": 0.0,
    "information technology (it)": -0.8,
    "information technology": -0.8,
    "it": -0.8,
    "artificial intelligence & machine learning": -1.2,
    "ai & ml": -1.2,
    "ai/ml": -1.2,
    "aiml": -1.2,
    "artificial intelligence & data science": -1.4,
    "artificial intelligence": -1.4,
    "ai & ds": -1.4,
    "ai-ds": -1.4,
    "aids": -1.4,
    "cyber security": -1.2,
    "cyber": -1.2,
    "data science": -1.5,
    "electronics & telecommunication": -3.2,
    "electronics and telecommunication": -3.2,
    "e&tc": -3.2,
    "entc": -3.2,
    "electronics & communication": -3.0,
    "electronics and communication": -3.0,
    "ece": -3.0,
    "electrical engineering": -5.5,
    "electrical": -5.5,
    "mechanical engineering": -7.0,
    "mechanical": -7.0,
    "civil engineering": -9.0,
    "civil": -9.0,
    "chemical engineering": -8.5,
    "chemical": -8.5,
    "robotics & automation": -2.5,
    "robotics": -2.5,
    "mechatronics": -3.5,
    "biotechnology": -5.0,
    "biotech": -5.0,
    "aerospace engineering": -2.0,
    "aerospace": -2.0,
    "automobile engineering": -7.5,
    "automobile": -7.5,
    "others": -4.0,
}

# Base college reputations and cutoffs for Open category in Round 1
KNOWN_COLLEGE_BASE_CUTOFFS = {
    "iit-bombay": 99.85,
    "iit-delhi": 99.80,
    "iit-madras": 99.75,
    "coep-pune": 99.20,
    "vjti-mumbai": 99.40,
    "pict-pune": 98.80,
    "spit-mumbai": 98.60,
    "walchand-sangli": 97.40,
    "pccoe-pune": 96.20,
    "vit-pune": 95.80,
    "cummins-pune": 94.80,
    "mit-wpu": 93.20,
    "dypcoe-akurdi": 91.50,
    "dypit-pimpri": 89.20,
    "vesit-mumbai": 92.50,
    "viit-pune": 91.00,
    "vnit-nagpur": 97.80,
    "aissms-coe": 84.50,
    "sinhgad-vadgaon": 82.00,
    "jspm-tathawade": 80.50,
    "modern-education-society": 81.20,
    "thakur-mumbai": 86.50,
    "pillai-navi-mumbai": 79.50,
    "gh-raisoni-nagpur": 74.00,
}

# Populate baseline cutoffs from seed data
for _c in ADDITIONAL_MAHARASHTRA_COLLEGES:
    if "id" in _c and "base_cutoff" in _c:
        KNOWN_COLLEGE_BASE_CUTOFFS[_c["id"]] = _c["base_cutoff"]


async def search_cutoffs(db, search_request: CutoffSearchRequest) -> CutoffResult:
    """Legacy Cutoff Search Method"""
    if db is not None:
        try:
            collection = db["cutoffs"]
            query = {}
            if search_request.course:
                query["course"] = {"$regex": search_request.course, "$options": "i"}
            if search_request.category:
                query["category"] = search_request.category
            if search_request.gender:
                query["gender"] = search_request.gender
            if search_request.university:
                query["university"] = {"$regex": search_request.university, "$options": "i"}
            if search_request.location:
                query["location"] = {"$regex": search_request.location, "$options": "i"}
            if search_request.round:
                query["round"] = search_request.round

            cutoff_record = await collection.find_one(query, sort=[("percentile", -1)])
            if cutoff_record:
                return CutoffResult(
                    cutoff=str(cutoff_record.get("percentile", "94.5%ile")),
                    rank=str(cutoff_record.get("rank", "12,450")),
                    suggestion=cutoff_record.get("college_name", "COEP Tech / PICT Pune"),
                )
        except Exception as e:
            logging.warning("Cutoffs DB lookup exception: %s", e)

    # Fallback
    try:
        pct = float(search_request.percentile) if search_request.percentile else 90.0
    except Exception:
        pct = 90.0

    rank_est = int(max(1, (100 - pct) * 1200))
    if pct >= 98:
        sugg = "IIT Bombay / COEP Technological University (Computer Engg)"
    elif pct >= 95:
        sugg = "VJTI Mumbai / PICT Pune / SPIT Mumbai (Information Tech)"
    elif pct >= 90:
        sugg = "PCCOE Pune / VIT Pune / DYPCOE Akurdi (AI & Data Science)"
    elif pct >= 80:
        sugg = "MIT-WPU Pune / Cummins College of Engg / DYPIT Pimpri"
    else:
        sugg = "State Autonomous & University Affiliated Colleges"

    return CutoffResult(
        cutoff=f"{pct:.2f}%ile",
        rank=f"AIR ~{rank_est:,}",
        suggestion=sugg,
    )


def _get_category_delta(category_str: str) -> float:
    cat_lower = (category_str or "").strip().lower()
    for k, v in CATEGORY_DELTAS.items():
        if k in cat_lower:
            return v
    return 0.0


def _get_round_delta(round_str: str) -> float:
    r_lower = (round_str or "").strip().lower()
    for k, v in ROUND_DELTAS.items():
        if k in r_lower:
            return v
    return 0.0


def _get_branch_offset(branch_str: str) -> float:
    b_lower = (branch_str or "").strip().lower()
    for k, v in BRANCH_OFFSETS.items():
        if k in b_lower:
            return v
    return -2.0


def _get_college_base_cutoff(college: Dict[str, Any]) -> float:
    if "base_cutoff" in college and college["base_cutoff"] is not None:
        return float(college["base_cutoff"])

    cid = college.get("id", "")
    if cid in KNOWN_COLLEGE_BASE_CUTOFFS:
        return KNOWN_COLLEGE_BASE_CUTOFFS[cid]

    # Heuristic based on rating and NIRF
    rating = float(college.get("rating", 4.0))
    nirf = college.get("nirf_rank")

    if nirf and nirf <= 20:
        return 99.3
    elif nirf and nirf <= 50:
        return 98.0
    elif nirf and nirf <= 100:
        return 95.5
    elif nirf and nirf <= 200:
        return 91.0

    if rating >= 4.8:
        return 97.5
    elif rating >= 4.5:
        return 94.0
    elif rating >= 4.2:
        return 88.5
    elif rating >= 4.0:
        return 80.0
    elif rating >= 3.8:
        return 70.0
    elif rating >= 3.5:
        return 56.0
    elif rating >= 3.2:
        return 44.0
    else:
        return 34.0


def _call_groq_for_reasoning(
    candidate_summary: str,
    college_list: List[Dict[str, Any]],
) -> Optional[Dict[str, str]]:
    """Invokes Groq LLaMA to generate custom counselor reasoning."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return None

    url = settings.GROQ_API_URL or "https://api.groq.com/openai/v1/chat/completions"
    model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    prompt = (
        f"You are the Chief Academic Admissions Counselor at CutoffGuide. "
        f"A student with profile: {candidate_summary} is seeking college recommendations.\n\n"
        f"Here are candidate recommendations:\n"
        f"{json.dumps(college_list[:10], indent=2)}\n\n"
        f"Respond with a strict JSON object mapping each college_id to a 2-sentence expert counselor reasoning:\n"
        f"Explain why it fits their category and CAP round, and strategic advice for option form filling.\n"
        f"Format: {{\"college_id_1\": \"reasoning...\", \"college_id_2\": \"reasoning...\"}}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert Indian engineering admissions counselor. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"}
    }

    try:
        req = urllib_request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST"
        )
        with urllib_request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
    except Exception as exc:
        logging.info("Groq counselor reasoning note: %s", exc)

    return None


async def predict_colleges_with_llm(
    db,
    req: CollegePredictLLMRequest,
) -> CollegePredictLLMResponse:
    candidate_pct = round(req.percentile, 2)
    category = req.category or "Open/General"
    location_pref = (req.location or "").strip()
    cap_round = req.round or "Round 1"
    target_courses = req.preferred_courses or ["Computer Engineering (CSE)"]

    cat_delta = _get_category_delta(category)
    round_delta = _get_round_delta(cap_round)

    # 1. Gather all colleges
    all_pool = list(INDIAN_COLLEGES_SEED)

    # Filter by exam compatibility
    exam_lower = req.exam.lower()
    if "adv" in exam_lower:
        compatible_pool = [c for c in all_pool if "Advanced" in str(c.get("exams", [])) or "IIT" in c.get("name", "")]
        if not compatible_pool:
            compatible_pool = [c for c in all_pool if "IIT" in c.get("name", "")]
    elif "cet" in exam_lower or "mht" in exam_lower:
        compatible_pool = [
            c for c in all_pool
            if c.get("state") == "Maharashtra" or "MHT-CET" in str(c.get("exams", []))
        ]
    else:
        compatible_pool = [
            c for c in all_pool
            if "JEE" in str(c.get("exams", [])) or "NIT" in c.get("name", "") or "IIIT" in c.get("name", "")
        ]

    if len(compatible_pool) < 20:
        compatible_pool = compatible_pool + [c for c in all_pool if c not in compatible_pool]

    # Prioritize preferred location if specified
    location_pool = []
    if location_pref and location_pref.lower() not in ("all", "all maharashtra", "any", "all india"):
        loc_clean = location_pref.lower()
        location_pool = [
            c for c in compatible_pool
            if loc_clean in (c.get("city", "") + " " + c.get("location", "") + " " + c.get("name", "")).lower()
        ]

    # Combine location-matched colleges first, then remaining compatible pool, then broader pool
    seen_ids = set()
    ordered_pool = []
    for c in location_pool + compatible_pool + all_pool:
        cid = c.get("id")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            ordered_pool.append(c)

    # Low percentile (< 30%ile) check
    is_low_percentile = candidate_pct < 30.0

    selected = []

    if is_low_percentile:
        # For percentile < 30, government merit cutoffs through CAP rounds are unreachable.
        # Provide at least 15 curated private engineering institutions and deemed universities
        # that accept direct admissions, institute-level quota, or management quota.
        private_pool = [
            c for c in ordered_pool
            if any(term in (c.get("type", "") + " " + c.get("name", "")).lower() for term in ["private", "deemed", "autonomous", "institute of technology", "college of engineering", "technology"])
            and "government" not in c.get("type", "").lower()
            and "iit " not in c.get("name", "").lower()
            and "nit " not in c.get("name", "").lower()
        ]
        if len(private_pool) < 18:
            private_pool = private_pool + [
                c for c in INDIAN_COLLEGES_SEED
                if "government" not in c.get("type", "").lower() and c not in private_pool
            ]

        # Prioritize location if requested
        if location_pref and location_pref.lower() not in ("all", "all maharashtra", "any", "all india"):
            loc_c = location_pref.lower()
            loc_matched = [c for c in private_pool if loc_c in (c.get("city", "") + " " + c.get("location", "") + " " + c.get("name", "")).lower()]
            other_p = [c for c in private_pool if c not in loc_matched]
            private_pool = loc_matched + other_p

        chosen_private = private_pool[:18]
        primary_course = target_courses[0] if target_courses else "Computer Engineering (CSE)"

        for i, college in enumerate(chosen_private):
            # Tier balance: 7 Safe, 6 Target, 5 Ambitious
            if i < 7:
                tier = "Safe"
                pct_chance = 92
            elif i < 13:
                tier = "Target"
                pct_chance = 72
            else:
                tier = "Ambitious"
                pct_chance = 45

            assigned_course = target_courses[i % len(target_courses)] if target_courses else primary_course

            selected.append({
                "college_id": college.get("id"),
                "college_name": college.get("name"),
                "city": college.get("city", "Maharashtra"),
                "location": college.get("location", college.get("city", "Maharashtra")),
                "branch": assigned_course,
                "cutoff_percentile": 30.0,
                "chance_tier": tier,
                "chance_percentage": pct_chance,
                "category": category,
                "round": "Private / Management Quota",
                "placement_avg": college.get("placement_avg", "₹6.5 LPA"),
                "highest_package": college.get("highest_package", "₹24.0 LPA"),
                "fee_display": college.get("fee_display", "₹1.2 Lakh / year"),
                "diff": candidate_pct - 30.0,
                "rating": college.get("rating", 4.0),
                "is_preferred_loc": bool(location_pref and location_pref.lower() in (college.get("city", "") + college.get("location", "")).lower()),
                "is_private_quota": True,
            })

    else:
        # Regular merit-based evaluation (percentile >= 30%ile)
        candidates = []

        for college in ordered_pool:
            base_college_cutoff = _get_college_base_cutoff(college)

            for course in target_courses:
                b_offset = _get_branch_offset(course)
                raw_cutoff = base_college_cutoff + b_offset + cat_delta + round_delta
                effective_cutoff = round(float(max(30.0, min(99.95, raw_cutoff))), 2)

                diff = candidate_pct - effective_cutoff

                # Classify into tier
                if diff >= 0.8:
                    tier = "Safe"
                    pct_chance = min(98, max(82, int(86 + min(diff, 12.0) * 1.0)))
                elif diff >= -2.5:
                    tier = "Target"
                    pct_chance = min(80, max(52, int(66 + diff * 5.0)))
                elif diff >= -7.0:
                    tier = "Ambitious"
                    pct_chance = min(49, max(20, int(35 + diff * 3.0)))
                else:
                    tier = "Ambitious"
                    pct_chance = 18

                candidates.append({
                    "college_id": college.get("id"),
                    "college_name": college.get("name"),
                    "city": college.get("city", "Maharashtra"),
                    "location": college.get("location", college.get("city", "Maharashtra")),
                    "branch": course,
                    "cutoff_percentile": effective_cutoff,
                    "chance_tier": tier,
                    "chance_percentage": pct_chance,
                    "category": category,
                    "round": cap_round,
                    "placement_avg": college.get("placement_avg", "₹8.5 LPA"),
                    "highest_package": college.get("highest_package", "₹32.0 LPA"),
                    "fee_display": college.get("fee_display", "₹1.1 Lakh / year"),
                    "diff": diff,
                    "rating": college.get("rating", 4.0),
                    "is_preferred_loc": bool(location_pref and location_pref.lower() in (college.get("city", "") + college.get("location", "")).lower()),
                    "is_private_quota": False,
                })

        safe_list = [c for c in candidates if c["chance_tier"] == "Safe"]
        target_list = [c for c in candidates if c["chance_tier"] == "Target"]
        ambitious_list = [c for c in candidates if c["chance_tier"] == "Ambitious"]

        # Sort tiers prioritizing preferred location, rating, and closeness to candidate
        safe_list.sort(key=lambda x: (x["is_preferred_loc"], -abs(x["diff"] - 2.5), x["rating"], x["cutoff_percentile"]), reverse=True)
        target_list.sort(key=lambda x: (x["is_preferred_loc"], -abs(x["diff"]), x["rating"]), reverse=True)
        ambitious_list.sort(key=lambda x: (x["is_preferred_loc"], -abs(x["diff"]), x["rating"]), reverse=True)

        selected_keys = set()
        college_counts = {}

        def add_from_list(source_list, quota):
            added = 0
            for item in source_list:
                cid = item["college_id"]
                key = f"{cid}_{item['branch']}"
                max_per_college = 2 if len(target_courses) > 1 else 1
                if key not in selected_keys and college_counts.get(cid, 0) < max_per_college:
                    selected.append(item)
                    selected_keys.add(key)
                    college_counts[cid] = college_counts.get(cid, 0) + 1
                    added += 1
                    if added >= quota:
                        break

        # Balanced initial distribution: 6 Target, 6 Safe, 5 Ambitious (target: 17 unique colleges)
        add_from_list(target_list, 6)
        add_from_list(safe_list, 6)
        add_from_list(ambitious_list, 5)

        # Backfill from remaining candidates if any tier was sparse
        if len(selected) < 15:
            for item in target_list + safe_list + ambitious_list + candidates:
                cid = item["college_id"]
                key = f"{cid}_{item['branch']}"
                if key not in selected_keys:
                    selected.append(item)
                    selected_keys.add(key)
                    if len(selected) >= 16:
                        break

        # Backfill from broader pool across state/nation if still < 15
        if len(selected) < 15:
            primary_course = target_courses[0] if target_courses else "Computer Engineering (CSE)"
            for college in ordered_pool:
                cid = college.get("id")
                if cid not in selected_college_ids:
                    b_cut = _get_college_base_cutoff(college)
                    eff_c = round(float(max(30.0, min(99.95, b_cut + cat_delta + round_delta))), 2)
                    d = candidate_pct - eff_c
                    if d >= 0.8:
                        t = "Safe"
                        p_c = 88
                    elif d >= -2.5:
                        t = "Target"
                        p_c = 68
                    else:
                        t = "Ambitious"
                        p_c = 35

                    selected.append({
                        "college_id": cid,
                        "college_name": college.get("name"),
                        "city": college.get("city", "Maharashtra"),
                        "location": college.get("location", college.get("city", "Maharashtra")),
                        "branch": primary_course,
                        "cutoff_percentile": eff_c,
                        "chance_tier": t,
                        "chance_percentage": p_c,
                        "category": category,
                        "round": cap_round,
                        "placement_avg": college.get("placement_avg", "₹7.5 LPA"),
                        "highest_package": college.get("highest_package", "₹28.0 LPA"),
                        "fee_display": college.get("fee_display", "₹1.2 Lakh / year"),
                        "diff": d,
                        "rating": college.get("rating", 4.0),
                        "is_preferred_loc": bool(location_pref and location_pref.lower() in (college.get("city", "") + college.get("location", "")).lower()),
                        "is_private_quota": False,
                    })
                    selected_college_ids.add(cid)
                    if len(selected) >= 16:
                        break

        # Backfill with secondary branches if pool is somehow smaller than 15
        if len(selected) < 15:
            existing_keys = {f"{c['college_id']}_{c['branch']}" for c in selected}
            extra_branches = [
                "Information Technology (IT)",
                "Artificial Intelligence & Machine Learning",
                "Artificial Intelligence & Data Science",
                "Cyber Security",
                "Data Science",
                "Electronics & Telecommunication",
                "Electronics & Communication",
                "Electrical Engineering",
                "Robotics & Automation",
                "Mechanical Engineering",
            ]
            for c in list(selected):
                for b in extra_branches:
                    key = f"{c['college_id']}_{b}"
                    if key not in existing_keys:
                        c_copy = dict(c)
                        c_copy["branch"] = b
                        selected.append(c_copy)
                        existing_keys.add(key)
                        if len(selected) >= 15:
                            break
                if len(selected) >= 15:
                    break

        # Cap selection to at least 15 (e.g. 15 to 18)
        selected = selected[:max(15, min(18, len(selected)))]

    # 3. Generate AI Reasoning
    summary_text = (
        f"Candidate scored {candidate_pct}%ile in {req.exam}, applying under {category} category "
        f"in {cap_round} for location '{location_pref or 'Maharashtra'}'."
    )

    llm_reasons = _call_groq_for_reasoning(summary_text, selected[:10]) or {}

    final_recommendations: List[CollegeRecommendationItem] = []
    for item in selected:
        cid = item["college_id"]
        cname = item["college_name"]
        branch = item["branch"]
        tier = item["chance_tier"]
        diff = item["diff"]

        if is_low_percentile or item.get("is_private_quota"):
            if tier == "Safe":
                reason = (
                    f"Private / Institute-Level Quota: At {candidate_pct}%ile, regular CAP cutoffs are unreachable. "
                    f"{cname} offers direct admissions under institutional quota with a high {item['chance_percentage']}% feasibility. "
                    f"Contact the college admissions office directly."
                )
            elif tier == "Target":
                reason = (
                    f"Private Autonomous Quota: {cname} offers management seats for {branch}. "
                    f"Admission is feasible via merit-cum-management counseling ({item['chance_percentage']}% probability). "
                    f"Early application at the campus desk is recommended."
                )
            else:
                reason = (
                    f"Deemed University Quota: {cname} provides deemed/management quota seats for {branch}. "
                    f"While competitive ({item['chance_percentage']}% chance), direct application and personal counseling "
                    f"offer a realistic pathway."
                )
        elif cid in llm_reasons and len(llm_reasons[cid]) > 15:
            reason = llm_reasons[cid]
        else:
            # High-fidelity counselor intelligence synthesis
            if tier == "Safe":
                reason = (
                    f"With your {candidate_pct}%ile against a projected {item['cutoff_percentile']}%ile cutoff "
                    f"({category} quota in {cap_round}), you have a commanding {item['chance_percentage']}% probability. "
                    f"Keep {cname} as a secure backup option in your preference form."
                )
            elif tier == "Target":
                reason = (
                    f"Your percentile is closely aligned with {cname}'s {branch} closing trend "
                    f"({item['cutoff_percentile']}%ile). Strong probability of allotment in {cap_round}; "
                    f"recommended to place in your top choices."
                )
            else:
                reason = (
                    f"An ambitious dream reach requiring a minor {abs(diff):.1f}%ile cutoff movement. "
                    f"With {category} quota adjustments in {cap_round}, placing this at the top of your "
                    f"option form carries high upside with zero allocation penalty."
                )

        final_recommendations.append(
            CollegeRecommendationItem(
                college_id=cid,
                college_name=cname,
                city=item["city"],
                location=item["location"],
                branch=branch,
                cutoff_percentile=item["cutoff_percentile"],
                chance_tier=tier,
                chance_percentage=item["chance_percentage"],
                category=item["category"],
                round=item["round"],
                placement_avg=item["placement_avg"],
                highest_package=item["highest_package"],
                fee_display=item["fee_display"],
                ai_reasoning=reason,
            )
        )

    safe_count = sum(1 for c in final_recommendations if c.chance_tier == "Safe")
    target_count = sum(1 for c in final_recommendations if c.chance_tier == "Target")
    ambitious_count = sum(1 for c in final_recommendations if c.chance_tier == "Ambitious")

    if is_low_percentile:
        counselor_advice = (
            f"Advisory for {candidate_pct}%ile: Your percentile is below 30%, which is too low to apply for "
            f"merit-based seats in government or top autonomous engineering colleges through regular CAP rounds. "
            f"We have curated {len(final_recommendations)} premier private engineering colleges and deemed universities "
            f"where direct admission, institute-level seats, and management quota options are feasible."
        )
    else:
        counselor_advice = (
            f"Strategy Report: With {candidate_pct}%ile under {category} in {cap_round}, "
            f"we recommend an optimal preference distribution across your {len(final_recommendations)} options: "
            f"{ambitious_count} Ambitious dream colleges, {target_count} Target realistic allotments, "
            f"and {safe_count} Safe fail-safe backups."
        )

    summary_data = {
        "candidate_percentile": candidate_pct,
        "exam": req.exam,
        "category": category,
        "location": location_pref or "All Maharashtra / India",
        "round": cap_round,
        "total_recommendations": len(final_recommendations),
        "safe_count": safe_count,
        "target_count": target_count,
        "ambitious_count": ambitious_count,
        "counselor_advice": counselor_advice,
        "is_low_percentile": is_low_percentile,
        "advisory_message": (
            "Percentile is below 30% — too low to apply for government / CAP merit cutoffs. "
            "Please search for private colleges, deemed universities, and management quota seats."
        ) if is_low_percentile else None,
    }

    return CollegePredictLLMResponse(
        summary=summary_data,
        colleges=final_recommendations,
    )
