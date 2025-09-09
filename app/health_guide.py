import copy
import inspect
import json
import os
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

user_data = {
    "gender": "male",  # 1.1.1
    "height_inches": 70,  # 1.1.2
    "age": 35,  # 1.1.3
    "current_weight_lbs": 180,  # 1.1.4
    "body_fat_percentage": 18.5,  # 1.1.5
    "target_weight_lbs": 170,  # 1.1.6
    "target_body_area": "full body",  # 1.1.7
    "has_daily_responsibilities": True,  # 1.2.5
    "responsibility_days_per_week": 5,  # 1.2.6
    "responsibility_start_time": "09:00",  # 1.2.7 (start time)
    "responsibility_end_time": "17:00",  # 1.2.7 (end time)
    "pet_care_morning": True,  # 1.2.8 (morning)
    "pet_care_morning_start_time": "07:00",  # 1.2.8 (morning start)
    "pet_care_morning_end_time": "08:30",  # 1.2.8 (morning end)
    "pet_care_evening": True,  # 1.2.8 (evening)
    "pet_care_evening_start_time": "18:30",  # 1.2.8 (evening start)
    "pet_care_evening_end_time": "19:00",  # 1.2.8 (evening end)
    "others_rely_on_time": True,  # 1.2.9
    "use_tobacco": True,  # 1.3.1
    "tobacco_type": ["cigarette"],  # 1.3.2
    "tobacco_quantity": 10,  # 1.3.3
    "tobacco_frequency": "per day",  # 1.3.4
    "tobacco_goal": "quit entirely",  # 1.3.5
    "tobacco_cravings_time": ["evenings"],  # 1.3.6
    "use_marijuana": False,  # 1.3.7
    "marijuana_type": [],  # 1.3.8
    "marijuana_quantity": 0,  # 1.3.9
    "marijuana_frequency": "",  # 1.3.10
    "marijuana_goal": "no change",  # 1.3.11
    "marijuana_cravings_time": [],  # 1.3.12
    "use_alcohol": True,  # 1.3.13
    "alcohol_quantity": 4,  # 1.3.14
    "alcohol_frequency": "per week",  # 1.3.15
    "alcohol_goal": "reduce",  # 1.3.16
    "alcohol_cravings_time": ["evenings"],  # 1.3.17
    "use_caffeine": True,  # 1.3.18
    "caffeine_type": ["coffee"],  # 1.3.19
    "caffeine_quantity": 3,  # 1.3.20
    "caffeine_frequency": "per day",  # 1.3.21
    "caffeine_goal": "reduce",  # 1.3.22
    "caffeine_cravings_time": ["mornings"],  # 1.3.23
    "take_daily_meds_supplements": True,  # 1.5.1
    "meds_supplements_times": ["morning", "bedtime"],  # 1.5.2
    "include_med_reminders": True,  # 1.5.3
    "gym_access": True,  # 1.7.1
    "preferred_workout_location": "gym or fitness center",  # 1.7.2
    "home_fitness_equipment": ["dumbbells", "yoga mat"],  # 1.7.3
    "injuries_or_limitations": False,  # 1.7.4
    "exercise_types_enjoyed": ["strength training", "cardio"],  # 1.7.5
    "preferred_workout_time": "evening",  # 1.7.6
    "daily_fitness_minutes": 45,  # 1.7.7
    "current_activity_level": "light activity",  # 1.7.8
    "fitness_goals": ["increase strength", "improve endurance"],  # 1.7.9
    "sexual_partners_per_month": 1,  # 1.8.1
    "partnered_sex_frequency_per_week": 3,  # 1.8.2
    "solo_play_frequency_per_week": 1,  # 1.8.3
    "relationship_status": "monogamous partnership only",  # 1.8.4
    "sexual_orientation": "straight",  # 1.8.5
    "solo_play_methods": ["manual stimulation", "porn or erotic media"],  # 1.8.6
    "partnered_activity_types": ["vaginal intercourse", "oral sex (giving)"],  # 1.8.7
    "regular_uninterrupted_time_for_sexual_activity": True,  # 1.8.8
    "satisfaction_with_frequency": "somewhat satisfied",  # 1.8.9
    "satisfaction_with_quality": "somewhat satisfied",  # 1.8.10
    "contraception_safety_methods": ["none"],  # 1.8.11
    "menstrual_periods": None,  # 1.8.12 (female only)
    "track_cycle": None,  # 1.8.12 (female only)
    "menstrual_phase": None,  # 1.8.12 (female only)
    "male_performance_goals": [
        "stamina",
        "control / delay orgasm",
        "libido / arousal",
    ],  # 1.8.13
    "female_performance_goals": [],  # 1.8.14
    "issues_with_stamina_control_sensitivity_or_discomfort": False,  # 1.8.15
    "daily_stress_causes": [
        "work deadlines",
        "time pressure",
        "health worries",
    ],  # 1.9.1
    "uses_stress_relief_tools": True,  # 1.9.2
    "stress_tool_meditation_app": True,  # 1.9.2.2.1
    "stress_tool_journaling": False,  # 1.9.2.2.2
    "stress_tool_deep_breathing": True,  # 1.9.2.2.3
    "stress_tool_yoga": False,  # 1.9.2.2.4
    "stress_tool_other": False,  # 1.9.2.2.5
    "can_take_breaks": True,  # 1.9.3
    "has_space_for_movement_sessions": True,  # 1.9.4
    "preferred_time_for_unscheduled_activities": "evenings",  # 1.9.5
    "desired_free_time_per_day_hours": 3,  # 1.9.6
    "screen_time_outside_work_hours": 4,  # 1.9.7
    "sleep_with_phone_in_room": True,  # 1.9.8
    "preferred_mental_reset_activities": [
        "games or puzzles",
        "social connection",
    ],  # 1.9.9
    "coping_mechanisms_when_stressed": ["alcohol", "excessive screen time"],  # 1.9.10
    "interest_categories": [  # 1.10.1
        "games & puzzles",
        "creative & craft",
        "sports, fitness & outdoors",
        "food & culinary",
    ],
    "current_interest_hours_per_week": 6,  # 1.10.2
    "desired_interest_hours_per_week": 10,  # 1.10.3
    "has_specific_projects": True,  # 1.10.4
    "open_to_sprint_sessions": True,  # 1.10.5
    "desired_unscheduled_downtime_hours_per_day": 2,  # 1.10.6
    "diet_style": "Mediterranean",  # 1.4.1
    "meals_at_home": 2,  # 1.4.2
    "meals_out": 1,  # 1.4.3
    "meal_duration": 45,  # 1.4.4
    "use_eating_window": True,  # 1.4.5
    "eating_window_start": "12:00",  # 1.4.5.2.1
    "eating_window_end": "20:00",  # 1.4.5.2.2
    "meal_composition": "balanced",  # 1.4.6
    "food_allergies": ["nuts"],  # 1.4.7
    "water_intake_cups": 8,  # 1.4.8
    "other_fluids": ["tea"],  # 1.4.9
    "digestion_issues": ["none"],  # 1.4.10
    "snacks_between_meals": True,  # 1.4.11
    "snacks_per_day": 2,  # 1.4.11.1.1
    "snack_types": {  # 1.4.11.2
        "sweet": False,
        "salty": True,
        "fruit": True,
        "protein": True,
        "other": False,
    },
    "foods_to_avoid": ["processed foods"],  # 1.4.12
    "hungry_within_2_hours": False,  # 1.4.13
    "hours_between_meals": 4,  # 1.4.14
    "meals_prep_in_advance": 3,  # 1.4.15
    "health_goals": [1, 3, 4],  # 1.6.1
    "usual_sleep_hours": 7.5,  # 1.6.2
    "trouble_sleeping": "Yes",  # 1.6.3
    "use_sleep_aids": "No",  # 1.6.4
    "earliest_wake_time": "05:30",  # 1.6.5
    "latest_bedtime": "23:00",  # 1.6.6
    "feel_rested_on_waking": "No",  # 1.6.9
    "use_screens_before_bed": "Yes",  # 1.6.10
    "cravings_evening": True,  # extra variable for bedtime adjustment
    "cooking_skill_level": "Intermediate",  # 1.4.16
    "daily_meal_prep_time": "16–30",  # 1.4.17
    "preferred_meal_prep_style": "Mix of fresh and batch prep",  # 1.4.18
    "kitchen_equipment_access": ["Stove", "Oven", "Microwave"],  # 1.4.19
}

for key, value in user_data.items():
    globals()[key] = value


def callwdata(function, data_dict):
    try:
        sig = inspect.signature(function)
        inputs = sig.parameters.keys()
        calldata = {}
        for k, v in data_dict.items():
            if k in inputs:
                calldata[k] = v
        return function(**calldata)
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
    return None


identity_questions = {
    "section": "1.1 Identity & Physical Baseline",
    "questions": [
        {
            "id": "1.1.1",
            "variable_name": "gender",
            "text": "What’s your gender?",
            "type": "single-select",
            "options": [
                {"id": "1.1.1.1", "text": "male"},
                {"id": "1.1.1.2", "text": "female"},
            ],
        },
        {
            "id": "1.1.2",
            "variable_name": "height_inches",
            "text": "What’s your height? (inches)",
            "type": "number",
            "range": {"min": 36, "max": 96},  # Example reasonable range
        },
        {
            "id": "1.1.3",
            "variable_name": "age",
            "text": "What’s your age?",
            "type": "number",
        },
        {
            "id": "1.1.4",
            "variable_name": "current_weight_lbs",
            "text": "What’s your current weight? (pounds)",
            "type": "number",
        },
        {
            "id": "1.1.5",
            "variable_name": "body_fat_percentage",
            "text": "What’s your approximate body fat percentage? (optional)",
            "type": "number",
            "optional": True,
        },
        {
            "id": "1.1.6",
            "variable_name": "target_weight_lbs",
            "text": "What’s your target weight? (pounds)",
            "type": "number",
        },
        {
            "id": "1.1.7",
            "variable_name": "target_body_area",
            "text": "Do you want to target a specific area of your body for improvement?",
            "type": "single-select",
            "options": [
                {"id": "1.1.7.1", "text": "no"},
                {"id": "1.1.7.2", "text": "belly"},
                {"id": "1.1.7.3", "text": "thighs"},
                {"id": "1.1.7.4", "text": "chest"},
                {"id": "1.1.7.5", "text": "arms"},
                {"id": "1.1.7.6", "text": "glutes"},
                {"id": "1.1.7.7", "text": "back"},
                {"id": "1.1.7.8", "text": "full body"},
                {"id": "1.1.7.9", "text": "other"},
            ],
        },
    ],
}

daily_rhythm_questions = {
    "section": "1.2 Daily Rhythm & Structure",
    "questions": [
        {
            "id": "1.2.5",
            "variable_name": "has_daily_responsibilities",
            "text": "Do you have daily responsibilities that occupy specific hours?",
            "type": "single-select",
            "options": [
                {"id": "1.2.5.1", "text": "yes"},
                {"id": "1.2.5.2", "text": "no"},
            ],
        },
        {
            "id": "1.2.6",
            "variable_name": "responsibility_days_per_week",
            "text": "If yes, how many days per week are those responsibilities scheduled? (0–7)",
            "type": "number",
            "range": {"min": 0, "max": 7},
            "conditional_on": {
                "variable_name": "has_daily_responsibilities",
                "value": "yes",
            },
        },
        {
            "id": "1.2.7_start",
            "variable_name": "responsibility_start_time",
            "text": "What time do your daily responsibilities start? (HH:MM, 24-hour)",
            "type": "time_24h",
            "conditional_on": {
                "variable_name": "has_daily_responsibilities",
                "value": "yes",
            },
        },
        {
            "id": "1.2.7_end",
            "variable_name": "responsibility_end_time",
            "text": "What time do your daily responsibilities end? (HH:MM, 24-hour)",
            "type": "time_24h",
            "conditional_on": {
                "variable_name": "has_daily_responsibilities",
                "value": "yes",
            },
        },
        {
            "id": "1.2.8a",
            "variable_name": "pet_care_morning",
            "text": "Do you care for pets in the morning?",
            "type": "single-select",
            "options": [
                {"id": "1.2.8a.1", "text": "yes"},
                {"id": "1.2.8a.2", "text": "no"},
            ],
        },
        {
            "id": "1.2.8a_start",
            "variable_name": "pet_care_morning_start_time",
            "text": "What time do you typically start morning pet care? (HH:MM, 24-hour)",
            "type": "time_24h",
            "conditional_on": {"variable_name": "pet_care_morning", "value": "yes"},
        },
        {
            "id": "1.2.8a_end",
            "variable_name": "pet_care_morning_end_time",
            "text": "What time do you typically finish morning pet care? (HH:MM, 24-hour)",
            "type": "time_24h",
            "conditional_on": {"variable_name": "pet_care_morning", "value": "yes"},
        },
        {
            "id": "1.2.8b",
            "variable_name": "pet_care_evening",
            "text": "Do you care for pets in the evening?",
            "type": "single-select",
            "options": [
                {"id": "1.2.8b.1", "text": "yes"},
                {"id": "1.2.8b.2", "text": "no"},
            ],
        },
        {
            "id": "1.2.8b_start",
            "variable_name": "pet_care_evening_start_time",
            "text": "What time do you typically start evening pet care? (HH:MM, 24-hour)",
            "type": "time_24h",
            "conditional_on": {"variable_name": "pet_care_evening", "value": "yes"},
        },
        {
            "id": "1.2.8b_end",
            "variable_name": "pet_care_evening_end_time",
            "text": "What time do you typically finish evening pet care? (HH:MM, 24-hour)",
            "type": "time_24h",
            "conditional_on": {"variable_name": "pet_care_evening", "value": "yes"},
        },
        {
            "id": "1.2.9",
            "variable_name": "others_rely_on_time",
            "text": "Do other people regularly rely on your time or attention during the day?",
            "type": "single-select",
            "options": [
                {"id": "1.2.9.1", "text": "yes"},
                {"id": "1.2.9.2", "text": "no"},
            ],
        },
    ],
}

