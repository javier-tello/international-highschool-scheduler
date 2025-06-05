from ortools.sat.python import cp_model
from collections import defaultdict

# ============================================================================
# DATA STRUCTURES
# ============================================================================

# Time slots (34 periods total, period 3 is lunch)
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
ALL_PERIODS = {
    'Monday': [1, 2, 3, 4, 5, 6, 7, 8],      # 8 periods (3 is lunch)
    'Tuesday': [1, 2, 3, 4, 5, 6, 7, 8],     # 8 periods
    'Wednesday': [1, 2, 3, 4, 5, 6, 7],      # 7 periods
    'Thursday': [1, 2, 3, 4, 5, 6, 7, 8],    # 8 periods
    'Friday': [1, 2, 3, 4, 5, 6, 7, 8]       # 8 periods
}

# Non-lunch periods (for scheduling classes)
TEACHING_PERIODS = {
    'Monday': [1, 2, 4, 5, 6, 7, 8],      # 7 periods (skip 3 for lunch)
    'Tuesday': [1, 2, 4, 5, 6, 7, 8],     # 7 periods
    'Wednesday': [1, 2, 4, 5, 6, 7],      # 6 periods
    'Thursday': [1, 2, 4, 5, 6, 7, 8],    # 7 periods
    'Friday': [1, 2, 4, 5, 6, 7, 8]       # 7 periods
}

# All time slots as (day, period) tuples
ALL_TIME_SLOTS = []
for day in DAYS:
    for period in ALL_PERIODS[day]:
        ALL_TIME_SLOTS.append((day, period))

# Classes and team mappings
CLASSES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
           'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

TEAM_MAPPING = {
    'A': 1, 'B': 1, 'C': 1, 'D': 1,
    'E': 2, 'F': 2, 'G': 2, 'H': 2,
    'I': 3, 'J': 3, 'K': 3, 'L': 3,
    'M': 4, 'N': 4, 'O': 4, 'P': 4
}

# Core subjects and teachers
CORE_SUBJECTS = ['ELA', 'SS', 'Science', 'Math', 'Arts']

# Teacher assignments
TEACHERS = {
    'team_1': {
        'ELA': 'ELA_T1', 'SS': 'SS_T1', 'Science': 'Science_T1', 
        'Math': 'Math_T1', 'Arts': 'Arts_T1', 'Literacy': 'Literacy_T1'
    },
    'team_2': {
        'ELA': 'ELA_T2', 'SS': 'SS_T2', 'Science': 'Science_T2', 
        'Math': 'Math_T2', 'Arts': 'Arts_T2', 'Literacy': 'Literacy_T1'
    },
    'team_3': {
        'ELA': 'ELA_T3', 'SS': 'SS_T3', 'Science': 'Science_T3', 
        'Math': 'Math_T3', 'Arts': 'Arts_T3', 'Literacy': 'Literacy_T2'
    },
    'team_4': {
        'ELA': 'ELA_T4', 'SS': 'SS_T4', 'Science': 'Science_T4', 
        'Math': 'Math_T4', 'Arts': 'Arts_T4', 'Literacy': 'Literacy_T2'
    }
}

# PE teachers (serve all teams)
PE_TEACHERS = ['PE_T1', 'PE_T2']

# All teachers list
ALL_TEACHERS = []
for team_data in TEACHERS.values():
    ALL_TEACHERS.extend(team_data.values())
ALL_TEACHERS.extend(PE_TEACHERS)
ALL_TEACHERS = list(set(ALL_TEACHERS))  # Remove duplicates

# Activity types
ACTIVITIES = ['Teaching', 'Prep', 'Team_Meeting', 'Discipline_Meeting', 
              'Advisory', 'Elective', 'Lunch']

# ============================================================================
# OR-TOOLS CP-SAT SETUP
# ============================================================================

model = cp_model.CpModel()

# Decision Variables
# teacher_activity[teacher][day][period] = activity_type
teacher_activity = {}
for teacher in ALL_TEACHERS:
    teacher_activity[teacher] = {}
    for day in DAYS:
        teacher_activity[teacher][day] = {}
        for period in ALL_PERIODS[day]:  # Now includes period 3
            teacher_activity[teacher][day][period] = model.NewIntVar(
                0, len(ACTIVITIES) - 1, 
                f'{teacher}_{day}_P{period}_activity'
            )

# class_subject[class][day][period] = subject (or activity)
class_subject = {}
for class_name in CLASSES:
    class_subject[class_name] = {}
    for day in DAYS:
        class_subject[class_name][day] = {}
        for period in TEACHING_PERIODS[day]:  # Only non-lunch periods
            class_subject[class_name][day][period] = model.NewIntVar(
                0, len(CORE_SUBJECTS) + 10,  # Extra space for PE, Literacy, etc.
                f'Class_{class_name}_{day}_P{period}_subject'
            )

# teacher_class_assignment[teacher][class][day][period] = 1 if teaching
teacher_class_assignment = {}
for teacher in ALL_TEACHERS:
    teacher_class_assignment[teacher] = {}
    for class_name in CLASSES:
        teacher_class_assignment[teacher][class_name] = {}
        for day in DAYS:
            teacher_class_assignment[teacher][class_name][day] = {}
            for period in TEACHING_PERIODS[day]:  # Only non-lunch periods
                teacher_class_assignment[teacher][class_name][day][period] = \
                    model.NewBoolVar(
                        f'{teacher}_teaches_{class_name}_{day}_P{period}'
                    )

# ============================================================================
# BASIC CONSTRAINTS
# ============================================================================

# Constraint: All teachers have lunch during period 3
for teacher in ALL_TEACHERS:
    for day in DAYS:
        if 3 in ALL_PERIODS[day]:  # Check if period 3 exists for this day
            model.Add(teacher_activity[teacher][day][3] == ACTIVITIES.index('Lunch'))

# Constraint: Each teacher has exactly 1 prep per day
for teacher in ALL_TEACHERS:
    for day in DAYS:
        daily_preps = []
        for period in TEACHING_PERIODS[day]:  # Only check non-lunch periods
            prep_var = model.NewBoolVar(f'{teacher}_{day}_P{period}_is_prep')
            model.Add(teacher_activity[teacher][day][period] == ACTIVITIES.index('Prep')).OnlyEnforceIf(prep_var)
            model.Add(teacher_activity[teacher][day][period] != ACTIVITIES.index('Prep')).OnlyEnforceIf(prep_var.Not())
            daily_preps.append(prep_var)
        model.Add(sum(daily_preps) == 1)

# Constraint: Core teachers teach 4 periods per week to each of their classes
for team_num in range(1, 5):
    team_key = f'team_{team_num}'
    team_classes = [c for c in CLASSES if TEAM_MAPPING[c] == team_num]
    
    for subject in CORE_SUBJECTS:
        teacher = TEACHERS[team_key][subject]
        for class_name in team_classes:
            weekly_teaching = []
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:  # Only non-lunch periods
                    weekly_teaching.append(
                        teacher_class_assignment[teacher][class_name][day][period]
                    )
            model.Add(sum(weekly_teaching) == 4)

print("Data structures and basic CP-SAT model setup complete!")
print(f"Total teachers: {len(ALL_TEACHERS)}")
print(f"Total time slots: {len(ALL_TIME_SLOTS)}")
print(f"Total classes: {len(CLASSES)}")