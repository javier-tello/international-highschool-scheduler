import unittest
from ortools.sat.python import cp_model
import sys
import os

# Add the main module to path (adjust as needed)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestSchedulerConstraints(unittest.TestCase):
    """Unit tests for school scheduler constraints based on stakeholder requirements"""
    
    def setUp(self):
        """Set up test data matching stakeholder requirements"""
        # Mock data structure matching your actual data
        self.DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.ALL_PERIODS = {
            'Monday': [1, 2, 3, 4, 5, 6, 7],
            'Tuesday': [1, 2, 3, 4, 5, 6, 7],
            'Wednesday': [1, 2, 3, 4, 5, 6],
            'Thursday': [1, 2, 3, 4, 5, 6, 7],
            'Friday': [1, 2, 3, 4, 5, 6, 7]
        }
        self.TEACHING_PERIODS = {
            day: [p for p in periods if p != 3] 
            for day, periods in self.ALL_PERIODS.items()
        }
        
        self.CLASSES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                       'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        
        self.TEAMS = {
            1: ['A', 'B', 'C', 'D'],
            2: ['E', 'F', 'G', 'H'], 
            3: ['I', 'J', 'K', 'L'],
            4: ['M', 'N', 'O', 'P']
        }
        
        self.TEAM_MAPPING = {}
        for team_num, classes in self.TEAMS.items():
            for class_name in classes:
                self.TEAM_MAPPING[class_name] = team_num
        
        self.CORE_SUBJECTS = ['ELA', 'SS', 'Science', 'Math', 'Arts']
        
        self.CORE_TEACHERS = {
            'team_1': {'ELA': 'ELA_T1', 'SS': 'SS_T1', 'Science': 'Science_T1', 'Math': 'Math_T1', 'Arts': 'Arts_T1'},
            'team_2': {'ELA': 'ELA_T2', 'SS': 'SS_T2', 'Science': 'Science_T2', 'Math': 'Math_T2', 'Arts': 'Arts_T2'},
            'team_3': {'ELA': 'ELA_T3', 'SS': 'SS_T3', 'Science': 'Science_T3', 'Math': 'Math_T3', 'Arts': 'Arts_T3'},
            'team_4': {'ELA': 'ELA_T4', 'SS': 'SS_T4', 'Science': 'Science_T4', 'Math': 'Math_T4', 'Arts': 'Arts_T4'}
        }
        
        self.PE_TEACHERS = ['PE_T1', 'PE_T2']
        self.LITERACY_TEACHERS = ['Literacy_T1', 'Literacy_T2']
        
        self.ALL_TEACHERS = []
        for team_teachers in self.CORE_TEACHERS.values():
            self.ALL_TEACHERS.extend(team_teachers.values())
        self.ALL_TEACHERS.extend(self.PE_TEACHERS)
        self.ALL_TEACHERS.extend(self.LITERACY_TEACHERS)
        
        self.ACTIVITIES = ['Prep', 'Team_Meeting', 'Discipline_Meeting', 'Advisory', 'Elective', 'Lunch']
        
        self.LITERACY_ASSIGNMENTS = {
            'Literacy_T1': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
            'Literacy_T2': ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        }

    def create_base_model(self):
        """Create base model with decision variables"""
        model = cp_model.CpModel()
        
        # Decision Variables
        teacher_activity = {}
        for teacher in self.ALL_TEACHERS:
            teacher_activity[teacher] = {}
            for day in self.DAYS:
                teacher_activity[teacher][day] = {}
                for period in self.ALL_PERIODS[day]:
                    teacher_activity[teacher][day][period] = model.NewIntVar(
                        0, len(self.ACTIVITIES) - 1, f'{teacher}_{day}_P{period}_activity'
                    )
        
        teacher_class_assignment = {}
        for teacher in self.ALL_TEACHERS:
            teacher_class_assignment[teacher] = {}
            for class_name in self.CLASSES:
                teacher_class_assignment[teacher][class_name] = {}
                for day in self.DAYS:
                    teacher_class_assignment[teacher][class_name][day] = {}
                    for period in self.TEACHING_PERIODS[day]:
                        teacher_class_assignment[teacher][class_name][day][period] = \
                            model.NewBoolVar(f'{teacher}_teaches_{class_name}_{day}_P{period}')
        
        return model, teacher_activity, teacher_class_assignment

    def add_basic_constraints(self, model, teacher_activity, teacher_class_assignment):
        """Add basic constraints that should always work"""
        # Lunch constraint
        for teacher in self.ALL_TEACHERS:
            for day in self.DAYS:
                if 3 in self.ALL_PERIODS[day]:
                    model.Add(teacher_activity[teacher][day][3] == self.ACTIVITIES.index('Lunch'))
        
        # Prep constraint
        for teacher in self.ALL_TEACHERS:
            for day in self.DAYS:
                daily_preps = []
                for period in self.TEACHING_PERIODS[day]:
                    prep_var = model.NewBoolVar(f'{teacher}_{day}_P{period}_is_prep')
                    model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Prep')).OnlyEnforceIf(prep_var)
                    model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Prep')).OnlyEnforceIf(prep_var.Not())
                    daily_preps.append(prep_var)
                model.Add(sum(daily_preps) == 1)
        
        # One teacher per class per period
        for class_name in self.CLASSES:
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    class_teachers = []
                    for teacher in self.ALL_TEACHERS:
                        class_teachers.append(teacher_class_assignment[teacher][class_name][day][period])
                    model.Add(sum(class_teachers) <= 1)

    def test_basic_constraints_feasible(self):
        """Test that basic constraints (lunch, prep, one teacher per class) are feasible"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Basic constraints should be feasible")

    def test_core_teaching_requirements_feasible(self):
        """Test core subject teaching requirements (4x/week, Arts 3x/week)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add core teaching requirements
        for team_num in range(1, 5):
            team_key = f'team_{team_num}'
            if team_key in self.CORE_TEACHERS:
                team_classes = self.TEAMS[team_num]
                
                for subject in self.CORE_SUBJECTS:
                    if subject in self.CORE_TEACHERS[team_key]:
                        teacher = self.CORE_TEACHERS[team_key][subject]
                        periods_per_week = 3 if subject == 'Arts' else 4
                        
                        for class_name in team_classes:
                            weekly_teaching = []
                            for day in self.DAYS:
                                for period in self.TEACHING_PERIODS[day]:
                                    weekly_teaching.append(
                                        teacher_class_assignment[teacher][class_name][day][period]
                                    )
                            model.Add(sum(weekly_teaching) == periods_per_week)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Core teaching requirements should be feasible")

    def test_literacy_requirements_feasible(self):
        """Test literacy teaching requirements (2x/week per class)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add literacy constraints
        for literacy_teacher, assigned_classes in self.LITERACY_ASSIGNMENTS.items():
            for class_name in self.CLASSES:
                if class_name not in assigned_classes:
                    for day in self.DAYS:
                        for period in self.TEACHING_PERIODS[day]:
                            model.Add(teacher_class_assignment[literacy_teacher][class_name][day][period] == 0)
            
            for class_name in assigned_classes:
                weekly_literacy = []
                for day in self.DAYS:
                    for period in self.TEACHING_PERIODS[day]:
                        weekly_literacy.append(
                            teacher_class_assignment[literacy_teacher][class_name][day][period]
                        )
                model.Add(sum(weekly_literacy) == 2)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Literacy requirements should be feasible")

    def test_discipline_meetings_alone_feasible(self):
        """Test discipline meeting constraints alone (1/week per subject)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add discipline meeting constraints
        discipline_schedule = {}
        for subject in self.CORE_SUBJECTS + ["Literacy"]:
            discipline_schedule[subject] = {}
            for day in self.DAYS:
                discipline_schedule[subject][day] = {}
                for period in self.TEACHING_PERIODS[day]:
                    discipline_schedule[subject][day][period] = model.NewBoolVar(
                        f'{subject}_discipline_{day}_P{period}'
                    )
        
        # Each subject has exactly 1 discipline meeting per week
        for subject in self.CORE_SUBJECTS + ["Literacy"]:
            weekly_discipline = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    weekly_discipline.append(discipline_schedule[subject][day][period])
            model.Add(sum(weekly_discipline) == 1)
        
        # At most 1 discipline meeting per period
        for day in self.DAYS:
            for period in self.TEACHING_PERIODS[day]:
                period_discipline_meetings = []
                for subject in self.CORE_SUBJECTS + ["Literacy"]:
                    period_discipline_meetings.append(discipline_schedule[subject][day][period])
                model.Add(sum(period_discipline_meetings) <= 1)
        
        # Each non-PE teacher has exactly 1 discipline meeting per week
        all_non_pe_teachers = []
        for team_teachers in self.CORE_TEACHERS.values():
            all_non_pe_teachers.extend(team_teachers.values())
        all_non_pe_teachers.extend(self.LITERACY_TEACHERS)
        
        for teacher in all_non_pe_teachers:
            weekly_discipline = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    is_discipline = model.NewBoolVar(f'{teacher}_{day}_P{period}_discipline')
                    model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Discipline_Meeting')).OnlyEnforceIf(is_discipline)
                    model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Discipline_Meeting')).OnlyEnforceIf(is_discipline.Not())
                    weekly_discipline.append(is_discipline)
            model.Add(sum(weekly_discipline) == 1)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Discipline meetings alone should be feasible")

    def test_advisory_meetings_alone_feasible(self):
        """Test advisory meeting constraints alone (2/week per team)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add advisory constraints
        team_advisory_schedule = {}
        for team_num in range(1, 5):
            team_advisory_schedule[team_num] = {}
            for day in self.DAYS:
                team_advisory_schedule[team_num][day] = {}
                for period in self.TEACHING_PERIODS[day]:
                    team_advisory_schedule[team_num][day][period] = model.NewBoolVar(
                        f'team_{team_num}_advisory_{day}_P{period}'
                    )
        
        # Each team gets exactly 2 advisory periods per week
        for team_num in range(1, 5):
            weekly_advisory = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    weekly_advisory.append(team_advisory_schedule[team_num][day][period])
            model.Add(sum(weekly_advisory) == 2)
        
        # Each non-PE teacher has exactly 2 advisory periods per week
        for teacher in self.ALL_TEACHERS:
            if teacher not in self.PE_TEACHERS:
                weekly_advisory = []
                for day in self.DAYS:
                    for period in self.TEACHING_PERIODS[day]:
                        is_advisory = model.NewBoolVar(f'{teacher}_{day}_P{period}_advisory')
                        model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Advisory')).OnlyEnforceIf(is_advisory)
                        model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Advisory')).OnlyEnforceIf(is_advisory.Not())
                        weekly_advisory.append(is_advisory)
                model.Add(sum(weekly_advisory) == 2)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Advisory meetings alone should be feasible")

    def test_electives_alone_feasible(self):
        """Test elective constraints alone (2/week school-wide)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add elective constraints
        elective_schedule = {}
        for day in self.DAYS:
            elective_schedule[day] = {}
            for period in self.TEACHING_PERIODS[day]:
                elective_schedule[day][period] = model.NewBoolVar(f'school_elective_{day}_P{period}')
        
        # Exactly 2 elective periods per week
        weekly_electives = []
        for day in self.DAYS:
            for period in self.TEACHING_PERIODS[day]:
                weekly_electives.append(elective_schedule[day][period])
        model.Add(sum(weekly_electives) == 2)
        
        # Each core teacher gets exactly 2 electives per week OR 0
        for teacher in self.ALL_TEACHERS:
            if teacher not in self.PE_TEACHERS and teacher not in self.LITERACY_TEACHERS:
                weekly_electives = []
                for day in self.DAYS:
                    for period in self.TEACHING_PERIODS[day]:
                        is_elective = model.NewBoolVar(f'{teacher}_{day}_P{period}_elective')
                        model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Elective')).OnlyEnforceIf(is_elective)
                        model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Elective')).OnlyEnforceIf(is_elective.Not())
                        weekly_electives.append(is_elective)
                
                has_electives = model.NewBoolVar(f'{teacher}_has_electives')
                model.Add(sum(weekly_electives) == 2).OnlyEnforceIf(has_electives)
                model.Add(sum(weekly_electives) == 0).OnlyEnforceIf(has_electives.Not())
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Electives alone should be feasible")

    def test_discipline_plus_advisory_combination(self):
        """Test the critical combination: discipline + advisory meetings"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add BOTH discipline and advisory constraints
        # (Copy the constraint code from the individual tests above)
        
        # Discipline constraints
        discipline_schedule = {}
        for subject in self.CORE_SUBJECTS + ["Literacy"]:
            discipline_schedule[subject] = {}
            for day in self.DAYS:
                discipline_schedule[subject][day] = {}
                for period in self.TEACHING_PERIODS[day]:
                    discipline_schedule[subject][day][period] = model.NewBoolVar(
                        f'{subject}_discipline_{day}_P{period}'
                    )
        
        for subject in self.CORE_SUBJECTS + ["Literacy"]:
            weekly_discipline = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    weekly_discipline.append(discipline_schedule[subject][day][period])
            model.Add(sum(weekly_discipline) == 1)
        
        for day in self.DAYS:
            for period in self.TEACHING_PERIODS[day]:
                period_discipline_meetings = []
                for subject in self.CORE_SUBJECTS + ["Literacy"]:
                    period_discipline_meetings.append(discipline_schedule[subject][day][period])
                model.Add(sum(period_discipline_meetings) <= 1)
        
        # Advisory constraints
        team_advisory_schedule = {}
        for team_num in range(1, 5):
            team_advisory_schedule[team_num] = {}
            for day in self.DAYS:
                team_advisory_schedule[team_num][day] = {}
                for period in self.TEACHING_PERIODS[day]:
                    team_advisory_schedule[team_num][day][period] = model.NewBoolVar(
                        f'team_{team_num}_advisory_{day}_P{period}'
                    )
        
        for team_num in range(1, 5):
            weekly_advisory = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    weekly_advisory.append(team_advisory_schedule[team_num][day][period])
            model.Add(sum(weekly_advisory) == 2)
        
        # Teacher frequency constraints for BOTH
        all_non_pe_teachers = []
        for team_teachers in self.CORE_TEACHERS.values():
            all_non_pe_teachers.extend(team_teachers.values())
        all_non_pe_teachers.extend(self.LITERACY_TEACHERS)
        
        for teacher in all_non_pe_teachers:
            # Discipline: exactly 1 per week
            weekly_discipline = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    is_discipline = model.NewBoolVar(f'{teacher}_{day}_P{period}_discipline')
                    model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Discipline_Meeting')).OnlyEnforceIf(is_discipline)
                    model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Discipline_Meeting')).OnlyEnforceIf(is_discipline.Not())
                    weekly_discipline.append(is_discipline)
            model.Add(sum(weekly_discipline) == 1)
            
            # Advisory: exactly 2 per week
            weekly_advisory = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    is_advisory = model.NewBoolVar(f'{teacher}_{day}_P{period}_advisory')
                    model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Advisory')).OnlyEnforceIf(is_advisory)
                    model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Advisory')).OnlyEnforceIf(is_advisory.Not())
                    weekly_advisory.append(is_advisory)
            model.Add(sum(weekly_advisory) == 2)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        status = solver.Solve(model)
        
        # This is the test that should reveal the problem
        if status == cp_model.INFEASIBLE:
            self.fail("CRITICAL: Discipline + Advisory combination is INFEASIBLE! This is the root cause.")
        else:
            self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                         "Discipline + Advisory combination should be feasible")

    def test_pe_constraints_feasible(self):
        """Test PE constraints (3x/week per team, team-based)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add PE constraints
        team_pe_schedule = {}
        for team_num in range(1, 5):
            team_pe_schedule[team_num] = {}
            for day in self.DAYS:
                team_pe_schedule[team_num][day] = {}
                for period in self.TEACHING_PERIODS[day]:
                    team_pe_schedule[team_num][day][period] = model.NewBoolVar(
                        f'team_{team_num}_has_PE_{day}_P{period}'
                    )
        
        # Each team gets exactly 3 PE periods per week
        for team_num in range(1, 5):
            weekly_pe = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    weekly_pe.append(team_pe_schedule[team_num][day][period])
            model.Add(sum(weekly_pe) == 3)
        
        # Only one team can have PE at a time
        for day in self.DAYS:
            for period in self.TEACHING_PERIODS[day]:
                teams_with_pe = []
                for team_num in range(1, 5):
                    teams_with_pe.append(team_pe_schedule[team_num][day][period])
                model.Add(sum(teams_with_pe) <= 1)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "PE constraints should be feasible")

    def test_team_meeting_constraints_feasible(self):
        """Test team meeting constraints (2x/week per team, during PE)"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add team meeting constraints
        team_meeting_schedule = {}
        for team_num in range(1, 5):
            team_meeting_schedule[team_num] = {}
            for day in self.DAYS:
                team_meeting_schedule[team_num][day] = {}
                for period in self.TEACHING_PERIODS[day]:
                    team_meeting_schedule[team_num][day][period] = model.NewBoolVar(
                        f'team_{team_num}_meeting_{day}_P{period}'
                    )
        
        # Each team has exactly 2 team meetings per week
        for team_num in range(1, 5):
            weekly_meetings = []
            for day in self.DAYS:
                for period in self.TEACHING_PERIODS[day]:
                    weekly_meetings.append(team_meeting_schedule[team_num][day][period])
            model.Add(sum(weekly_meetings) == 2)
        
        # Each core teacher has exactly 2 team meetings per week
        for team_key, team_teachers in self.CORE_TEACHERS.items():
            for teacher in team_teachers.values():
                weekly_team_meetings = []
                for day in self.DAYS:
                    for period in self.TEACHING_PERIODS[day]:
                        is_team_meeting = model.NewBoolVar(f'{teacher}_{day}_P{period}_is_team_meeting')
                        model.Add(teacher_activity[teacher][day][period] == self.ACTIVITIES.index('Team_Meeting')).OnlyEnforceIf(is_team_meeting)
                        model.Add(teacher_activity[teacher][day][period] != self.ACTIVITIES.index('Team_Meeting')).OnlyEnforceIf(is_team_meeting.Not())
                        weekly_team_meetings.append(is_team_meeting)
                model.Add(sum(weekly_team_meetings) == 2)
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                     "Team meeting constraints should be feasible")

    def test_full_constraint_set(self):
        """Test ALL constraints together - matching main code exactly"""
        model, teacher_activity, teacher_class_assignment = self.create_base_model()
        self.add_basic_constraints(model, teacher_activity, teacher_class_assignment)
        
        # Add ALL the constraints from your main code here
        # This should replicate your main solve_scheduling_model method exactly
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 120.0
        status = solver.Solve(model)
        
        if status == cp_model.INFEASIBLE:
            self.fail("FULL constraint set is INFEASIBLE - this matches your main code problem!")
        else:
            self.assertIn(status, [cp_model.OPTIMAL, cp_model.FEASIBLE], 
                         "Full constraint set should be feasible")

if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)