substances_questions = {
    "section": "1.3 Substances & Regulation",
    "questions": [
        {
            "id": "1.3.1",
            "variable_name": "use_tobacco",
            "text": "Do you currently use tobacco products?",
            "type": "single-select",
            "options": [
                {"id": "1.3.1.1", "text": "Yes"},
                {"id": "1.3.1.2", "text": "No"},
            ],
        },
        {
            "id": "1.3.2",
            "variable_name": "tobacco_type",
            "text": "If yes, what type?",
            "type": "multi-select",
            "options": [
                {"id": "1.3.2.1", "text": "Cigarette"},
                {"id": "1.3.2.2", "text": "Cigar"},
                {"id": "1.3.2.3", "text": "Vape"},
                {"id": "1.3.2.4", "text": "Chewing tobacco"},
                {"id": "1.3.2.5", "text": "Other"},
            ],
            "conditional_on": {"variable_name": "use_tobacco", "value": "Yes"},
        },
        {
            "id": "1.3.3",
            "variable_name": "tobacco_quantity",
            "text": "How many?",
            "type": "number",
            "conditional_on": {"variable_name": "use_tobacco", "value": "Yes"},
        },
        {
            "id": "1.3.4",
            "variable_name": "tobacco_frequency",
            "text": "Frequency",
            "type": "single-select",
            "options": [
                {"id": "1.3.4.1", "text": "Per day"},
                {"id": "1.3.4.2", "text": "Per week"},
            ],
            "conditional_on": {"variable_name": "use_tobacco", "value": "Yes"},
        },
        {
            "id": "1.3.5",
            "variable_name": "tobacco_goal",
            "text": "Goal for this plan:",
            "type": "single-select",
            "options": [
                {"id": "1.3.5.1", "text": "No change"},
                {"id": "1.3.5.2", "text": "Reduce"},
                {"id": "1.3.5.3", "text": "Quit entirely"},
            ],
            "conditional_on": {"variable_name": "use_tobacco", "value": "Yes"},
        },
        {
            "id": "1.3.6",
            "variable_name": "tobacco_cravings_time",
            "text": "Strongest cravings:",
            "type": "single-select",
            "options": [
                {"id": "1.3.6.1", "text": "All day"},
                {"id": "1.3.6.2", "text": "Mornings"},
                {"id": "1.3.6.3", "text": "Afternoons"},
                {"id": "1.3.6.4", "text": "Evenings"},
                {"id": "1.3.6.5", "text": "Late nights"},
                {"id": "1.3.6.6", "text": "Weekends"},
                {"id": "1.3.6.7", "text": "None"},
            ],
            "conditional_on": {"variable_name": "use_tobacco", "value": "Yes"},
        },
        {
            "id": "1.3.7",
            "variable_name": "use_marijuana",
            "text": "Do you currently use marijuana?",
            "type": "single-select",
            "options": [
                {"id": "1.3.7.1", "text": "Yes"},
                {"id": "1.3.7.2", "text": "No"},
            ],
        },
        {
            "id": "1.3.8",
            "variable_name": "marijuana_type",
            "text": "If yes, what type?",
            "type": "multi-select",
            "options": [
                {"id": "1.3.8.1", "text": "Joint"},
                {"id": "1.3.8.2", "text": "Edible"},
                {"id": "1.3.8.3", "text": "Vape"},
                {"id": "1.3.8.4", "text": "Tincture"},
                {"id": "1.3.8.5", "text": "Other"},
            ],
            "conditional_on": {"variable_name": "use_marijuana", "value": "Yes"},
        },
        {
            "id": "1.3.9",
            "variable_name": "marijuana_quantity",
            "text": "How many?",
            "type": "number",
            "conditional_on": {"variable_name": "use_marijuana", "value": "Yes"},
        },
        {
            "id": "1.3.10",
            "variable_name": "marijuana_frequency",
            "text": "Frequency",
            "type": "single-select",
            "options": [
                {"id": "1.3.10.1", "text": "Per day"},
                {"id": "1.3.10.2", "text": "Per week"},
            ],
            "conditional_on": {"variable_name": "use_marijuana", "value": "Yes"},
        },
        {
            "id": "1.3.11",
            "variable_name": "marijuana_goal",
            "text": "Goal for this plan:",
            "type": "single-select",
            "options": [
                {"id": "1.3.11.1", "text": "No change"},
                {"id": "1.3.11.2", "text": "Reduce"},
                {"id": "1.3.11.3", "text": "Quit entirely"},
            ],
            "conditional_on": {"variable_name": "use_marijuana", "value": "Yes"},
        },
        {
            "id": "1.3.12",
            "variable_name": "marijuana_cravings_time",
            "text": "Strongest cravings:",
            "type": "single-select",
            "options": [
                {"id": "1.3.12.1", "text": "All day"},
                {"id": "1.3.12.2", "text": "Mornings"},
                {"id": "1.3.12.3", "text": "Afternoons"},
                {"id": "1.3.12.4", "text": "Evenings"},
                {"id": "1.3.12.5", "text": "Late nights"},
                {"id": "1.3.12.6", "text": "Weekends"},
                {"id": "1.3.12.7", "text": "None"},
            ],
            "conditional_on": {"variable_name": "use_marijuana", "value": "Yes"},
        },
        {
            "id": "1.3.13",
            "variable_name": "use_alcohol",
            "text": "Do you drink alcohol?",
            "type": "single-select",
            "options": [
                {"id": "1.3.13.1", "text": "Yes"},
                {"id": "1.3.13.2", "text": "No"},
            ],
        },
        {
            "id": "1.3.14",
            "variable_name": "alcohol_quantity",
            "text": "How many drinks?",
            "type": "number",
            "conditional_on": {"variable_name": "use_alcohol", "value": "Yes"},
        },
        {
            "id": "1.3.15",
            "variable_name": "alcohol_frequency",
            "text": "Frequency",
            "type": "single-select",
            "options": [
                {"id": "1.3.15.1", "text": "Per day"},
                {"id": "1.3.15.2", "text": "Per week"},
            ],
            "conditional_on": {"variable_name": "use_alcohol", "value": "Yes"},
        },
        {
            "id": "1.3.16",
            "variable_name": "alcohol_goal",
            "text": "Goal for this plan:",
            "type": "single-select",
            "options": [
                {"id": "1.3.16.1", "text": "No change"},
                {"id": "1.3.16.2", "text": "Reduce"},
                {"id": "1.3.16.3", "text": "Quit entirely"},
            ],
            "conditional_on": {"variable_name": "use_alcohol", "value": "Yes"},
        },
        {
            "id": "1.3.17",
            "variable_name": "alcohol_cravings_time",
            "text": "Strongest cravings:",
            "type": "single-select",
            "options": [
                {"id": "1.3.17.1", "text": "All day"},
                {"id": "1.3.17.2", "text": "Mornings"},
                {"id": "1.3.17.3", "text": "Afternoons"},
                {"id": "1.3.17.4", "text": "Evenings"},
                {"id": "1.3.17.5", "text": "Late nights"},
                {"id": "1.3.17.6", "text": "Weekends"},
                {"id": "1.3.17.7", "text": "None"},
            ],
            "conditional_on": {"variable_name": "use_alcohol", "value": "Yes"},
        },
        {
            "id": "1.3.18",
            "variable_name": "use_caffeine",
            "text": "Do you drink caffeine?",
            "type": "single-select",
            "options": [
                {"id": "1.3.18.1", "text": "Yes"},
                {"id": "1.3.18.2", "text": "No"},
            ],
        },
        {
            "id": "1.3.19",
            "variable_name": "caffeine_type",
            "text": "If yes, what type?",
            "type": "multi-select",
            "options": [
                {"id": "1.3.19.1", "text": "Coffee"},
                {"id": "1.3.19.2", "text": "Energy drink"},
                {"id": "1.3.19.3", "text": "Tea"},
                {"id": "1.3.19.4", "text": "Soda"},
                {"id": "1.3.19.5", "text": "Other"},
            ],
            "conditional_on": {"variable_name": "use_caffeine", "value": "Yes"},
        },
        {
            "id": "1.3.20",
            "variable_name": "caffeine_quantity",
            "text": "How much?",
            "type": "number",
            "conditional_on": {"variable_name": "use_caffeine", "value": "Yes"},
        },
        {
            "id": "1.3.21",
            "variable_name": "caffeine_frequency",
            "text": "Frequency",
            "type": "single-select",
            "options": [
                {"id": "1.3.21.1", "text": "Per day"},
                {"id": "1.3.21.2", "text": "Per week"},
            ],
            "conditional_on": {"variable_name": "use_caffeine", "value": "Yes"},
        },
        {
            "id": "1.3.22",
            "variable_name": "caffeine_goal",
            "text": "Goal for this plan:",
            "type": "single-select",
            "options": [
                {"id": "1.3.22.1", "text": "No change"},
                {"id": "1.3.22.2", "text": "Reduce"},
                {"id": "1.3.22.3", "text": "Quit entirely"},
            ],
            "conditional_on": {"variable_name": "use_caffeine", "value": "Yes"},
        },
        {
            "id": "1.3.23",
            "variable_name": "caffeine_cravings_time",
            "text": "Strongest cravings:",
            "type": "single-select",
            "options": [
                {"id": "1.3.23.1", "text": "All day"},
                {"id": "1.3.23.2", "text": "Mornings"},
                {"id": "1.3.23.3", "text": "Afternoons"},
                {"id": "1.3.23.4", "text": "Evenings"},
                {"id": "1.3.23.5", "text": "Late nights"},
                {"id": "1.3.23.6", "text": "Weekends"},
                {"id": "1.3.23.7", "text": "None"},
            ],
            "conditional_on": {"variable_name": "use_caffeine", "value": "Yes"},
        },
    ],
}

medications_questions = {
    "section": "1.5 Medications & Supplements",
    "questions": [
        {
            "id": "1.5.1",
            "variable_name": "take_daily_meds_supplements",
            "text": "Do you take any prescriptions, supplements, or vitamins daily?",
            "type": "single-select",
            "options": [
                {"id": "1.5.1.1", "text": "yes"},
                {"id": "1.5.1.2", "text": "no"},
            ],
        },
        {
            "id": "1.5.2",
            "variable_name": "meds_supplements_times",
            "text": "At what times do you typically take them?",
            "type": "multi-select",
            "options": [
                {"id": "1.5.2.1", "text": "early morning (6–9 AM)"},
                {"id": "1.5.2.2", "text": "mid-day (11 AM–2 PM)"},
                {"id": "1.5.2.3", "text": "afternoon (2–5 PM)"},
                {"id": "1.5.2.4", "text": "evening (5–8 PM)"},
                {"id": "1.5.2.5", "text": "bedtime (8–11 PM)"},
                {"id": "1.5.2.6", "text": "as needed"},
            ],
            "conditional_on": {
                "variable_name": "take_daily_meds_supplements",
                "value": "yes",
            },
        },
        {
            "id": "1.5.3",
            "variable_name": "include_med_reminders",
            "text": "Should I include reminders for your meds or supplements at those times?",
            "type": "single-select",
            "options": [
                {"id": "1.5.3.1", "text": "yes"},
                {"id": "1.5.3.2", "text": "no"},
            ],
            "conditional_on": {
                "variable_name": "take_daily_meds_supplements",
                "value": "yes",
            },
        },
    ],
}

fitness_questions = {
    "section": "1.7 Fitness & Physical Capacity",
    "questions": [
        {
            "id": "1.7.1",
            "variable_name": "gym_access",
            "text": "Do you have access to a gym or fitness facility?",
            "type": "single-select",
            "options": [
                {"id": "1.7.1.1", "text": "yes"},
                {"id": "1.7.1.2", "text": "no"},
            ],
        },
        {
            "id": "1.7.2",
            "variable_name": "preferred_workout_location",
            "text": "Where do you prefer to work out?",
            "type": "single-select",
            "options": [
                {"id": "1.7.2.1", "text": "at home"},
                {"id": "1.7.2.2", "text": "gym or fitness center"},
                {"id": "1.7.2.3", "text": "outdoors (parks, trails)"},
                {"id": "1.7.2.4", "text": "studio or class (yoga, spin, etc.)"},
                {"id": "1.7.2.5", "text": "do not prefer to work out"},
                {"id": "1.7.2.6", "text": "other"},
            ],
        },
        {
            "id": "1.7.3",
            "variable_name": "home_fitness_equipment",
            "text": "Which fitness equipment do you have available at home?",
            "type": "multi-select",
            "options": [
                {"id": "1.7.3.1", "text": "resistance bands"},
                {"id": "1.7.3.2", "text": "dumbbells or kettlebells"},
                {"id": "1.7.3.3", "text": "barbell or weight plates"},
                {"id": "1.7.3.4", "text": "cardio machine (bike, treadmill, rower)"},
                {"id": "1.7.3.5", "text": "yoga mat or floor space"},
                {"id": "1.7.3.6", "text": "none"},
                {"id": "1.7.3.7", "text": "other"},
            ],
        },
        {
            "id": "1.7.4",
            "variable_name": "injuries_or_limitations",
            "text": "Do you have any injuries or physical limitations?",
            "type": "single-select",
            "options": [
                {"id": "1.7.4.1", "text": "yes"},
                {"id": "1.7.4.2", "text": "no"},
            ],
        },
        {
            "id": "1.7.5",
            "variable_name": "exercise_types_enjoyed",
            "text": "Which types of exercise do you enjoy?",
            "type": "multi-select",
            "options": [
                {"id": "1.7.5.1", "text": "strength training (weights, bodyweight)"},
                {"id": "1.7.5.2", "text": "cardio (running, biking, HIIT)"},
                {"id": "1.7.5.3", "text": "flexibility or mobility (yoga, stretching)"},
                {"id": "1.7.5.4", "text": "balance or stability (Pilates, tai chi)"},
                {"id": "1.7.5.5", "text": "sports or recreational activities"},
                {"id": "1.7.5.6", "text": "do not enjoy exercising"},
                {"id": "1.7.5.7", "text": "other"},
            ],
        },
        {
            "id": "1.7.6",
            "variable_name": "preferred_workout_time",
            "text": "What time of day do you prefer to work out?",
            "type": "single-select",
            "options": [
                {"id": "1.7.6.1", "text": "early morning (5–8 AM)"},
                {"id": "1.7.6.2", "text": "late morning (8–11 AM)"},
                {"id": "1.7.6.3", "text": "afternoon (11 AM–3 PM)"},
                {"id": "1.7.6.4", "text": "late afternoon (3–6 PM)"},
                {"id": "1.7.6.5", "text": "evening (6–9 PM)"},
            ],
        },
        {
            "id": "1.7.7",
            "variable_name": "daily_fitness_minutes",
            "text": "How much time can you dedicate to fitness each day? (minutes)",
            "type": "number",
        },
        {
            "id": "1.7.8",
            "variable_name": "current_activity_level",
            "text": "How would you describe your current activity level?",
            "type": "single-select",
            "options": [
                {"id": "1.7.8.1", "text": "sedentary"},
                {"id": "1.7.8.2", "text": "light activity (1–2 days/week)"},
                {"id": "1.7.8.3", "text": "moderate activity (3–5 days/week)"},
                {"id": "1.7.8.4", "text": "high activity (6–7 days/week)"},
            ],
        },
        {
            "id": "1.7.9",
            "variable_name": "fitness_goals",
            "text": "Do you have specific fitness goals?",
            "type": "multi-select",
            "options": [
                {"id": "1.7.9.1", "text": "increase strength"},
                {"id": "1.7.9.2", "text": "improve endurance"},
                {"id": "1.7.9.3", "text": "enhance flexibility"},
                {"id": "1.7.9.4", "text": "lose body fat"},
                {"id": "1.7.9.5", "text": "build muscle"},
                {"id": "1.7.9.6", "text": "improve balance/coordination"},
                {"id": "1.7.9.7", "text": "other"},
                {"id": "1.7.9.8", "text": "no specific goals"},
            ],
        },
    ],
}

sexual_wellness_questions = {
    "section": "1.8 Sexual Wellness",
    "questions": [
        {
            "id": "1.8.1",
            "variable_name": "sexual_partners_per_month",
            "text": "How many different sexual partners per month? (number)",
            "type": "number",
        },
        {
            "id": "1.8.2",
            "variable_name": "partnered_sex_frequency_per_week",
            "text": "Current partnered sex frequency per week? (number)",
            "type": "number",
        },
        {
            "id": "1.8.3",
            "variable_name": "solo_play_frequency_per_week",
            "text": "Current solo play frequency per week? (number)",
            "type": "number",
        },
        {
            "id": "1.8.4",
            "variable_name": "relationship_status",
            "text": "Relationship status",
            "type": "single-select",
            "options": [
                {"id": "1.8.4.1", "text": "single"},
                {"id": "1.8.4.2", "text": "monogamous partnership only"},
                {"id": "1.8.4.3", "text": "monogamous partnership (exploring)"},
                {"id": "1.8.4.4", "text": "open relationship"},
                {"id": "1.8.4.5", "text": "polyamorous"},
                {"id": "1.8.4.6", "text": "other"},
            ],
        },
        {
            "id": "1.8.5",
            "variable_name": "sexual_orientation",
            "text": "Sexual orientation",
            "type": "single-select",
            "options": [
                {"id": "1.8.5.1", "text": "straight"},
                {"id": "1.8.5.2", "text": "gay"},
                {"id": "1.8.5.3", "text": "bisexual"},
                {"id": "1.8.5.4", "text": "pansexual"},
                {"id": "1.8.5.5", "text": "other"},
            ],
        },
        {
            "id": "1.8.6",
            "variable_name": "solo_play_methods",
            "text": "Usual solo-play methods",
            "type": "multi-select",
            "options": [
                {"id": "1.8.6.1", "text": "manual stimulation"},
                {"id": "1.8.6.2", "text": "vibrator or toy"},
                {"id": "1.8.6.3", "text": "porn or erotic media"},
                {"id": "1.8.6.4", "text": "other"},
            ],
        },
        {
            "id": "1.8.7",
            "variable_name": "partnered_activity_types",
            "text": "Usual partnered-activity types",
            "type": "multi-select",
            "options": [
                {"id": "1.8.7.1", "text": "vaginal intercourse"},
                {"id": "1.8.7.2", "text": "anal intercourse"},
                {"id": "1.8.7.3", "text": "oral sex (giving)"},
                {"id": "1.8.7.4", "text": "oral sex (receiving)"},
                {"id": "1.8.7.5", "text": "other"},
            ],
        },
        {
            "id": "1.8.8",
            "variable_name": "regular_uninterrupted_time_for_sexual_activity",
            "text": "Do you have regular uninterrupted time for sexual activity?",
            "type": "single-select",
            "options": [
                {"id": "1.8.8.1", "text": "yes"},
                {"id": "1.8.8.2", "text": "no"},
            ],
        },
        {
            "id": "1.8.9",
            "variable_name": "satisfaction_with_frequency",
            "text": "Satisfaction with frequency",
            "type": "single-select",
            "options": [
                {"id": "1.8.9.1", "text": "very satisfied"},
                {"id": "1.8.9.2", "text": "somewhat satisfied"},
                {"id": "1.8.9.3", "text": "neutral"},
                {"id": "1.8.9.4", "text": "somewhat dissatisfied"},
                {"id": "1.8.9.5", "text": "very dissatisfied"},
            ],
        },
        {
            "id": "1.8.10",
            "variable_name": "satisfaction_with_quality",
            "text": "Satisfaction with quality",
            "type": "single-select",
            "options": [
                {"id": "1.8.10.1", "text": "very satisfied"},
                {"id": "1.8.10.2", "text": "somewhat satisfied"},
                {"id": "1.8.10.3", "text": "neutral"},
                {"id": "1.8.10.4", "text": "somewhat dissatisfied"},
                {"id": "1.8.10.5", "text": "very dissatisfied"},
            ],
        },
        {
            "id": "1.8.11",
            "variable_name": "contraception_safety_methods",
            "text": "Contraception & safety methods",
            "type": "multi-select",
            "options": [
                {"id": "1.8.11.1", "text": "condoms"},
                {"id": "1.8.11.2", "text": "hormonal birth control"},
                {"id": "1.8.11.3", "text": "IUD or implant"},
                {"id": "1.8.11.4", "text": "barrier methods"},
                {"id": "1.8.11.5", "text": "none"},
                {"id": "1.8.11.6", "text": "other"},
            ],
        },
        {
            "id": "1.8.12",
            "variable_name": "menstrual_periods",
            "text": "Menstrual periods? (female only)",
            "type": "single-select",
            "options": [
                {"id": "1.8.12.1f", "text": "yes"},
                {"id": "1.8.12.2f", "text": "no"},
            ],
        },
        {
            "id": "1.8.12.1f.1",
            "variable_name": "track_cycle",
            "text": "Do you track your menstrual cycle?",
            "type": "single-select",
            "options": [
                {"id": "1.8.12.1.1", "text": "yes"},
                {"id": "1.8.12.1.2", "text": "no"},
            ],
            "conditional_on": {"variable_name": "menstrual_periods", "value": "yes"},
        },
        {
            "id": "1.8.12.1f.2",
            "variable_name": "menstrual_phase",
            "text": "Which phase are you currently in?",
            "type": "single-select",
            "options": [
                {"id": "1.8.12.1.2.1", "text": "menstrual"},
                {"id": "1.8.12.1.2.2", "text": "follicular"},
                {"id": "1.8.12.1.2.3", "text": "ovulation"},
                {"id": "1.8.12.1.2.4", "text": "luteal"},
            ],
            "conditional_on": {"variable_name": "menstrual_periods", "value": "yes"},
        },
        {
            "id": "1.8.13",
            "variable_name": "male_performance_goals",
            "text": "Do you have any Performance goals – male",
            "type": "multi-select",
            "options": [
                {"id": "1.8.13.1m", "text": "stamina"},
                {"id": "1.8.13.2m", "text": "control / delay orgasm"},
                {"id": "1.8.13.3m", "text": "orgasm intensity"},
                {"id": "1.8.13.4m", "text": "libido / arousal"},
                {"id": "1.8.13.5m", "text": "erection quality"},
                {"id": "1.8.13.6m", "text": "ejaculatory volume"},
                {"id": "1.8.13.7m", "text": "reduce performance anxiety"},
                {"id": "1.8.13.8m", "text": "enhance partner satisfaction"},
                {"id": "1.8.13.9m", "text": "other"},
            ],
        },
        {
            "id": "1.8.14",
            "variable_name": "female_performance_goals",
            "text": "Do you have any Performance goals – female",
            "type": "multi-select",
            "options": [
                {"id": "1.8.14.1f", "text": "stamina"},
                {"id": "1.8.14.2f", "text": "control / delay orgasm"},
                {"id": "1.8.14.3f", "text": "orgasm intensity (clitoral or G-spot)"},
                {"id": "1.8.14.4f", "text": "libido / arousal"},
                {"id": "1.8.14.5f", "text": "natural lubrication"},
                {"id": "1.8.14.6f", "text": "clitoral sensitivity"},
                {"id": "1.8.14.7f", "text": "multiple orgasms"},
                {"id": "1.8.14.8f", "text": "reduce discomfort or pain"},
                {"id": "1.8.14.9f", "text": "intimacy / sensual connection"},
                {"id": "1.8.14.10f", "text": "other"},
            ],
        },
        {
            "id": "1.8.15",
            "variable_name": "issues_with_stamina_control_sensitivity_or_discomfort",
            "text": "Do you experience any issues with stamina, control, sensitivity, or discomfort?",
            "type": "single-select",
            "options": [
                {"id": "1.8.15.1", "text": "yes"},
                {"id": "1.8.15.2", "text": "no"},
            ],
        },
    ],
}

stress_work_tech_questions = {
    "section": "1.9 Stress, Work, Tech",
    "questions": [
        {
            "id": "1.9.1",
            "variable_name": "daily_stress_causes",
            "text": "Which of these cause you the most daily stress? (select up to 3)",
            "type": "multi-select",
            "options": [
                {"id": "1.9.1.1", "text": "Work deadlines"},
                {"id": "1.9.1.2", "text": "Financial concerns"},
                {"id": "1.9.1.3", "text": "Relationship issues"},
                {"id": "1.9.1.4", "text": "Health worries"},
                {"id": "1.9.1.5", "text": "Family or caregiving"},
                {"id": "1.9.1.6", "text": "Time pressure"},
                {"id": "1.9.1.7", "text": "Information overload"},
                {"id": "1.9.1.8", "text": "Other"},
            ],
        },
        {
            "id": "1.9.2",
            "variable_name": "uses_stress_relief_tools",
            "text": "Do you currently use any stress-relief or mindfulness tools?",
            "type": "single-select",
            "options": [
                {"id": "1.9.2.1", "text": "no"},
                {"id": "1.9.2.2", "text": "yes"},
            ],
        },
        {
            "id": "1.9.2.2.1",
            "variable_name": "stress_tool_meditation_app",
            "text": "Meditation app",
            "type": "boolean",
            "conditional_on": {
                "variable_name": "uses_stress_relief_tools",
                "value": "yes",
            },
        },
        {
            "id": "1.9.2.2.2",
            "variable_name": "stress_tool_journaling",
            "text": "Journaling",
            "type": "boolean",
            "conditional_on": {
                "variable_name": "uses_stress_relief_tools",
                "value": "yes",
            },
        },
        {
            "id": "1.9.2.2.3",
            "variable_name": "stress_tool_deep_breathing",
            "text": "Deep breathing",
            "type": "boolean",
            "conditional_on": {
                "variable_name": "uses_stress_relief_tools",
                "value": "yes",
            },
        },
        {
            "id": "1.9.2.2.4",
            "variable_name": "stress_tool_yoga",
            "text": "Yoga",
            "type": "boolean",
            "conditional_on": {
                "variable_name": "uses_stress_relief_tools",
                "value": "yes",
            },
        },
        {
            "id": "1.9.2.2.5",
            "variable_name": "stress_tool_other",
            "text": "Other",
            "type": "boolean",
            "conditional_on": {
                "variable_name": "uses_stress_relief_tools",
                "value": "yes",
            },
        },
        {
            "id": "1.9.3",
            "variable_name": "can_take_breaks",
            "text": "Can you take breaks during your main responsibilities?",
            "type": "single-select",
            "options": [
                {"id": "1.9.3.1", "text": "yes"},
                {"id": "1.9.3.2", "text": "no"},
            ],
        },
        {
            "id": "1.9.4",
            "variable_name": "has_space_for_movement_sessions",
            "text": "Do you have space or time for short movement sessions during the day?",
            "type": "single-select",
            "options": [
                {"id": "1.9.4.1", "text": "yes"},
                {"id": "1.9.4.2", "text": "no"},
            ],
        },
        {
            "id": "1.9.5",
            "variable_name": "preferred_time_for_unscheduled_activities",
            "text": "Which part of your day is more flexible for unscheduled activities?",
            "type": "single-select",
            "options": [
                {"id": "1.9.5.1", "text": "mornings"},
                {"id": "1.9.5.2", "text": "afternoons"},
                {"id": "1.9.5.3", "text": "evenings"},
                {"id": "1.9.5.4", "text": "no clear preference"},
            ],
        },
        {
            "id": "1.9.6",
            "variable_name": "desired_free_time_per_day_hours",
            "text": "How many hours of free or unscheduled time do you want each day? (0–12)",
            "type": "number",
        },
        {
            "id": "1.9.7",
            "variable_name": "screen_time_outside_work_hours",
            "text": "Outside of work or study, how many hours per day do you spend on screens? (0–12)",
            "type": "number",
        },
        {
            "id": "1.9.8",
            "variable_name": "sleep_with_phone_in_room",
            "text": "Do you sleep with your phone or other devices in the same room?",
            "type": "single-select",
            "options": [
                {"id": "1.9.8.1", "text": "yes"},
                {"id": "1.9.8.2", "text": "no"},
            ],
        },
        {
            "id": "1.9.9",
            "variable_name": "preferred_mental_reset_activities",
            "text": "Which mental-reset activities work best for you? (select up to 3)",
            "type": "multi-select",
            "options": [
                {"id": "1.9.9.1", "text": "Silence / quiet"},
                {"id": "1.9.9.2", "text": "Music"},
                {"id": "1.9.9.3", "text": "Games or puzzles"},
                {"id": "1.9.9.4", "text": "Nature / outdoors"},
                {"id": "1.9.9.5", "text": "Guided meditation"},
                {"id": "1.9.9.6", "text": "Movement / stretching"},
                {"id": "1.9.9.7", "text": "Social connection"},
                {"id": "1.9.9.8", "text": "Other"},
            ],
        },
        {
            "id": "1.9.10",
            "variable_name": "coping_mechanisms_when_stressed",
            "text": "When you feel stressed, which coping mechanisms do you use?",
            "type": "multi-select",
            "options": [
                {"id": "1.9.10.1", "text": "Alcohol"},
                {"id": "1.9.10.2", "text": "Tobacco"},
                {"id": "1.9.10.3", "text": "Marijuana or cannabis"},
                {"id": "1.9.10.4", "text": "Caffeine"},
                {"id": "1.9.10.5", "text": "Eating or snacking"},
                {"id": "1.9.10.6", "text": "Excessive screen time"},
                {"id": "1.9.10.7", "text": "Impulse spending / shopping"},
                {"id": "1.9.10.8", "text": "Avoidance / procrastination"},
                {"id": "1.9.10.9", "text": "Self-harm or self-injury"},
                {"id": "1.9.10.10", "text": "Sex or masturbation"},
                {"id": "1.9.10.11", "text": "Other"},
            ],
        },
    ],
}

interests_lifestyle_questions = {
    "section": "1.10 Interests & Lifestyle",
    "questions": [
        {
            "id": "1.10.1",
            "variable_name": "interest_categories",
            "text": "Which of these interest categories would you be interested in or want to include as part of your daily life?",
            "type": "multi-select",
            "options": [
                {"id": "1.10.1.1", "text": "Games & Puzzles (board games, card games)"},
                {
                    "id": "1.10.1.2",
                    "text": "Creative & Craft (drawing, painting, woodworking, knitting, stained glass)",
                },
                {
                    "id": "1.10.1.3",
                    "text": "DIY & Mechanic (auto work, welding, home projects)",
                },
                {
                    "id": "1.10.1.4",
                    "text": "Sports, Fitness & Outdoors (team sports, hiking, camping, gym workouts)",
                },
                {
                    "id": "1.10.1.5",
                    "text": "Travel & Adventure (road trips, exploring)",
                },
                {
                    "id": "1.10.1.6",
                    "text": "Learning & Intellectual (reading, languages, politics, collecting)",
                },
                {
                    "id": "1.10.1.7",
                    "text": "Media & Entertainment (gaming, movies/TV, theater)",
                },
                {
                    "id": "1.10.1.8",
                    "text": "Social & Community (clubs, meetups, events)",
                },
                {
                    "id": "1.10.1.9",
                    "text": "Sexual Activities & Physical Pleasure (intimacy with partner, solo exploration, attending lifestyle events, erotic massage)",
                },
                {
                    "id": "1.10.1.10",
                    "text": "Food & Culinary (cooking, baking, exploring restaurants)",
                },
                {
                    "id": "1.10.1.11",
                    "text": "Home Improvement & Environment (gardening, organizing, décor, cleaning projects)",
                },
                {
                    "id": "1.10.1.12",
                    "text": "Financial & Career Growth (budgeting, investing, skill-building)",
                },
                {
                    "id": "1.10.1.13",
                    "text": "Volunteering & Giving Back (charity, activism, mentoring)",
                },
                {
                    "id": "1.10.1.14",
                    "text": "Mind & Spiritual Growth (meditation, religion, philosophy, personal reflection)",
                },
                {
                    "id": "1.10.1.15",
                    "text": "Animal & Pet Activities (training, care, play)",
                },
                {"id": "1.10.1.16", "text": "Other"},
            ],
        },
        {
            "id": "1.10.2",
            "variable_name": "current_interest_hours_per_week",
            "text": "How many hours per week do you currently spend on these interests? (hours)",
            "type": "number",
        },
        {
            "id": "1.10.3",
            "variable_name": "desired_interest_hours_per_week",
            "text": "How many hours per week would you like to spend on these interests? (hours)",
            "type": "number",
        },
        {
            "id": "1.10.4",
            "variable_name": "has_specific_projects",
            "text": "Do you have any specific projects you want to work on?",
            "type": "single-select",
            "options": [
                {"id": "1.10.4.1", "text": "yes"},
                {"id": "1.10.4.2", "text": "no"},
            ],
        },
        {
            "id": "1.10.5",
            "variable_name": "open_to_sprint_sessions",
            "text": "Are you open to scheduling focused sprint sessions?",
            "type": "single-select",
            "options": [
                {"id": "1.10.5.1", "text": "yes"},
                {"id": "1.10.5.2", "text": "no"},
            ],
        },
        {
            "id": "1.10.6",
            "variable_name": "desired_unscheduled_downtime_hours_per_day",
            "text": "How much unscheduled downtime would you like each day? (0–5)",
            "type": "number",
        },
    ],
}

diet_questions = {
    "section": "1.4 Food, Diet, and Digestion",
    "questions": [
        {
            "id": "1.4.1",
            "variable_name": "diet_style",
            "text": "Do you follow a specific diet or eating style?",
            "type": "single-select",
            "options": [
                {"id": "1.4.1.1", "text": "No"},
                {"id": "1.4.1.2", "text": "Keto"},
                {"id": "1.4.1.3", "text": "Paleo"},
                {"id": "1.4.1.4", "text": "Mediterranean"},
                {"id": "1.4.1.5", "text": "Vegetarian"},
                {"id": "1.4.1.6", "text": "Vegan"},
                {"id": "1.4.1.7", "text": "Other"},
            ],
        },
        {
            "id": "1.4.2",
            "variable_name": "meals_at_home",
            "text": "How many meals per day do you eat at home?",
            "type": "number",
            "range": {"min": 0, "max": 10},
        },
        {
            "id": "1.4.3",
            "variable_name": "meals_out",
            "text": "How many meals per day do you eat out or order in?",
            "type": "number",
            "range": {"min": 0, "max": 10},
        },
        {
            "id": "1.4.4",
            "variable_name": "meal_duration",
            "text": "How long does a typical meal take from prep to finish? (minutes)",
            "type": "number",
        },
        {
            "id": "1.4.5",
            "variable_name": "use_eating_window",
            "text": "Do you follow a specific eating window?",
            "type": "single-select",
            "options": [
                {"id": "1.4.5.1", "text": "No"},
                {"id": "1.4.5.2", "text": "Yes"},
            ],
        },
        {
            "id": "1.4.5.2.1",
            "variable_name": "eating_window_start",
            "text": "If yes, what is the start time of your eating window? (hour + AM/PM)",
            "type": "time",
        },
        {
            "id": "1.4.5.2.2",
            "variable_name": "eating_window_end",
            "text": "If yes, what is the end time of your eating window? (hour + AM/PM)",
            "type": "time",
        },
        {
            "id": "1.4.6",
            "variable_name": "meal_composition",
            "text": "What’s your typical meal composition?",
            "type": "single-select",
            "options": [
                {"id": "1.4.6.1", "text": "High-protein"},
                {"id": "1.4.6.2", "text": "High-carb"},
                {"id": "1.4.6.3", "text": "High-fat"},
                {"id": "1.4.6.4", "text": "Balanced"},
                {"id": "1.4.6.5", "text": "Other"},
            ],
        },
        {
            "id": "1.4.7",
            "variable_name": "food_allergies",
            "text": "Do you have any food allergies or intolerances?",
            "type": "multi-select",
            "options": [
                {"id": "1.4.7.1", "text": "Gluten"},
                {"id": "1.4.7.2", "text": "Dairy"},
                {"id": "1.4.7.3", "text": "Nuts"},
                {"id": "1.4.7.4", "text": "Shellfish"},
                {"id": "1.4.7.5", "text": "Soy"},
                {"id": "1.4.7.6", "text": "Eggs"},
                {"id": "1.4.7.7", "text": "Other"},
                {"id": "1.4.7.8", "text": "None"},
            ],
        },
        {
            "id": "1.4.8",
            "variable_name": "water_intake_cups",
            "text": "How much water do you drink daily? (cups)",
            "type": "number",
        },
        {
            "id": "1.4.9",
            "variable_name": "other_fluids",
            "text": "Which of these other fluids do you consume regularly?",
            "type": "multi-select",
            "options": [
                {"id": "1.4.9.1", "text": "Juice"},
                {"id": "1.4.9.2", "text": "Soda"},
                {"id": "1.4.9.3", "text": "Energy Drinks"},
                {"id": "1.4.9.4", "text": "Coffee"},
                {"id": "1.4.9.5", "text": "Tea"},
                {"id": "1.4.9.6", "text": "Other"},
                {"id": "1.4.9.7", "text": "None"},
            ],
        },
        {
            "id": "1.4.10",
            "variable_name": "digestion_issues",
            "text": "Do you experience any common digestion issues?",
            "type": "multi-select",
            "options": [
                {"id": "1.4.10.1", "text": "Bloating"},
                {"id": "1.4.10.2", "text": "Acid reflux"},
                {"id": "1.4.10.3", "text": "Irregularity"},
                {"id": "1.4.10.4", "text": "Gas"},
                {"id": "1.4.10.5", "text": "None"},
            ],
        },
        {
            "id": "1.4.11",
            "variable_name": "snacks_between_meals",
            "text": "Do you snack between meals?",
            "type": "single-select",
            "options": [
                {"id": "1.4.11.1", "text": "Yes"},
                {"id": "1.4.11.2", "text": "No"},
            ],
        },
        {
            "id": "1.4.11.1.1",
            "variable_name": "snacks_per_day",
            "text": "If yes, how many snacks per day?",
            "type": "number",
        },
        {
            "id": "1.4.11.2",
            "variable_name": "snack_types",
            "text": "What types of snacks do you usually have? (select all that apply)",
            "type": "multi-select",
            "options": [
                {"id": "1.4.11.2.1", "text": "Sweet", "value": "sweet"},
                {"id": "1.4.11.2.2", "text": "Salty", "value": "salty"},
                {"id": "1.4.11.2.3", "text": "Fruit", "value": "fruit"},
                {"id": "1.4.11.2.4", "text": "Protein", "value": "protein"},
                {"id": "1.4.11.2.5", "text": "Other", "value": "other"},
            ],
        },
        {
            "id": "1.4.12",
            "variable_name": "foods_to_avoid",
            "text": "Are there any foods you want to avoid or limit?",
            "type": "multi-select",
            "options": [
                {"id": "1.4.12.1", "text": "Gluten"},
                {"id": "1.4.12.2", "text": "Dairy"},
                {"id": "1.4.12.3", "text": "Sugar"},
                {"id": "1.4.12.4", "text": "Red meat"},
                {"id": "1.4.12.5", "text": "Processed foods"},
                {"id": "1.4.12.6", "text": "Other"},
                {"id": "1.4.12.7", "text": "None"},
            ],
        },
        {
            "id": "1.4.13",
            "variable_name": "hungry_within_2_hours",
            "text": "Do you often feel hungry within 2 hours after a meal?",
            "type": "single-select",
            "options": [
                {"id": "1.4.13.1", "text": "Yes"},
                {"id": "1.4.13.2", "text": "No"},
            ],
        },
        {
            "id": "1.4.14",
            "variable_name": "hours_between_meals",
            "text": "How many hours typically pass between your meals?",
            "type": "number",
        },
        {
            "id": "1.4.15",
            "variable_name": "meals_prep_in_advance",
            "text": "How many meals per week do you cook or prep in advance?",
            "type": "number",
            "range": {"min": 0, "max": 14},
        },
        {
            "id": "1.4.16",
            "variable_name": "cooking_skill_level",
            "text": "What is your cooking skill level?",
            "type": "single-select",
            "options": [
                {
                    "id": "1.4.16.1",
                    "text": "None (no cooking, relies on ready-made or takeout)",
                },
                {
                    "id": "1.4.16.2",
                    "text": "Basic (can do simple recipes, reheating, boiling, frying)",
                },
                {
                    "id": "1.4.16.3",
                    "text": "Intermediate (comfortable with various cooking methods and recipes)",
                },
                {
                    "id": "1.4.16.4",
                    "text": "Advanced (experienced with complex dishes and meal prep)",
                },
            ],
        },
        {
            "id": "1.4.17",
            "variable_name": "daily_meal_prep_time",
            "text": "Average time available for meal prep per day (minutes)",
            "type": "single-select",
            "options": [
                {"id": "1.4.17.1", "text": "0–15"},
                {"id": "1.4.17.2", "text": "16–30"},
                {"id": "1.4.17.3", "text": "31–60"},
                {"id": "1.4.17.4", "text": "60+"},
            ],
        },
        {
            "id": "1.4.18",
            "variable_name": "preferred_meal_prep_style",
            "text": "Preferred meal prep style",
            "type": "single-select",
            "options": [
                {"id": "1.4.18.1", "text": "Cook fresh each meal"},
                {"id": "1.4.18.2", "text": "Batch cook/prep meals in advance"},
                {"id": "1.4.18.3", "text": "Mix of fresh and batch prep"},
            ],
        },
        {
            "id": "1.4.19",
            "variable_name": "kitchen_equipment_access",
            "text": "Access to kitchen equipment (select all that apply)",
            "type": "multi-select",
            "options": [
                {"id": "1.4.19.1", "text": "Stove"},
                {"id": "1.4.19.2", "text": "Oven"},
                {"id": "1.4.19.3", "text": "Microwave"},
                {"id": "1.4.19.4", "text": "Blender"},
                {"id": "1.4.19.5", "text": "Slow cooker / Instant Pot"},
                {"id": "1.4.19.6", "text": "Other (please specify)"},
            ],
        },
    ],
}

sleep_questions = {
    "section": "1.6 Health, Recovery, Sleep",
    "questions": [
        {
            "id": "1.6.1",
            "variable_name": "health_goals",
            "text": "Which of these health goals apply to you?",
            "type": "multi-select",
            "options": [
                {"id": "1.6.1.1", "text": "Weight loss / fat reduction"},
                {"id": "1.6.1.2", "text": "Muscle gain / strength building"},
                {"id": "1.6.1.3", "text": "Improved energy / reduced fatigue"},
                {"id": "1.6.1.4", "text": "Better sleep quality"},
                {"id": "1.6.1.5", "text": "Stress management / anxiety reduction"},
                {"id": "1.6.1.6", "text": "Cardiovascular endurance"},
                {"id": "1.6.1.7", "text": "Flexibility / joint mobility"},
                {"id": "1.6.1.8", "text": "Healthy eating / nutrition"},
                {"id": "1.6.1.9", "text": "Digestive health / gut comfort"},
                {
                    "id": "1.6.1.10",
                    "text": "Long-term health maintenance / disease prevention",
                },
                {"id": "1.6.1.11", "text": "Other"},
            ],
        },
        {
            "id": "1.6.2",
            "variable_name": "usual_sleep_hours",
            "text": "How many hours of sleep do you usually get per night?",
            "type": "number",
            "range": {"min": 0, "max": 12},
        },
        {
            "id": "1.6.3",
            "variable_name": "trouble_sleeping",
            "text": "Do you have trouble falling or staying asleep?",
            "type": "single-select",
            "options": [
                {"id": "1.6.3.1", "text": "Yes"},
                {"id": "1.6.3.2", "text": "No"},
            ],
        },
        {
            "id": "1.6.4",
            "variable_name": "use_sleep_aids",
            "text": "Do you use melatonin or other sleep aids?",
            "type": "single-select",
            "options": [
                {"id": "1.6.4.1", "text": "Yes"},
                {"id": "1.6.4.2", "text": "No"},
            ],
        },
        {
            "id": "1.6.5",
            "variable_name": "earliest_wake_time",
            "text": "What is the earliest you are required to wake up?",
            "type": "time",
        },
        {
            "id": "1.6.6",
            "variable_name": "latest_bedtime",
            "text": "What is the latest you are required to go to sleep?",
            "type": "time",
        },
        {
            "id": "1.6.9",
            "variable_name": "feel_rested_on_waking",
            "text": "Do you feel rested when you wake up?",
            "type": "single-select",
            "options": [
                {"id": "1.6.9.1", "text": "Yes"},
                {"id": "1.6.9.2", "text": "No"},
            ],
        },
        {
            "id": "1.6.10",
            "variable_name": "use_screens_before_bed",
            "text": "Do you use screens within 30 minutes before bed?",
            "type": "single-select",
            "options": [
                {"id": "1.6.10.1", "text": "Yes"},
                {"id": "1.6.10.2", "text": "No"},
            ],
        },
    ],
}

motivation_mindset_questions = {
    "section": "1.11 Motivation & Mindset",
    "questions": [
        {
            "id": "1.11.1",
            "variable_name": "primary_motivation",
            "text": "What are your top motivations for improving your well-being?",
            "type": "multi-select",
            "max_selections": 2,
            "options": [
                {"id": "1.11.1.1", "text": "Have more energy"},
                {"id": "1.11.1.2", "text": "Look better physically"},
                {"id": "1.11.1.3", "text": "Improve sexual performance"},
                {"id": "1.11.1.4", "text": "Improve mental focus"},
                {"id": "1.11.1.5", "text": "Build consistency or discipline"},
                {"id": "1.11.1.6", "text": "Feel healthier overall"},
                {"id": "1.11.1.7", "text": "Reduce stress or anxiety"},
                {"id": "1.11.1.8", "text": "Other"},
            ],
        },
        {
            "id": "1.11.2",
            "variable_name": "commitment_level",
            "text": "How committed do you feel to this plan for the next 4 weeks?",
            "type": "single-select",
            "options": [
                {"id": "1.11.2.1", "text": "Just curious"},
                {"id": "1.11.2.2", "text": "I'll try, but not strict"},
                {"id": "1.11.2.3", "text": "I'll stick with it if it feels good"},
                {"id": "1.11.2.4", "text": "I'm serious"},
                {"id": "1.11.2.5", "text": "I'm all in—no excuses"},
            ],
        },
        {
            "id": "1.11.3",
            "variable_name": "routine_disruptors",
            "text": "Which of these are most likely to disrupt your routines?",
            "type": "multi-select",
            "options": [
                {"id": "1.11.3.1", "text": "Boredom"},
                {"id": "1.11.3.2", "text": "Travel or schedule changes"},
                {"id": "1.11.3.3", "text": "Work or school stress"},
                {"id": "1.11.3.4", "text": "Low motivation or energy"},
                {"id": "1.11.3.5", "text": "Other people’s schedules"},
                {"id": "1.11.3.6", "text": "Lack of flexibility"},
                {"id": "1.11.3.7", "text": "Forgetting or losing momentum"},
                {"id": "1.11.3.8", "text": "All-or-nothing thinking"},
                {"id": "1.11.3.9", "text": "Other"},
            ],
        },
        {
            "id": "1.11.4",
            "variable_name": "willing_to_give_up",
            "text": "Which things are you willing to reduce or give up for better results?",
            "type": "multi-select",
            "options": [
                {"id": "1.11.4.1", "text": "Screen time or social media"},
                {"id": "1.11.4.2", "text": "Alcohol"},
                {"id": "1.11.4.3", "text": "Tobacco or vaping"},
                {"id": "1.11.4.4", "text": "Marijuana or recreational drugs"},
                {"id": "1.11.4.5", "text": "Sex or solo play"},
                {"id": "1.11.4.6", "text": "Junk food or takeout"},
                {"id": "1.11.4.7", "text": "Sugar or sweets"},
                {"id": "1.11.4.8", "text": "Sleeping in"},
                {"id": "1.11.4.9", "text": "Passive downtime"},
                {"id": "1.11.4.10", "text": "Impulse spending"},
                {"id": "1.11.4.11", "text": "Evening entertainment (TV, games)"},
                {"id": "1.11.4.12", "text": "Hobbies or creative time"},
                {"id": "1.11.4.13", "text": "Spontaneity in schedule"},
                {"id": "1.11.4.14", "text": "Other"},
            ],
        },
        {
            "id": "1.11.5",
            "variable_name": "not_willing_to_give_up",
            "text": "Which things are you NOT willing to give up, even for faster progress?",
            "type": "multi-select",
            "options": [
                {"id": "1.11.5.1", "text": "Time with partner or family"},
                {"id": "1.11.5.2", "text": "Sex or solo play"},
                {"id": "1.11.5.3", "text": "Caffeine"},
                {"id": "1.11.5.4", "text": "Recreational substances (weed, etc.)"},
                {"id": "1.11.5.5", "text": "Alcohol"},
                {"id": "1.11.5.6", "text": "Smoking or vaping"},
                {"id": "1.11.5.7", "text": "Gaming or TV"},
                {"id": "1.11.5.8", "text": "Reading or quiet time"},
                {"id": "1.11.5.9", "text": "Hobbies or creative outlets"},
                {"id": "1.11.5.10", "text": "Comfort foods"},
                {"id": "1.11.5.11", "text": "Freedom to sleep in occasionally"},
                {"id": "1.11.5.12", "text": "Ability to skip workouts if tired"},
                {"id": "1.11.5.13", "text": "Flexibility or unstructured time"},
                {"id": "1.11.5.14", "text": "Other"},
            ],
        },
        {
            "id": "1.11.6",
            "variable_name": "early_signs_of_success",
            "text": "What will tell you this plan is starting to work?",
            "type": "multi-select",
            "options": [
                {"id": "1.11.6.1", "text": "Better sleep"},
                {"id": "1.11.6.2", "text": "Compliments from others"},
                {"id": "1.11.6.3", "text": "Improved focus or mood"},
                {"id": "1.11.6.4", "text": "Higher sex drive or performance"},
                {"id": "1.11.6.5", "text": "Stronger workouts"},
                {"id": "1.11.6.6", "text": "More self-control"},
                {"id": "1.11.6.7", "text": "Clothes fitting better"},
                {"id": "1.11.6.8", "text": "Other"},
            ],
        },
        {
            "id": "1.11.7",
            "variable_name": "desired_end_feelings",
            "text": "How do you want to feel at the end of this plan?",
            "type": "multi-select",
            "options": [
                {"id": "1.11.7.1", "text": "Proud"},
                {"id": "1.11.7.2", "text": "Energized"},
                {"id": "1.11.7.3", "text": "Confident"},
                {"id": "1.11.7.4", "text": "Stronger or fitter"},
                {"id": "1.11.7.5", "text": "More attractive"},
                {"id": "1.11.7.6", "text": "Focused"},
                {"id": "1.11.7.7", "text": "Balanced"},
                {"id": "1.11.7.8", "text": "Other"},
            ],
        },
        {
            "id": "1.11.8",
            "variable_name": "motivational_style",
            "text": "What type of motivation works best for you?",
            "type": "multi-select",
            "max_selections": 2,
            "options": [
                {"id": "1.11.8.1", "text": "Encouragement and praise"},
                {"id": "1.11.8.2", "text": "Competitive challenge"},
                {"id": "1.11.8.3", "text": "Clear structure and targets"},
                {"id": "1.11.8.4", "text": "Accountability from others"},
                {"id": "1.11.8.5", "text": "Internal motivation only"},
                {"id": "1.11.8.6", "text": "Other"},
            ],
        },
        {
            "id": "1.11.9",
            "variable_name": "accountability_preference",
            "text": "How do you feel about external accountability?",
            "type": "single-select",
            "options": [
                {"id": "1.11.9.1", "text": "I want reminders and check-ins"},
                {"id": "1.11.9.2", "text": "I prefer solo tracking"},
                {"id": "1.11.9.3", "text": "Light nudges only"},
                {"id": "1.11.9.4", "text": "I find accountability intrusive"},
                {"id": "1.11.9.5", "text": "Other"},
            ],
        },
    ],
}

plan_supporting_questions = {
    "section": "1.12 Plan Tailoring Extras",
    "questions": [
        {
            "id": "1.12.1",
            "variable_name": "stress_peak_time",
            "text": "What part of the day do you usually feel the most stress?",
            "type": "single-select",
            "options": [
                {"id": "1.12.1.1", "text": "Morning"},
                {"id": "1.12.1.2", "text": "Midday"},
                {"id": "1.12.1.3", "text": "Afternoon"},
                {"id": "1.12.1.4", "text": "Evening"},
                {"id": "1.12.1.5", "text": "Late night"},
                {"id": "1.12.1.6", "text": "No specific time"},
            ],
        },
        {
            "id": "1.12.2",
            "variable_name": "meal_prep_willingness",
            "text": "Would you be willing to spend more time prepping meals if it improved results?",
            "type": "single-select",
            "options": [
                {"id": "1.12.2.1", "text": "Yes"},
                {"id": "1.12.2.2", "text": "Maybe a little more"},
                {"id": "1.12.2.3", "text": "No"},
            ],
        },
        {
            "id": "1.12.3",
            "variable_name": "substance_quit_history",
            "text": "Have you tried quitting tobacco, alcohol, or other substances before?",
            "type": "single-select",
            "options": [
                {"id": "1.12.3.1", "text": "Yes, and it worked well"},
                {"id": "1.12.3.2", "text": "Yes, but it didn’t last"},
                {"id": "1.12.3.3", "text": "Yes, multiple times"},
                {"id": "1.12.3.4", "text": "No, this is my first real attempt"},
                {"id": "1.12.3.5", "text": "Not trying to quit anything"},
            ],
        },
        {
            "id": "1.12.4",
            "variable_name": "frequent_soreness",
            "text": "Do you often feel sore, tight, or stiff during the day?",
            "type": "single-select",
            "options": [
                {"id": "1.12.4.1", "text": "Yes, most days"},
                {"id": "1.12.4.2", "text": "Sometimes"},
                {"id": "1.12.4.3", "text": "Rarely or never"},
            ],
        },
        {
            "id": "1.12.5",
            "variable_name": "interest_in_recovery",
            "text": "Would you like to include light mobility or recovery sessions in your plan?",
            "type": "single-select",
            "options": [
                {"id": "1.12.5.1", "text": "Yes"},
                {"id": "1.12.5.2", "text": "Maybe"},
                {"id": "1.12.5.3", "text": "No"},
            ],
        },
    ],
}

all_questions = {
    "identity": identity_questions,
    "daily": daily_rhythm_questions,
    "substance": substances_questions,
    "meds": medications_questions,
    "fitness": fitness_questions,
    "sex": sexual_wellness_questions,
    "stress": stress_work_tech_questions,
    "interest": interests_lifestyle_questions,
    "diet": diet_questions,
    "sleep": sleep_questions,
    "motivation": motivation_mindset_questions,
    "support": plan_supporting_questions,
}


def time_str_to_slot(time_str: str) -> int:
    """Convert 'HH:MM' 24h string to 5-min slot integer (0–287)."""
    h, m = map(int, time_str.split(":"))
    return h * 12 + m // 5


def slot_to_time_str(slot: int) -> str:
    """Convert 5-min slot integer back to 'HH:MM' string."""
    h = slot // 12
    m = (slot % 12) * 5
    return f"{h:02d}:{m:02d}"


def calculate_target_bedtime_slot(
    earliest_wake_str: str, typical_sleep_hours: float
) -> int:
    wake_slot = time_str_to_slot(earliest_wake_str)
    sleep_slots = int(typical_sleep_hours * 12)
    bedtime_slot = wake_slot - sleep_slots
    if bedtime_slot < 0:
        bedtime_slot += 288  # wrap around midnight
    return bedtime_slot


def adjust_bedtime_for_sleep_issues(
    bedtime_slot: int,
    trouble_sleeping: bool,
    use_sleep_aids: bool,
    caffeine_intake_per_day: int,
    caffeine_last_intake_slot: int,
    tobacco_use: bool,
    alcohol_use: bool,
    cravings_evening: bool,
) -> int:
    """
    Adjust bedtime earlier if trouble sleeping and no aids.
    Also consider caffeine/alcohol/tobacco and evening cravings delaying sleep.
    """
    adjusted_slot = bedtime_slot

    # Shift earlier 15 minutes if trouble sleeping and no aids
    if trouble_sleeping and not use_sleep_aids:
        adjusted_slot -= 3  # 3 slots = 15 min

    # If caffeine consumed late (within 6 hours of bedtime), shift bedtime later by 15 minutes
    # if caffeine_intake_per_day > 0:
    #     diff = adjusted_slot - caffeine_last_intake_slot
    #     if 0 <= diff < 72:  # 6 hours = 72 slots
    #         adjusted_slot += 3  # delay bedtime 15 min

    # If evening cravings present, possibly delay bedtime 15 min
    if cravings_evening:
        adjusted_slot += 3

    # Tobacco and alcohol can disrupt sleep, but exact timing unknown
    # Could add similar logic if timing info available

    # Normalize to 0–287
    adjusted_slot %= 288
    return adjusted_slot


def validate_sleep_schedule(
    bedtime_slot: int, latest_bedtime_str: str
) -> Tuple[bool, int]:
    latest_slot = time_str_to_slot(latest_bedtime_str)
    if bedtime_slot > latest_slot:
        return False, latest_slot
    return True, bedtime_slot


def generate_sleep_routine_recommendations(
    trouble_sleeping: bool,
    use_sleep_aids: bool,
    caffeine_quantity: int,
    use_tobacco: bool,
    use_alcohol: bool,
) -> List[str]:
    tips = []
    if trouble_sleeping:
        tips.append("Establish a calming pre-sleep routine.")
        tips.append("Avoid screens 30 minutes before bedtime.")
        if not use_sleep_aids:
            tips.append(
                "Consider relaxation techniques like meditation or deep breathing."
            )
    else:
        tips.append("Maintain consistent sleep and wake times.")

    if caffeine_quantity > 0:
        tips.append("Limit caffeine intake, especially in the afternoon and evening.")
    if use_tobacco:
        tips.append("Avoid tobacco use close to bedtime.")
    if use_alcohol:
        tips.append("Limit alcohol consumption near bedtime for better sleep quality.")

    return tips


def summarize_sleep_plan(
    bedtime_slot: int,
    wake_time_str: str,
    duration_hours: float,
    recommendations: List[str],
) -> str:
    bedtime_str = slot_to_time_str(bedtime_slot)
    summary = (
        f"Sleep Plan:\n- Target bedtime: {bedtime_str}\n- Wake time: {wake_time_str}\n"
        f"- Target duration: {duration_hours} hours\n- Recommendations:\n"
    )
    for tip in recommendations:
        summary += f"  • {tip}\n"
    return summary


def calculate_bmr(weight_lbs, height_inches, age, gender):
    weight_kg = weight_lbs * 0.4536
    height_cm = height_inches * 2.54
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    elif gender.lower() == "female":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        raise ValueError("Gender must be 'male' or 'female'")
    return bmr


def calculate_bmi(weight_lbs, height_inches):
    weight_kg = weight_lbs * 0.4536
    height_m = height_inches * 0.0254
    bmi = weight_kg / (height_m**2)
    return bmi


def get_bmr_multiplier(category):
    mapping = {
        1: 1.2,  # Sedentary
        2: 1.375,  # Light activity
        3: 1.55,  # Moderate activity
        4: 1.725,  # High activity
        5: 1.9,  # Very high activity
    }
    try:
        category_int = int(category)
    except (ValueError, TypeError):
        return 1.2  # Default sedentary multiplier for invalid input
    return mapping.get(category_int, 1.2)


def get_activity_multiplier(daily_minutes, health_goals):
    """
    daily_minutes: int, minutes available for fitness per day
    fitness_goals: list of ints, e.g., [1, 2, 6] corresponding to:
        1 - Weight loss / fat reduction
        2 - Muscle gain / strength building
        3 - Improved energy / reduced fatigue
        4 - Better sleep quality
        5 - Stress management / anxiety reduction
        6 - Cardiovascular endurance
        7 - Flexibility / joint mobility
        8 - Healthy eating / nutrition
        9 - Digestive health / gut comfort
        10 - Long-term health maintenance / disease prevention
        11 - Other

    Returns: float, activity multiplier
    """
    moderate_goals = {1, 2, 6, 7}  # goals implying moderate activity
    light_goals = {3, 4, 5, 8, 9}  # goals implying light activity

    if daily_minutes >= 60 and any(goal in health_goals for goal in moderate_goals):
        return 1.55  # Moderate activity
    elif daily_minutes >= 30 and any(
        goal in health_goals for goal in moderate_goals.union(light_goals)
    ):
        return 1.375  # Light activity
    else:
        return 1.2  # Sedentary


def generate_meal_times(
    eating_window: Optional[
        tuple
    ],  # (start_hour, end_hour) in 24h format, e.g., (12, 20)
    meals_per_day: int,
    hours_between_meals: Optional[float] = None,
) -> List[str]:
    """
    Generate meal times as strings 'HH:MM', spaced within eating window or by hours_between_meals.
    If no window or spacing provided, defaults to 3 meals spaced evenly from 7 AM.
    """
    if meals_per_day <= 0:
        return []

    if eating_window:
        start, end = eating_window
        # Handle overnight window
        total_hours = (end - start) % 24 or 24
        interval = total_hours / max(meals_per_day - 1, 1)
        meal_hours = [(start + i * interval) % 24 for i in range(meals_per_day)]
    elif hours_between_meals:
        meal_hours = []
        current_hour = 7  # default start time
        for _ in range(meals_per_day):
            meal_hours.append(current_hour % 24)
            current_hour += hours_between_meals
    else:
        interval = 12 / max(meals_per_day - 1, 1)
        meal_hours = [7 + i * interval for i in range(meals_per_day)]

    # Format as HH:MM strings
    meal_times = [f"{int(h):02d}:{int((h - int(h)) * 60):02d}" for h in meal_hours]
    return meal_times


def validate_meals(meals_at_home: int, meals_out: int) -> int:
    total_meals = meals_at_home + meals_out
    if total_meals < 0 or total_meals > 10:
        raise ValueError("Total meals per day must be between 0 and 10")
    return total_meals


def parse_eating_window(
    use_window: bool, start: Optional[str], end: Optional[str]
) -> Optional[tuple]:
    if not use_window or not start or not end:
        return None

    # Convert HH:MM strings to decimal hours for easy calculation
    def time_to_decimal(t: str) -> float:
        h, m = map(int, t.split(":"))
        return h + m / 60

    return (time_to_decimal(start), time_to_decimal(end))


def generate_meal_schedule(
    total_meals: int, eating_window: Optional[tuple], spacing_hours: Optional[float]
) -> List[str]:
    if total_meals == 0:
        return []
    if eating_window:
        start, end = eating_window
        window_hours = (end - start) % 24 or 24
        interval = window_hours / max(total_meals - 1, 1)
        times = [(start + i * interval) % 24 for i in range(total_meals)]
    elif spacing_hours:
        # Start at 7 AM default if no window, space by spacing_hours
        times = [7 + i * spacing_hours for i in range(total_meals)]
    else:
        # Default 3 meals spaced over 12 hours
        interval = 12 / max(total_meals - 1, 1)
        times = [7 + i * interval for i in range(total_meals)]

    # Format to HH:MM strings
    def decimal_to_time(d: float) -> str:
        h = int(d) % 24
        m = int((d - int(d)) * 60)
        return f"{h:02d}:{m:02d}"

    return [decimal_to_time(t) for t in times]


def summarize_hydration(water_cups: int, other_fluids: List[str]) -> str:
    fluids = ["water"] if water_cups > 0 else []
    fluids += other_fluids
    return (
        f"Daily hydration includes {water_cups} cups of water and other fluids: {', '.join(other_fluids)}."
        if fluids
        else "No hydration data."
    )


def snack_summary(
    snacks_between_meals: bool, snacks_per_day: int, snack_types: Dict[str, bool]
) -> str:
    if not snacks_between_meals or snacks_per_day == 0:
        return "No snacks between meals."
    types = [k for k, v in snack_types.items() if v]
    return f"{snacks_per_day} snacks per day, types: {', '.join(types)}."


def apply_dietary_restrictions(avoid_list: List[str]) -> str:
    if not avoid_list or "None" in avoid_list:
        return "No dietary restrictions."
    return f"Avoid or limit these foods: {', '.join(avoid_list)}."


def build_meal_plan(
    meals_at_home: int,
    meals_out: int,
    use_eating_window: bool,
    eating_window_start: Optional[str],
    eating_window_end: Optional[str],
    hours_between_meals: Optional[float],
    water_intake_cups: int,
    other_fluids: List[str],
    snacks_between_meals: bool,
    snacks_per_day: int,
    snack_types: Dict[str, bool],
    foods_to_avoid: List[str],
    cooking_skill_level: str,
    daily_meal_prep_time: str,
    preferred_meal_prep_style: str,
    kitchen_equipment_access: List[str],
    current_weight_lbs: float,
    height_inches: float,
    age: int,
    gender: str,
    daily_fitness_minutes: int,
    health_goals: List[int],
) -> Dict:

    # Original calculations
    total_meals = validate_meals(meals_at_home, meals_out)
    window = parse_eating_window(
        use_eating_window, eating_window_start, eating_window_end
    )
    meal_times = generate_meal_schedule(total_meals, window, hours_between_meals)
    hydration = summarize_hydration(water_intake_cups, other_fluids)
    snacks = snack_summary(snacks_between_meals, snacks_per_day, snack_types)
    restrictions = apply_dietary_restrictions(foods_to_avoid)

    # Map daily_meal_prep_time string to minutes
    prep_time_map = {"0-15": 15, "16-30": 30, "31-60": 60, "60+": 90}
    prep_time_per_meal = prep_time_map.get(daily_meal_prep_time, 30)

    # Cooking skill value
    skill_levels = {"None": 0, "Basic": 1, "Intermediate": 2, "Advanced": 3}
    skill_level_value = skill_levels.get(cooking_skill_level, 1)

    # Batch cook flag
    batch_cook = preferred_meal_prep_style.lower().startswith("batch")

    # BMI, BMR, TDEE
    bmi_value = calculate_bmi(current_weight_lbs, height_inches)
    bmr_value = calculate_bmr(current_weight_lbs, height_inches, age, gender)
    activity_multiplier = get_activity_multiplier(daily_fitness_minutes, health_goals)
    tdee_value = bmr_value * activity_multiplier

    # ---- NEW DAILY/WEEKLY TARGET METRICS ----
    deficit = 450
    week4_cal = max(tdee_value - deficit, 1200)
    daily_calories_targets_by_week = [
        round(tdee_value - (i * ((tdee_value - week4_cal) / 3)), 0) for i in range(4)
    ]

    protein_grams_per_day = round(current_weight_lbs * 0.8)
    protein_per_meal_grams_by_week = [
        round(protein_grams_per_day / total_meals, 1) if total_meals else 0
        for _ in range(4)
    ]

    snacks_per_day_by_week = (
        [snacks_per_day] * 4 if snacks_between_meals else [0, 0, 0, 0]
    )
    snack_calories_by_week = [
        (
            round(
                (daily_calories_targets_by_week[w] * 0.15)
                / max(snacks_per_day_by_week[w], 1),
                0,
            )
            if snacks_per_day_by_week[w] > 0
            else 0
        )
        for w in range(4)
    ]

    per_meal_calories_by_week = [
        round(
            (
                daily_calories_targets_by_week[w]
                - (snack_calories_by_week[w] * snacks_per_day_by_week[w])
            )
            / max(total_meals, 1),
            0,
        )
        for w in range(4)
    ]

    water_cups_per_day_by_week = [
        max(water_intake_cups, 9) if w > 0 else water_intake_cups for w in range(4)
    ]

    # Final dict
    meal_plan_meta = {
        "total_meals_per_day": total_meals,
        "meal_times": meal_times,
        "hydration_summary": hydration,
        "snack_summary": snacks,
        "dietary_restrictions": restrictions,
        "prep_time_per_meal": prep_time_per_meal,
        "cooking_skill_level": cooking_skill_level,
        "skill_level_value": skill_level_value,
        "batch_cook": batch_cook,
        "kitchen_equipment_access": kitchen_equipment_access,
        "bmi": bmi_value,
        "bmr": bmr_value,
        "activity_multiplier": activity_multiplier,
        "tdee": tdee_value,
        # new targets
        "daily_calories_targets_by_week": daily_calories_targets_by_week,
        "protein_grams_per_day": protein_grams_per_day,
        "protein_per_meal_grams_by_week": protein_per_meal_grams_by_week,
        "snacks_per_day_by_week": snacks_per_day_by_week,
        "snack_calories_by_week": snack_calories_by_week,
        "per_meal_calories_by_week": per_meal_calories_by_week,
        "water_cups_per_day_by_week": water_cups_per_day_by_week,
    }

    return meal_plan_meta


def build_sleep_plan(
    earliest_wake_time,
    usual_sleep_hours,
    trouble_sleeping,
    use_sleep_aids,
    caffeine_quantity,
    use_tobacco,
    use_alcohol,
    tobacco_cravings_time,
    alcohol_cravings_time,
    latest_bedtime,
) -> Dict:
    # helpers local to this function
    slot_length_minutes = 5

    def slot_to_time_str(slot: int) -> str:
        mins = (slot * slot_length_minutes) % (24 * 60)
        h = mins // 60
        m = mins % 60
        return f"{h:02d}:{m:02d}"

    def minutes_to_slots(mins: int) -> int:
        return int(round(mins / slot_length_minutes))

    # Convert earliest wake time to slot
    wake_slot = time_str_to_slot(earliest_wake_time)

    # Calculate target bedtime slot
    bedtime_slot = calculate_target_bedtime_slot(earliest_wake_time, usual_sleep_hours)

    # Adjust bedtime based on sleep issues
    adjusted_bedtime_slot = adjust_bedtime_for_sleep_issues(
        bedtime_slot,
        trouble_sleeping == "Yes",
        use_sleep_aids == "Yes",
        caffeine_quantity,
        time_str_to_slot(
            "08:00"
        ),  # placeholder last-caffeine time; downstream can replace
        use_tobacco,
        use_alcohol,
        ("evenings" in (tobacco_cravings_time or ""))
        or ("evenings" in (alcohol_cravings_time or "")),
    )

    # Validate bedtime against latest allowed bedtime
    is_valid, valid_bedtime_slot = validate_sleep_schedule(
        adjusted_bedtime_slot, latest_bedtime
    )

    # Generate sleep routine recommendations
    recommendations = generate_sleep_routine_recommendations(
        trouble_sleeping, use_sleep_aids, caffeine_quantity, use_tobacco, use_alcohol
    )

    # NEW: week-by-week lights-out times (gentle earlier shift 0, -15, -30, -60 minutes)
    shift_minutes = [0, -15, -30, -60]
    lights_out_slots = [
        max(0, valid_bedtime_slot + minutes_to_slots(s)) for s in shift_minutes
    ]
    lights_out_time_by_week = [slot_to_time_str(s) for s in lights_out_slots]

    # NEW: screen-free progression (if user already does some, downstream can override)
    screen_free_minutes_by_week = [20, 30, 45, 60]

    # NEW: caffeine cutoff tied to Week 4 lights-out (8 hours before)
    cutoff_slot = max(0, lights_out_slots[-1] - minutes_to_slots(8 * 60))
    caffeine_cutoff_time = slot_to_time_str(cutoff_slot)

    return {
        "wake_slot": wake_slot,
        "wake_time": slot_to_time_str(wake_slot),
        "target_bedtime_slot": bedtime_slot,
        "adjusted_bedtime_slot": adjusted_bedtime_slot,
        "bedtime_valid": is_valid,
        "valid_bedtime_slot": valid_bedtime_slot,
        "recommendations": recommendations,
        # added fields for daily planning
        "screen_free_minutes_by_week": screen_free_minutes_by_week,
        "lights_out_time_by_week": lights_out_time_by_week,
        "caffeine_cutoff_time": caffeine_cutoff_time,
    }


def build_beginner_workout_plan(
    daily_fitness_minutes: int,
    preferred_workout_time: str = None,
    current_activity_level: str = None,
    fitness_goals: list = None,
    exercise_types_enjoyed: list = None,
    injuries_or_limitations: bool = False,
    frequent_soreness: bool = False,
    routine_disruptors: list = None,
    primary_motivation: list = None,
    commitment_level: str = None,
    interest_in_recovery: bool = False,
    responsibility_start_time: str = "09:00",
    responsibility_end_time: str = "17:00",
    pet_care_morning: bool = False,
    pet_care_morning_start_time: str = "07:00",
    pet_care_morning_end_time: str = "07:30",
    pet_care_evening: bool = True,
    pet_care_evening_start_time: str = "18:30",
    pet_care_evening_end_time: str = "19:00",
) -> dict:
    def lower_list(x):
        return [str(v).lower() for v in x] if isinstance(x, list) else []

    goals = set(lower_list(fitness_goals))
    disrupt = set(lower_list(routine_disruptors))
    motives = set(lower_list(primary_motivation))
    commitment = (commitment_level or "").lower()
    cal_level = (current_activity_level or "light activity").lower()
    minutes = int(daily_fitness_minutes or 20)

    # Default weekly session counts [W1, W2, W3, W4]
    wk_strength = [2, 2, 2, 3]
    wk_endur = [1, 1, 2, 2]
    wk_mob = [1, 2, 2, 2]
    wk_reco = [0, 0, 0, 0]
    wk_rest = [3, 2, 2, 2]

    # Session durations by available time
    if minutes <= 25:
        dur_strength = [20, 25, 25, 25]
        dur_endur = [20, 25, 25, 25]
        dur_mob = [15, 20, 20, 20]
        dur_reco = [15, 15, 15, 15]
    elif minutes <= 45:
        dur_strength = [20, 25, 30, 30]
        dur_endur = [20, 25, 30, 30]
        dur_mob = [15, 20, 20, 20]
        dur_reco = [15, 15, 15, 15]
    else:
        dur_strength = [25, 30, 35, 35]
        dur_endur = [25, 30, 35, 35]
        dur_mob = [20, 20, 25, 25]
        dur_reco = [15, 15, 20, 20]

    # Base intensity (RPE)
    rpe_strength = "4-5"
    rpe_endur = "4-5"
    rpe_mob = "3"
    rpe_reco = "2-3"

    # Goal adjustments
    if ("increase strength" in goals) and ("improve endurance" not in goals):
        wk_strength[3] = min(wk_strength[3] + 1, 4)
    if ("improve endurance" in goals) and ("increase strength" not in goals):
        wk_endur[2] = min(wk_endur[2] + 1, 3)
        wk_endur[3] = min(wk_endur[3] + 1, 3)

    if ("reduce stress" in motives) or ("reduce stress / anxiety" in motives):
        wk_mob[0] = max(wk_mob[0], 1)
        wk_mob[1] = max(wk_mob[1], 2)
    if "more energy" in motives:
        rpe_strength = "4-5"
        rpe_endur = "4-5"

    if injuries_or_limitations:
        wk_mob = [max(x, 1) for x in wk_mob]

    if frequent_soreness:
        for i in range(3):
            if wk_strength[i] > wk_endur[i] and wk_strength[i] > 1:
                wk_strength[i] -= 1
                wk_mob[i] += 1
            elif wk_endur[i] > 0:
                wk_endur[i] -= 1
                wk_mob[i] += 1
            wk_rest[i] = max(wk_rest[i], 2)

    if interest_in_recovery:
        wk_reco[2] = max(wk_reco[2], 1)
        wk_reco[3] = max(wk_reco[3], 1)

    if "just curious" in commitment:
        for i in range(2):
            active = wk_strength[i] + wk_endur[i] + wk_mob[i] + wk_reco[i]
            while active > 3:
                if wk_endur[i] > 0:
                    wk_endur[i] -= 1
                elif wk_strength[i] > 1:
                    wk_strength[i] -= 1
                elif wk_mob[i] > 0:
                    wk_mob[i] -= 1
                active = wk_strength[i] + wk_endur[i] + wk_mob[i] + wk_reco[i]
            wk_rest[i] = max(7 - active, wk_rest[i], 3)
    elif (
        ("i'll try" in commitment)
        or ("i'll try," in commitment)
        or ("i’ll try" in commitment)
    ):
        for i in range(3):
            if wk_endur[i] > 0:
                wk_endur[i] -= 1
            elif wk_strength[i] > 1:
                wk_strength[i] -= 1
            else:
                wk_mob[i] = max(wk_mob[i] - 1, 0)
            wk_rest[i] = max(wk_rest[i], 2)
    elif "all in" in commitment:
        wk_strength[3] += 1
        wk_rest[3] = max(2, 7 - (wk_strength[3] + wk_endur[3] + wk_mob[3] + wk_reco[3]))

    if (
        ("low energy or motivation" in disrupt)
        or ("low energy" in disrupt)
        or ("motivation" in disrupt)
    ):
        rpe_mob = "2-3"
        rpe_reco = "2"
        dur_mob = [15 if d <= 20 else d - 5 for d in dur_mob]
        dur_reco = [max(10, d) for d in dur_reco]
    if "all-or-nothing thinking" in disrupt:
        wk_reco = [max(r, 1) for r in wk_reco]

    def clamp_week(i):
        active = wk_strength[i] + wk_endur[i] + wk_mob[i] + wk_reco[i]
        if active > 5 and i < 2:
            overflow = active - 5
            while overflow > 0 and (wk_reco[i] > 0 or wk_mob[i] > 1 or wk_endur[i] > 0):
                if wk_reco[i] > 0:
                    wk_reco[i] -= 1
                elif wk_mob[i] > 1:
                    wk_mob[i] -= 1
                elif wk_endur[i] > 0:
                    wk_endur[i] -= 1
                overflow -= 1
        wk_rest[i] = max(2, 7 - (wk_strength[i] + wk_endur[i] + wk_mob[i] + wk_reco[i]))

    for i in range(4):
        clamp_week(i)

    if "sedentary" in cal_level:
        rpe_strength = "4-5"
        rpe_endur = "4-5"
        rpe_mob = "3"
    elif "light" in cal_level:
        rpe_strength = "4-5"
        rpe_endur = "4-5"
        rpe_mob = "3-4"
    elif "moderate" in cal_level:
        rpe_strength = "5-6"
        rpe_endur = "5-6"
        rpe_mob = "3-4"
    else:
        rpe_strength = "5-6"
        rpe_endur = "5-6"
        rpe_mob = "3-4"

    def build_week1_template():
        slots = []
        s, e, m, r = wk_strength[0], wk_endur[0], wk_mob[0], wk_reco[0]
        while len(slots) < 7:
            if s > 0:
                slots.append("strength_type")
                s -= 1
            if len(slots) >= 7:
                break
            if m > 0:
                slots.append("mobility_type")
                m -= 1
            elif r > 0:
                slots.append("recovery_type")
                r -= 1
            if len(slots) >= 7:
                break
            if e > 0:
                slots.append("endurance_type")
                e -= 1
            if len(slots) >= 7:
                break
            if (s + e + m + r) == 0:
                slots.append("rest")
            if len(slots) >= 7:
                break
            if "rest" not in slots and len(slots) < 6:
                slots.append("rest")
        while len(slots) < 7:
            slots.append("rest")
        return slots[:7]

    placement_rules = build_week1_template()

    avoid_times = []
    if pet_care_morning:
        avoid_times.append(f"{pet_care_morning_start_time}-{pet_care_morning_end_time}")
    if pet_care_evening:
        avoid_times.append(f"{pet_care_evening_start_time}-{pet_care_evening_end_time}")
    avoid_times.append(f"{responsibility_start_time}-{responsibility_end_time}")

    time_window = preferred_workout_time or "evening"

    kcal_per_min = {
        "strength_type": 5,
        "endurance_type": 6,
        "mobility_type": 3,
        "recovery_type": 2,
    }

    def weekly_minutes(i):
        return (
            wk_strength[i] * dur_strength[i]
            + wk_endur[i] * dur_endur[i]
            + wk_mob[i] * dur_mob[i]
            + wk_reco[i] * dur_reco[i]
        )

    def weekly_kcal(i):
        return int(
            round(
                wk_strength[i] * dur_strength[i] * kcal_per_min["strength_type"]
                + wk_endur[i] * dur_endur[i] * kcal_per_min["endurance_type"]
                + wk_mob[i] * dur_mob[i] * kcal_per_min["mobility_type"]
                + wk_reco[i] * dur_reco[i] * kcal_per_min["recovery_type"]
            )
        )

    calories_burned_weekly_targets = [weekly_kcal(i) for i in range(4)]
    active_days_by_week = [7 - wk_rest[i] for i in range(4)]
    total_minutes_by_week = [weekly_minutes(i) for i in range(4)]

    calories_burned_daily_target_by_week = [
        int(round(calories_burned_weekly_targets[i] / max(1, active_days_by_week[i])))
        for i in range(4)
    ]
    daily_minutes_target_by_week = [
        int(round(total_minutes_by_week[i] / max(1, active_days_by_week[i])))
        for i in range(4)
    ]

    return {
        "week_structure": {
            "strength_type_sessions": wk_strength,
            "endurance_type_sessions": wk_endur,
            "mobility_type_sessions": wk_mob,
            "recovery_type_sessions": wk_reco,
            "rest_days": wk_rest,
        },
        "session_targets": {
            "strength_type": {
                "duration_min": dur_strength,
                "intensity_rpe": rpe_strength,
            },
            "endurance_type": {"duration_min": dur_endur, "intensity_rpe": rpe_endur},
            "mobility_type": {"duration_min": dur_mob, "intensity_rpe": rpe_mob},
            "recovery_type": {"duration_min": dur_reco, "intensity_rpe": rpe_reco},
        },
        "placement_rules": {
            "week1_labels": placement_rules,
            "spacing_notes": [
                "No back-to-back strength days in Weeks 1-2",
                "Follow hardest day with mobility or rest",
                "Avoid endurance intervals the day before lower-body strength",
            ],
        },
        "constraints": {
            "primary_session_time_window": time_window,
            "avoid_times": avoid_times,
        },
        "energy_targets": {
            "per_session_kcal_estimates": kcal_per_min,
            "calories_burned_weekly_targets": calories_burned_weekly_targets,
            "calories_burned_daily_target_by_week": calories_burned_daily_target_by_week,
            "active_days_by_week": active_days_by_week,
            "daily_minutes_target_by_week": daily_minutes_target_by_week,
        },
    }


def build_substance_plan(
    use_alcohol: str,
    alcohol_quantity: int,
    alcohol_frequency: str,
    alcohol_goal: str,
    alcohol_cravings_time: str,
    use_tobacco: str,
    tobacco_quantity: int,
    tobacco_frequency: str,
    tobacco_goal: str,
    tobacco_cravings_time: str,
    use_marijuana: str,
    marijuana_quantity: int,
    marijuana_frequency: str,
    marijuana_goal: str,
    marijuana_cravings_time: str,
    use_caffeine: str,
    caffeine_quantity: int,
    caffeine_frequency: str,
    caffeine_goal: str,
    caffeine_cravings_time: str,
    stress_peak_time: str = None,
    accountability_preference: str = None,
    commitment_level: str = None,
    meal_times: list = None,
    preferred_workout_time: str = None,
    coping_mechanisms_when_stressed: list = None,
    replacement_activities: list = None,
) -> dict:
    def yes(v):
        return str(v).strip().lower() in ("yes", "y", "true", "1")

    def pos_int(x, default=0):
        try:
            xi = int(x)
            return xi if xi >= 0 else default
        except Exception:
            return default

    def norm_goal(txt):
        t = (str(txt) or "").strip().lower()
        if "quit" in t:
            return "quit"
        if "reduce" in t:
            return "reduce"
        if "no change" in t or "maintain" in t:
            return "maintain"
        return "reduce"

    def per_week(qty, freq_txt):
        q = pos_int(qty, 0)
        f = (str(freq_txt) or "").strip().lower()
        if f == "per day":
            return q * 7
        if f == "per week":
            return q
        return q

    def cravings_to_ranges(txt):
        t = (str(txt) or "").strip().lower()
        if t in ("evening", "evenings"):
            return ["18:00-22:00"]
        if t in ("late night", "late nights"):
            return ["22:00-02:00"]
        if t in ("afternoon", "afternoons"):
            return ["14:00-17:00"]
        if t in ("morning", "mornings"):
            return ["06:00-10:00"]
        if t in ("weekend", "weekends"):
            return ["Fri 18:00-23:59", "Sat 12:00-23:59"]
        return []

    def dedupe(seq):
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out

    substances_map = {
        "alcohol": (
            use_alcohol,
            alcohol_quantity,
            alcohol_frequency,
            alcohol_goal,
            alcohol_cravings_time,
        ),
        "tobacco": (
            use_tobacco,
            tobacco_quantity,
            tobacco_frequency,
            tobacco_goal,
            tobacco_cravings_time,
        ),
        "marijuana": (
            use_marijuana,
            marijuana_quantity,
            marijuana_frequency,
            marijuana_goal,
            marijuana_cravings_time,
        ),
        "caffeine": (
            use_caffeine,
            caffeine_quantity,
            caffeine_frequency,
            caffeine_goal,
            caffeine_cravings_time,
        ),
    }

    def reduce_curve_wk(b):
        return [max(0, round(b * r)) for r in (0.8, 0.6, 0.4, 0.25)]

    def quit_curve_wk(b):
        return [max(0, round(b * r)) for r in (0.75, 0.5, 0.25, 0.0)]

    def keep_curve_wk(b):
        return [max(0, round(b))] * 4

    def reduce_curve_amt(a):
        return [round(a * r, 2) for r in (0.85, 0.70, 0.50, 0.40)]

    def quit_curve_amt(a):
        return [round(a * r, 2) for r in (0.75, 0.50, 0.25, 0.00)]

    def keep_curve_amt(a):
        return [round(a, 2)] * 4

    substances_targeted = []
    targets_by_substance = {}
    amount_targets = {}
    high_risk_times = []

    for name, (flag, qty, freq, goal, cravings) in substances_map.items():
        if not yes(flag):
            continue
        substances_targeted.append(name)

        baseline_wk = per_week(qty, freq)
        g = norm_goal(goal)

        if g == "quit":
            weekly_uses = quit_curve_wk(baseline_wk)
        elif g == "maintain":
            weekly_uses = keep_curve_wk(baseline_wk)
        else:
            weekly_uses = reduce_curve_wk(baseline_wk)

        targets_by_substance[name] = {"weekly_uses_target": weekly_uses}

        base_amt = float(pos_int(qty, 0))
        if base_amt > 0:
            if g == "quit":
                amount_targets[name] = {
                    "per_use_amount_target": quit_curve_amt(base_amt)
                }
            elif g == "maintain":
                amount_targets[name] = {
                    "per_use_amount_target": keep_curve_amt(base_amt)
                }
            else:
                amount_targets[name] = {
                    "per_use_amount_target": reduce_curve_amt(base_amt)
                }

        high_risk_times.extend(cravings_to_ranges(cravings))

    if stress_peak_time:
        high_risk_times.extend(cravings_to_ranges(stress_peak_time))

    high_risk_times = dedupe(high_risk_times)

    no_use_windows = ["Within 3h of bedtime"]
    if meal_times and isinstance(meal_times, list) and len(meal_times) > 0:
        no_use_windows.append("Empty stomach discouraged; pair with meals only")
    no_use_windows = dedupe(no_use_windows)

    default_replacements = [
        "walk 10 min",
        "hydrate 16 oz water",
        "decaf or herbal tea",
        "deep breathing 4-7-8",
        "call or text someone",
        "fruit or protein snack",
        "gum or toothbrushing",
    ]
    substitution_rules = {
        "stress": default_replacements[:4],
        "boredom": ["hobby 10–15 min", "music playlist", "short game or puzzle"]
        + default_replacements[:2],
        "social events": [
            "alcohol-free drink",
            "arrive later or leave earlier",
            "designated driver commitment",
            "pre-set drink cap",
        ]
        + default_replacements[:1],
        "evenings": ["post-dinner walk", "shower or teeth early", "prep for tomorrow"]
        + default_replacements[:2],
        "cravings": [
            "timer 10 min then reassess",
            "breathing 4-7-8",
            "protein snack",
            "tea",
            "walk",
        ],
    }

    acct = (accountability_preference or "").strip().lower()
    commit = (commitment_level or "").strip().lower()
    if acct in ("i want reminders and check-ins", "reminders", "check-ins"):
        reminder_style, checkins = "reminders", 3
    elif acct in ("light nudges only", "light nudges"):
        reminder_style, checkins = "light_nudges", 1
    elif acct in ("i prefer solo tracking", "solo"):
        reminder_style, checkins = "solo", 0
    else:
        if "all in" in commit or "serious" in commit:
            reminder_style, checkins = "reminders", 2
        else:
            reminder_style, checkins = "light_nudges", 1

    support_actions = {
        "reminder_style": reminder_style,
        "checkins_per_week": checkins,
        "suggested_supports": ["self-tracking with weekly reflection"],
    }

    contingency_plan = [
        "Plan responses to common offers: I’m taking a break this month.",
        "Keep substitutes visible: tea, seltzer, gum, snacks.",
        "If lapse occurs, reset target the same day; review trigger and adjust.",
        "Avoid stocking at home; buy single-servings only if needed.",
        "Pair urges with a 10-minute delay and a replacement activity.",
    ]

    notes = []
    if preferred_workout_time:
        notes.append(
            f"pair cravings windows with light activity near {preferred_workout_time}"
        )

    return {
        "substances_targeted": substances_targeted,
        "targets_by_substance": targets_by_substance,
        "amount_targets": amount_targets,
        "schedule_guidelines": {
            "high_risk_times": high_risk_times,
            "no_use_windows": no_use_windows,
        },
        "substitution_rules": substitution_rules,
        "support_actions": support_actions,
        "contingency_plan": contingency_plan,
        "notes": notes,
    }


sleep_plan = callwdata(build_sleep_plan, user_data)
meal_plan = callwdata(build_meal_plan, user_data)
workout_plan = callwdata(build_beginner_workout_plan, user_data)
substance_plan = callwdata(build_substance_plan, user_data)


sleep_prompt = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a planner generator. Expand structured sleep data into a consistent, "
                "machine-parseable 28-day schedule. Always return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Here is the sleep plan data (JSON):\n\n{sleep_plan_json}\n\n"
                "Rules:\n"
                "- Generate exactly 28 days: Days 1–7 use week 1 values, 8–14 week 2, 15–21 week 3, 22–28 week 4.\n"
                "- Wake time must be computed from wake_slot using 5-minute slots (HH:MM, zero-padded). Do not invent a different time.\n"
                "- Bedtime must come from lights_out_time_by_week. If missing, use valid_bedtime_slot or target_bedtime_slot (convert slots to HH:MM).\n"
                "- Include caffeine_cutoff_time exactly if present.\n"
                "- If screen_free_minutes_by_week exists, build a pre-sleep routine of EXACTLY 3 distinct steps per day whose durations sum to at least that week’s minutes.\n"
                "- Choose steps ONLY from this allowed list to avoid generic filler: "
                '["slow lighting transition", "warm shower", "light stretch", "book reading", "journaling", '
                '"4-7-8 breathing", "box breathing", "guided relaxation", "herbal tea", '
                '"prep clothes/bag", "quick tidy-up", "meditation", "aromatherapy", "gratitude list", '
                '"soothing music listening", "skin care routine", "warm foot soak", "gentle yoga", '
                '"body scan meditation", "positive visualization", "progressive muscle relaxation", '
                '"comfort drink", "creative wind-down", "organize tomorrow\'s to-do list", '
                '"silent reflection / prayer", "mantra chanting", "light origami or puzzle", '
                '"self-massage (hands/neck/shoulders)", "stretch with foam roller", "coloring book session", '
                '"slow breathing with music", "story podcast or audiobook", "candle gazing", "tai chi flow", '
                '"declutter one small space", "handwriting practice", "visual gratitude (photos or vision board)", '
                '"mindful snacking", "hydration with intention", "affirmations out loud", '
                '"mindful walking indoors", "breathing with hand on chest", "guided imagery meditation", '
                '"pet bonding (gentle play or grooming)", "stretching in bed", "foot massage", '
                '"leg elevation rest", "simple journaling prompts", "face massage / acupressure", '
                '"write a short note or letter"] and include a duration (e.g., "book reading - 15 min").\n'
                "- Do not repeat the same step more than once within the same week.\n"
                "- Convert any ‘recommendations’ into 1–3 short reminders without contradicting provided data.\n"
                "- Time format must be 24-hour HH:MM. Output JSON only, no extra keys, no prose.\n"
                "Output format (strict):\n"
                "{\n"
                '  "days": [\n'
                "    {\n"
                '      "day": number,\n'
                '      "wake_time": string,\n'
                '      "bedtime": string,\n'
                '      "pre_sleep_routine": [string, string, string],\n'
                '      "reminders": [string]\n'
                "    }\n"
                "  ]\n"
                "}"
            ),
        },
    ],
}


diet_prompt = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a planner generator. Expand structured diet data into a consistent, "
                "machine-parseable 28-day meal schedule. Always return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Here is the diet plan data (JSON):\n\n{diet_plan_json}\n\n"
                "Rules:\n"
                "- Use week-based targets to set each day’s totals (days 1–7 = week 1, etc.).\n"
                "- Map daily_calories_targets_by_week to per-day targets; align per_meal_calories_by_week with meal_times.\n"
                "- Use protein_grams_per_day and protein_per_meal_grams_by_week to guide components.\n"
                "- Use snacks_per_day_by_week and snack_calories_by_week for daily snack count/options.\n"
                "- Respect dietary_restrictions, cooking_skill_level, prep_time_per_meal, kitchen_equipment_access.\n"
                "- Hydration from hydration_summary and water_cups_per_day_by_week if present.\n"
                "Output format (strict):\n"
                "{{\n"
                '  "days": [\n'
                "    {{\n"
                '      "day": number,                     # 1..28\n'
                '      "calorie_target": number,          # per day\n'
                '      "protein_target_g": number,\n'
                '      "meals": [                         # one item per meal_times entry\n'
                '        {{"time": string, "title": string, "components": [string], "approx_kcal": number, "approx_protein_g": number}}\n'
                "      ],\n"
                '      "snacks": [                        # 0..N snacks based on week target\n'
                '        {{"title": string, "approx_kcal": number}}\n'
                "      ],\n"
                '      "hydration": [string],             # short reminders derived from hydration_summary\n'
                '      "notes": [string]                  # short tips honoring restrictions/skill/prep limits\n'
                "    }}\n"
                "  ]\n"
                "}}"
            ),
        },
    ],
}

activity_prompt = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a planner generator. Expand structured activity data into a consistent, "
                "machine-parseable 28-day schedule. Always return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Here is the activity plan data (JSON):\n\n{activity_plan_json}\n\n"
                "Rules:\n"
                "- Use week_structure and session_targets to assign session type and duration per day.\n"
                "- If placement_rules.week1_labels exists, use its pattern for week 1; propagate logically to later weeks respecting week_structure counts.\n"
                "- Use energy_targets.daily_minutes_target_by_week for minimum daily minutes; intensity from session_targets.*.intensity_rpe.\n"
                "- Respect constraints.primary_session_time_window and avoid_times.\n"
                "Output format (strict):\n"
                "{{\n"
                '  "days": [\n'
                "    {{\n"
                '      "day": number,                        # 1..28\n'
                '      "session_type": string,               # strength_type | endurance_type | mobility_type | recovery_type | rest\n'
                '      "start_window": string,               # morning | afternoon | evening (from constraints)\n'
                '      "duration_minutes": number,           # from session_targets and week\n'
                '      "intensity": string,                  # RPE or similar from session_targets\n'
                '      "notes": [string]                     # short cues; avoid_times reminders if relevant\n'
                "    }}\n"
                "  ]\n"
                "}}"
            ),
        },
    ],
}

substance_prompt = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a planner generator. Expand structured substance plan data into a consistent, "
                "machine-parseable 28-day adherence plan. Always return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Here is the substance plan data (JSON):\n\n{substance_plan_json}\n\n"
                "Rules:\n"
                "- For each week, derive per-day limits from targets_by_substance.weekly_uses_target (distribute evenly across 7 days unless no_use_windows or high_risk_times suggest clustering).\n"
                "- Use amount_targets.per_use_amount_target as per-use limit where present.\n"
                "- Honor schedule_guidelines.no_use_windows (e.g., within 3h of bedtime) and latest_caffeine_time if provided.\n"
                "- Provide clear substitution options from substitution_rules; include support_actions and contingency_plan where useful as reminders.\n"
                "Output format (strict):\n"
                "{{\n"
                '  "days": [\n'
                "    {{\n"
                '      "day": number,                      # 1..28\n'
                '      "substances": [\n'
                "        {{\n"
                '          "name": string,\n'
                '          "allowed_uses": number,          # day-level cap derived from week\n'
                '          "per_use_limit": number|null,    # if amount_targets exist\n'
                '          "high_risk_times": [string],\n'
                '          "no_use_windows": [string],\n'
                '          "substitutions": [string]\n'
                "        }}\n"
                "      ],\n"
                '      "reminders": [string]                # support_actions + contingency points as brief cues\n'
                "    }}\n"
                "  ]\n"
                "}}"
            ),
        },
    ],
}


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_sleep_schedule(sleep_plan: dict):
    # Inject sleep_plan JSON into the existing prompt template
    prompt = copy.deepcopy(sleep_prompt)
    prompt["messages"][1]["content"] = prompt["messages"][1]["content"].replace(
        "{sleep_plan_json}", json.dumps(sleep_plan, ensure_ascii=False)
    )

    try:
        response = client.chat.completions.create(
            model=prompt["model"],  # use whatever is defined in sleep_prompt
            temperature=prompt["temperature"],
            messages=prompt["messages"],
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        return parsed
    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_diet_schedule(diet_plan: dict):
    prompt = copy.deepcopy(diet_prompt)
    prompt["messages"][1]["content"] = prompt["messages"][1]["content"].replace(
        "{diet_plan_json}", json.dumps(diet_plan, ensure_ascii=False)
    )

    try:
        response = client.chat.completions.create(
            model=prompt["model"],
            temperature=prompt.get("temperature", 0.0),
            messages=prompt["messages"],
            response_format={
                "type": "json_object"
            },  # enforce raw JSON (no code fences)
        )
        content = response.choices[0].message.content

        # Primary parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: slice first { ... } in case of wrappers
            i, j = content.find("{"), content.rfind("}")
            if i != -1 and j != -1 and j >= i:
                return json.loads(content[i : j + 1])
            raise

    except Exception as e:
        print(f"Error: {e}")
        return None


# print(sleep_plan)
# print(meal_plan)
print(workout_plan)
# print(substance_plan)
# generate_sleep_schedule(sleep_plan)
# print(meal_plan)
# gen_meal_plan = generate_diet_schedule(meal_plan)
