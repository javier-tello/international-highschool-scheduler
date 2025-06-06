import gspread
from google.oauth2.service_account import Credentials
from ortools.sat.python import cp_model
import time
from datetime import datetime

# ============================================================================
# GOOGLE SHEETS INTEGRATION CLASS
# ============================================================================

class SchoolSchedulerGoogleSheets:
    def __init__(self, credentials_file, spreadsheet_name):
        """
        Initialize Google Sheets connection
        
        Args:
            credentials_file: Path to Google service account JSON file
            spreadsheet_name: Name of the Google Spreadsheet
        """
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.gc = None
        self.spreadsheet = None
        self.connect()
    
    def connect(self):
        """Connect to Google Sheets"""
        try:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            self.gc = gspread.authorize(creds)
            
            # Try to open existing spreadsheet or create new one
            try:
                self.spreadsheet = self.gc.open(self.spreadsheet_name)
                print(f"✅ Connected to existing spreadsheet: {self.spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.gc.create(self.spreadsheet_name)
                print(f"✅ Created new spreadsheet: {self.spreadsheet_name}")
                
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
            raise

    def setup_input_sheets(self):
        """Create and populate input sheets with templates"""
        
        # 1. School Configuration Sheet
        try:
            config_sheet = self.spreadsheet.worksheet("School_Config")
        except gspread.WorksheetNotFound:
            config_sheet = self.spreadsheet.add_worksheet("School_Config", 20, 10)
        
        config_data = [
            ["Parameter", "Value", "Description"],
            ["School Name", "Sample Middle School", "Name of the school"],
            ["Total Teams", "4", "Number of grade teams"],
            ["Classes per Team", "4", "Number of classes per team"],
            ["Core Subjects", "ELA,SS,Science,Math,Arts", "Comma-separated core subjects"],
            ["PE Teachers", "2", "Number of PE teachers"],
            ["Literacy Teachers", "2", "Number of literacy teachers"],
            ["Periods per Day", "Monday:7,Tuesday:7,Wednesday:6,Thursday:7,Friday:7", "Periods by day"],
            ["Lunch Period", "3", "Fixed lunch period number"],
            ["Core Periods per Week", "4", "Periods per week for core subjects"],
            ["PE Periods per Week", "3", "PE periods per team per week"],
            ["Literacy Periods per Week", "2", "Literacy periods per class per week"],
            ["Team Meetings per Week", "2", "Team meetings per team per week"],
            ["Advisory Periods per Week", "2", "Advisory periods per team per week"],
            ["Elective Periods per Week", "2", "School-wide elective periods per week"]
        ]
        config_sheet.clear()
        config_sheet.update('A1', config_data)
        
        # 2. Teachers Sheet
        try:
            teachers_sheet = self.spreadsheet.worksheet("Teachers")
        except gspread.WorksheetNotFound:
            teachers_sheet = self.spreadsheet.add_worksheet("Teachers", 30, 6)
        
        teachers_data = [
            ["Teacher Name", "Subject", "Team", "Type", "Notes", "Active"],
            ["ELA_T1", "ELA", "1", "Core", "Team 1 ELA Teacher", "TRUE"],
            ["SS_T1", "SS", "1", "Core", "Team 1 Social Studies Teacher", "TRUE"],
            ["Science_T1", "Science", "1", "Core", "Team 1 Science Teacher", "TRUE"],
            ["Math_T1", "Math", "1", "Core", "Team 1 Math Teacher", "TRUE"],
            ["Arts_T1", "Arts", "1", "Core", "Team 1 Arts Teacher", "TRUE"],
            ["ELA_T2", "ELA", "2", "Core", "Team 2 ELA Teacher", "TRUE"],
            ["SS_T2", "SS", "2", "Core", "Team 2 Social Studies Teacher", "TRUE"],
            ["Science_T2", "Science", "2", "Core", "Team 2 Science Teacher", "TRUE"],
            ["Math_T2", "Math", "2", "Core", "Team 2 Math Teacher", "TRUE"],
            ["Arts_T2", "Arts", "2", "Core", "Team 2 Arts Teacher", "TRUE"],
            ["ELA_T3", "ELA", "3", "Core", "Team 3 ELA Teacher", "TRUE"],
            ["SS_T3", "SS", "3", "Core", "Team 3 Social Studies Teacher", "TRUE"],
            ["Science_T3", "Science", "3", "Core", "Team 3 Science Teacher", "TRUE"],
            ["Math_T3", "Math", "3", "Core", "Team 3 Math Teacher", "TRUE"],
            ["Arts_T3", "Arts", "3", "Core", "Team 3 Arts Teacher", "TRUE"],
            ["ELA_T4", "ELA", "4", "Core", "Team 4 ELA Teacher", "TRUE"],
            ["SS_T4", "SS", "4", "Core", "Team 4 Social Studies Teacher", "TRUE"],
            ["Science_T4", "Science", "4", "Core", "Team 4 Science Teacher", "TRUE"],
            ["Math_T4", "Math", "4", "Core", "Team 4 Math Teacher", "TRUE"],
            ["Arts_T4", "Arts", "4", "Core", "Team 4 Arts Teacher", "TRUE"],
            ["Literacy_T1", "Literacy", "1,2", "Literacy", "Serves teams 1 and 2", "TRUE"],
            ["Literacy_T2", "Literacy", "3,4", "Literacy", "Serves teams 3 and 4", "TRUE"],
            ["PE_T1", "PE", "All", "PE", "PE Teacher 1", "TRUE"],
            ["PE_T2", "PE", "All", "PE", "PE Teacher 2", "TRUE"]
        ]
        teachers_sheet.clear()
        teachers_sheet.update('A1', teachers_data)
        
        # 3. Classes Sheet
        try:
            classes_sheet = self.spreadsheet.worksheet("Classes")
        except gspread.WorksheetNotFound:
            classes_sheet = self.spreadsheet.add_worksheet("Classes", 20, 5)
        
        classes_data = [
            ["Class Name", "Team", "Notes"],
            ["A", "1", "Team 1 Class A"],
            ["B", "1", "Team 1 Class B"],
            ["C", "1", "Team 1 Class C"],
            ["D", "1", "Team 1 Class D"],
            ["E", "2", "Team 2 Class E"],
            ["F", "2", "Team 2 Class F"],
            ["G", "2", "Team 2 Class G"],
            ["H", "2", "Team 2 Class H"],
            ["I", "3", "Team 3 Class I"],
            ["J", "3", "Team 3 Class J"],
            ["K", "3", "Team 3 Class K"],
            ["L", "3", "Team 3 Class L"],
            ["M", "4", "Team 4 Class M"],
            ["N", "4", "Team 4 Class N"],
            ["O", "4", "Team 4 Class O"],
            ["P", "4", "Team 4 Class P"]
        ]
        classes_sheet.clear()
        classes_sheet.update('A1', classes_data)
        
        # 4. Control Panel Sheet
        try:
            control_sheet = self.spreadsheet.worksheet("Control_Panel")
        except gspread.WorksheetNotFound:
            control_sheet = self.spreadsheet.add_worksheet("Control_Panel", 15, 5)
        
        control_data = [
            ["School Scheduler Control Panel", "", "", "", ""],
            ["", "", "", "", ""],
            ["Instructions:", "", "", "", ""],
            ["1. Review and modify data in other sheets", "", "", "", ""],
            ["2. Run the Python script to generate schedule", "", "", "", ""],
            ["3. View results in Teacher_Schedules and Class_Schedules sheets", "", "", "", ""],
            ["", "", "", "", ""],
            ["Status:", "Ready", "", "", ""],
            ["Last Run:", "Never", "", "", ""],
            ["Solve Time:", "N/A", "", "", ""],
            ["Solution Quality:", "N/A", "", "", ""],
            ["", "", "", "", ""],
            ["Note:", "Run the Python script to generate schedules", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", "", ""]
        ]
        control_sheet.clear()
        control_sheet.update('A1', control_data)
        
        print("✅ Input sheets created successfully!")

    def read_configuration(self):
        """Read school configuration from Google Sheets"""
        try:
            config_sheet = self.spreadsheet.worksheet("School_Config")
            config_data = config_sheet.get_all_records()
            
            config = {}
            for row in config_data:
                config[row['Parameter']] = row['Value']
            
            return config
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
            return None

    def read_teachers(self):
        """Read teacher data from Google Sheets"""
        try:
            teachers_sheet = self.spreadsheet.worksheet("Teachers")
            teachers_data = teachers_sheet.get_all_records()
            
            # Filter active teachers only
            active_teachers = [t for t in teachers_data if t['Active'].upper() == 'TRUE']
            
            return active_teachers
        except Exception as e:
            print(f"❌ Error reading teachers: {e}")
            return None

    def read_classes(self):
        """Read class data from Google Sheets"""
        try:
            classes_sheet = self.spreadsheet.worksheet("Classes")
            classes_data = classes_sheet.get_all_records()
            
            return classes_data
        except Exception as e:
            print(f"❌ Error reading classes: {e}")
            return None

    def update_status(self, status, last_run=None, solve_time=None, quality=None):
        """Update control panel status"""
        try:
            control_sheet = self.spreadsheet.worksheet("Control_Panel")
            
            # Update status - use new API format (values first, then range)
            control_sheet.update([[status]], 'B8:B8')
            
            if last_run:
                control_sheet.update([[last_run]], 'B9:B9')
            if solve_time:
                control_sheet.update([[f"{solve_time:.2f} seconds"]], 'B10:B10')
            if quality:
                control_sheet.update([[quality]], 'B11:B11')
                
        except Exception as e:
            print(f"❌ Error updating status: {e}")

    def write_teacher_schedules(self, schedules_data):
        """Write teacher schedules to Google Sheets"""
        try:
            # Create or clear teacher schedules sheet with more rows
            try:
                schedule_sheet = self.spreadsheet.worksheet("Teacher_Schedules")
                schedule_sheet.clear()
            except gspread.WorksheetNotFound:
                schedule_sheet = self.spreadsheet.add_worksheet("Teacher_Schedules", 1000, 10)  # Increased rows
            
            # Prepare data for writing
            output_data = [["Teacher", "Day", "Period", "Activity", "Classes", "Subject", "Notes"]]
            
            for teacher_name, teacher_schedule in schedules_data.items():
                for day, day_schedule in teacher_schedule.items():
                    for period, period_info in day_schedule.items():
                        row = [
                            teacher_name,
                            day,
                            f"P{period}",
                            period_info.get('activity', ''),
                            ', '.join(period_info.get('classes', [])),
                            period_info.get('subject', ''),
                            period_info.get('notes', '')
                        ]
                        output_data.append(row)
            
            # Write to sheet in batches with new API format
            batch_size = 100
            for i in range(0, len(output_data), batch_size):
                batch = output_data[i:i + batch_size]
                start_row = i + 1
                end_row = start_row + len(batch) - 1
                range_name = f'A{start_row}:G{end_row}'
                schedule_sheet.update(batch, range_name)  # Values first, then range
            
            print("✅ Teacher schedules written to Google Sheets")
            
        except Exception as e:
            print(f"❌ Error writing teacher schedules: {e}")

    def write_class_schedules(self, schedules_data):
        """Write class schedules to Google Sheets"""
        try:
            # Create or clear class schedules sheet with more rows
            try:
                schedule_sheet = self.spreadsheet.worksheet("Class_Schedules")
                schedule_sheet.clear()
            except gspread.WorksheetNotFound:
                schedule_sheet = self.spreadsheet.add_worksheet("Class_Schedules", 1000, 8)  # Increased rows
            
            # Prepare data for writing
            output_data = [["Class", "Team", "Day", "Period", "Subject", "Teacher", "Activity Type"]]
            
            for class_name, class_schedule in schedules_data.items():
                for day, day_schedule in class_schedule.items():
                    for period, period_info in day_schedule.items():
                        row = [
                            class_name,
                            period_info.get('team', ''),
                            day,
                            f"P{period}",
                            period_info.get('subject', ''),
                            period_info.get('teacher', ''),
                            period_info.get('activity_type', '')
                        ]
                        output_data.append(row)
            
            # Write to sheet in batches with new API format
            batch_size = 100
            for i in range(0, len(output_data), batch_size):
                batch = output_data[i:i + batch_size]
                start_row = i + 1
                end_row = start_row + len(batch) - 1
                range_name = f'A{start_row}:G{end_row}'
                schedule_sheet.update(batch, range_name)  # Values first, then range
            
            print("✅ Class schedules written to Google Sheets")
            
        except Exception as e:
            print(f"❌ Error writing class schedules: {e}")

    def write_teacher_schedules_grid(self, schedules_data):
        """Write teacher schedules in grid format to Google Sheets"""
        try:
            print("🔧 Creating teacher schedules grid...")
            
            # Create or clear formatted teacher schedules sheet
            try:
                grid_sheet = self.spreadsheet.worksheet("Teacher_Schedules_Grid")
                grid_sheet.clear()
            except gspread.WorksheetNotFound:
                grid_sheet = self.spreadsheet.add_worksheet("Teacher_Schedules_Grid", 2000, 50)
            
            # Debug: Check if we have data
            if not schedules_data:
                print("❌ No schedule data provided")
                return
            
            print(f"📊 Processing {len(schedules_data)} teachers")
            
            # Get days and find all possible periods across all days
            first_teacher = list(schedules_data.keys())[0]
            days = list(schedules_data[first_teacher].keys())
            
            # Get all periods that exist across all days
            all_periods = set()
            for day in days:
                all_periods.update(schedules_data[first_teacher][day].keys())
            periods = sorted(list(all_periods))
            
            print(f"📅 Days: {days}")
            print(f"⏰ All periods found: {periods}")
            
            # Prepare grid data
            all_data = []
            
            # Create grids - 3 teachers per row
            teachers_per_row = 3
            all_teachers = list(schedules_data.keys())
            
            for i in range(0, len(all_teachers), teachers_per_row):
                row_teachers = all_teachers[i:i + teachers_per_row]
                
                # Teacher names header
                header_row = []
                for j, teacher in enumerate(row_teachers):
                    header_row.extend([teacher] + [''] * (len(days) - 1))
                    if j < len(row_teachers) - 1:  # Add separator except for last teacher
                        header_row.append('')
                all_data.append(header_row)
                
                # Days header
                days_row = []
                for j, teacher in enumerate(row_teachers):
                    days_row.extend(days)
                    if j < len(row_teachers) - 1:
                        days_row.append('')
                all_data.append(days_row)
                
                # Period rows
                for period in periods:
                    period_row = []
                    for j, teacher in enumerate(row_teachers):
                        period_data = []
                        for day in days:
                            try:
                                # Check if this period exists for this day
                                if period in schedules_data[teacher][day]:
                                    period_info = schedules_data[teacher][day][period]
                                    activity = period_info.get('activity', '')
                                    classes = period_info.get('classes', [])
                                    
                                    # Format cell content
                                    if activity == 'Teaching' and classes:
                                        cell_content = ', '.join(classes)
                                    elif activity == 'Lunch':
                                        cell_content = 'Lunch'
                                    elif activity == 'Prep':
                                        cell_content = 'Prep'
                                    elif activity == 'Team_Meeting':
                                        cell_content = 'Team Mtg'
                                    elif activity == 'Discipline_Meeting':
                                        cell_content = 'Disc Mtg'
                                    elif activity == 'Advisory':
                                        cell_content = 'Advisory'
                                    elif activity == 'Elective':
                                        cell_content = 'Elective'
                                    else:
                                        cell_content = activity or ''
                                else:
                                    # Period doesn't exist for this day (e.g., period 7 on Wednesday)
                                    cell_content = ''
                                
                                period_data.append(str(cell_content))
                            except KeyError as e:
                                print(f"⚠️ Missing data for {teacher}, {day}, period {period}: {e}")
                                period_data.append('')
                        
                        period_row.extend(period_data)
                        if j < len(row_teachers) - 1:
                            period_row.append('')  # Separator column
                    
                    all_data.append(period_row)
                
                # Add empty rows between teacher groups
                all_data.append([''] * len(header_row))
                all_data.append([''] * len(header_row))
            
            # Write data in smaller batches
            print(f"📝 Writing {len(all_data)} rows to Google Sheets...")
            
            batch_size = 50
            for batch_start in range(0, len(all_data), batch_size):
                batch_end = min(batch_start + batch_size, len(all_data))
                batch_data = all_data[batch_start:batch_end]
                
                if batch_data and batch_data[0]:  # Check if batch has data
                    max_cols = max(len(row) for row in batch_data)
                    end_col_letter = chr(ord('A') + max_cols - 1) if max_cols > 0 else 'A'
                    range_name = f'A{batch_start + 1}:{end_col_letter}{batch_end}'
                    
                    # Ensure all rows have the same length
                    for row in batch_data:
                        while len(row) < max_cols:
                            row.append('')
                    
                    grid_sheet.update(batch_data, range_name)
            
            print("✅ Teacher schedules grid written to Google Sheets")
        
        except Exception as e:
            print(f"❌ Error writing teacher schedules grid: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()

    def write_class_schedules_grid(self, schedules_data):
        """Write class schedules in grid format to Google Sheets"""
        try:
            print("🔧 Creating class schedules grid...")
            
            # Create or clear formatted class schedules sheet
            try:
                grid_sheet = self.spreadsheet.worksheet("Class_Schedules_Grid")
                grid_sheet.clear()
            except gspread.WorksheetNotFound:
                grid_sheet = self.spreadsheet.add_worksheet("Class_Schedules_Grid", 2000, 50)
            
            # Debug: Check if we have data
            if not schedules_data:
                print("❌ No schedule data provided")
                return
            
            print(f"📊 Processing {len(schedules_data)} classes")
            
            # Get days and find all possible periods across all days
            first_class = list(schedules_data.keys())[0]
            days = list(schedules_data[first_class].keys())
            
            # Get all periods that exist across all days
            all_periods = set()
            for day in days:
                all_periods.update(schedules_data[first_class][day].keys())
            periods = sorted(list(all_periods))
            
            print(f"📅 Days: {days}")
            print(f"⏰ All periods found: {periods}")
            
            # Group classes by team
            classes_by_team = {}
            for class_name, class_schedule in schedules_data.items():
                # Get team from first available period
                team = None
                for day in days:
                    for period in periods:
                        if period in class_schedule[day]:
                            team = class_schedule[day][period].get('team', 'Unknown')
                            break
                    if team:
                        break
                
                if team not in classes_by_team:
                    classes_by_team[team] = []
                classes_by_team[team].append(class_name)
            
            print(f"📚 Classes by team: {classes_by_team}")
            
            # Prepare grid data
            all_data = []
            
            # Create grids by team
            for team in sorted(classes_by_team.keys()):
                team_classes = sorted(classes_by_team[team])
                
                # Team header
                all_data.append([f'TEAM {team}'] + [''] * (len(days) * len(team_classes) - 1))
                
                # Class names header
                header_row = []
                for class_name in team_classes:
                    header_row.extend([class_name] + [''] * (len(days) - 1))
                all_data.append(header_row)
                
                # Days header
                days_row = []
                for class_name in team_classes:
                    days_row.extend(days)
                all_data.append(days_row)
                
                # Period rows
                for period in periods:
                    period_row = []
                    for class_name in team_classes:
                        period_data = []
                        for day in days:
                            try:
                                # Check if this period exists for this day
                                if period in schedules_data[class_name][day]:
                                    period_info = schedules_data[class_name][day][period]
                                    subject = period_info.get('subject', '')
                                    teacher = period_info.get('teacher', '')
                                    
                                    # Format cell content
                                    if subject == 'Lunch':
                                        cell_content = 'Lunch'
                                    elif teacher:
                                        cell_content = f'{subject}'
                                    else:
                                        cell_content = subject
                                else:
                                    # Period doesn't exist for this day (e.g., period 7 on Wednesday)
                                    cell_content = ''
                                
                                period_data.append(str(cell_content))
                            except KeyError as e:
                                print(f"⚠️ Missing data for {class_name}, {day}, period {period}: {e}")
                                period_data.append('')
                        
                        period_row.extend(period_data)
                    
                    all_data.append(period_row)
                
                # Add empty rows between teams
                all_data.append([''] * len(header_row))
                all_data.append([''] * len(header_row))
            
            # Write data in smaller batches
            print(f"📝 Writing {len(all_data)} rows to Google Sheets...")
            
            batch_size = 50
            for batch_start in range(0, len(all_data), batch_size):
                batch_end = min(batch_start + batch_size, len(all_data))
                batch_data = all_data[batch_start:batch_end]
                
                if batch_data and batch_data[0]:  # Check if batch has data
                    max_cols = max(len(row) for row in batch_data)
                    end_col_letter = chr(ord('A') + max_cols - 1) if max_cols > 0 else 'A'
                    range_name = f'A{batch_start + 1}:{end_col_letter}{batch_end}'
                    
                    # Ensure all rows have the same length
                    for row in batch_data:
                        while len(row) < max_cols:
                            row.append('')
                    
                    grid_sheet.update(batch_data, range_name)
            
            print("✅ Class schedules grid written to Google Sheets")
            
        except Exception as e:
            print(f"❌ Error writing class schedules grid: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()       

# ============================================================================
# INTEGRATED SCHEDULER CLASS
# ============================================================================

class GoogleSheetsScheduler:
    def __init__(self, credentials_file, spreadsheet_name):
        self.sheets = SchoolSchedulerGoogleSheets(credentials_file, spreadsheet_name)
        
    def setup_sheets(self):
        """Setup input sheets with templates"""
        self.sheets.setup_input_sheets()
        
    def load_data_from_sheets(self):
        """Load all data from Google Sheets"""
        print("📊 Loading data from Google Sheets...")
        
        # Read configuration
        config = self.sheets.read_configuration()
        if not config:
            raise Exception("Failed to read configuration")
        
        # Read teachers
        teachers_data = self.sheets.read_teachers()
        if not teachers_data:
            raise Exception("Failed to read teachers")
        
        # Read classes
        classes_data = self.sheets.read_classes()
        if not classes_data:
            raise Exception("Failed to read classes")
        
        print(f"✅ Loaded {len(teachers_data)} teachers and {len(classes_data)} classes")
        
        return config, teachers_data, classes_data
    
    def convert_sheets_data_to_model_format(self, config, teachers_data, classes_data):
        """Convert Google Sheets data to model format"""
        
        # Parse periods by day
        periods_str = config['Periods per Day']
        ALL_PERIODS = {}
        TEACHING_PERIODS = {}
        lunch_period = int(config['Lunch Period'])
        
        for day_info in periods_str.split(','):
            day, periods = day_info.split(':')
            period_count = int(periods)
            ALL_PERIODS[day] = list(range(1, period_count + 1))
            TEACHING_PERIODS[day] = [p for p in range(1, period_count + 1) if p != lunch_period]
        
        # Build classes and teams
        CLASSES = [c['Class Name'] for c in classes_data]
        TEAM_MAPPING = {c['Class Name']: int(c['Team']) for c in classes_data}
        
        # Build teams
        TEAMS = {}
        for class_data in classes_data:
            team_num = int(class_data['Team'])
            if team_num not in TEAMS:
                TEAMS[team_num] = []
            TEAMS[team_num].append(class_data['Class Name'])
        
        # Build teacher structure
        CORE_SUBJECTS = config['Core Subjects'].split(',')
        TEACHERS = {}
        PE_TEACHERS = []
        ALL_TEACHERS = []
        
        for teacher in teachers_data:
            teacher_name = teacher['Teacher Name']
            ALL_TEACHERS.append(teacher_name)
            
            if teacher['Type'] == 'PE':
                PE_TEACHERS.append(teacher_name)
            elif teacher['Type'] == 'Core':
                team_key = f"team_{teacher['Team']}"
                if team_key not in TEACHERS:
                    TEACHERS[team_key] = {}
                TEACHERS[team_key][teacher['Subject']] = teacher_name
            elif teacher['Type'] == 'Literacy':
                # Handle literacy teachers that serve multiple teams
                # Convert to string first, then split
                team_str = str(teacher['Team'])
                teams_served = [int(t.strip()) for t in team_str.split(',')]
                for team_num in teams_served:
                    team_key = f"team_{team_num}"
                    if team_key not in TEACHERS:
                        TEACHERS[team_key] = {}
                    TEACHERS[team_key]['Literacy'] = teacher_name
        
        return {
            'ALL_PERIODS': ALL_PERIODS,
            'TEACHING_PERIODS': TEACHING_PERIODS,
            'CLASSES': CLASSES,
            'TEAM_MAPPING': TEAM_MAPPING,
            'TEAMS': TEAMS,
            'CORE_SUBJECTS': CORE_SUBJECTS,
            'TEACHERS': TEACHERS,
            'PE_TEACHERS': PE_TEACHERS,
            'ALL_TEACHERS': ALL_TEACHERS,
            'DAYS': list(ALL_PERIODS.keys()),
            'ACTIVITIES': ['Teaching', 'Prep', 'Team_Meeting', 'Discipline_Meeting', 'Advisory', 'Elective', 'Lunch']
        }
    
    def solve_scheduling_model(self, data, teachers_data):
        """Complete scheduling solver using Google Sheets data"""

        # Add status mapping for debugging
        status_names = {
            cp_model.OPTIMAL: "OPTIMAL",
            cp_model.FEASIBLE: "FEASIBLE", 
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.UNKNOWN: "UNKNOWN",
            cp_model.MODEL_INVALID: "MODEL_INVALID"
        }
        
        print("🔧 Building scheduling model...")
        
        # Extract data
        DAYS = data['DAYS']
        ALL_PERIODS = data['ALL_PERIODS']
        TEACHING_PERIODS = data['TEACHING_PERIODS']
        CLASSES = data['CLASSES']
        TEAMS = data['TEAMS']
        TEACHERS = data['TEACHERS']
        PE_TEACHERS = data['PE_TEACHERS']
        ALL_TEACHERS = data['ALL_TEACHERS']
        CORE_SUBJECTS = data['CORE_SUBJECTS']
        ACTIVITIES = data['ACTIVITIES']
        TEAM_MAPPING = data['TEAM_MAPPING']
        
        # ============================================================================
        # MODEL SETUP
        # ============================================================================
        
        model = cp_model.CpModel()
        
        # Decision Variables
        teacher_activity = {}
        for teacher in ALL_TEACHERS:
            teacher_activity[teacher] = {}
            for day in DAYS:
                teacher_activity[teacher][day] = {}
                for period in ALL_PERIODS[day]:
                    teacher_activity[teacher][day][period] = model.NewIntVar(
                        0, len(ACTIVITIES) - 1, 
                        f'{teacher}_{day}_P{period}_activity'
                    )
        
        teacher_class_assignment = {}
        for teacher in ALL_TEACHERS:
            teacher_class_assignment[teacher] = {}
            for class_name in CLASSES:
                teacher_class_assignment[teacher][class_name] = {}
                for day in DAYS:
                    teacher_class_assignment[teacher][class_name][day] = {}
                    for period in TEACHING_PERIODS[day]:
                        teacher_class_assignment[teacher][class_name][day][period] = \
                            model.NewBoolVar(
                                f'{teacher}_teaches_{class_name}_{day}_P{period}'
                            )
        
        # ============================================================================
        # BASIC CONSTRAINTS
        # ============================================================================
        
        print("Adding basic constraints...")
        
        # Lunch constraint
        for teacher in ALL_TEACHERS:
            for day in DAYS:
                if 3 in ALL_PERIODS[day]:
                    model.Add(teacher_activity[teacher][day][3] == ACTIVITIES.index('Lunch'))
        
        # Prep constraint
        for teacher in ALL_TEACHERS:
            for day in DAYS:
                daily_preps = []
                for period in TEACHING_PERIODS[day]:
                    prep_var = model.NewBoolVar(f'{teacher}_{day}_P{period}_is_prep')
                    model.Add(teacher_activity[teacher][day][period] == ACTIVITIES.index('Prep')).OnlyEnforceIf(prep_var)
                    model.Add(teacher_activity[teacher][day][period] != ACTIVITIES.index('Prep')).OnlyEnforceIf(prep_var.Not())
                    daily_preps.append(prep_var)
                model.Add(sum(daily_preps) == 1)
        
        # Teaching activity constraint
        for teacher in ALL_TEACHERS:
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    teaching_assignments = []
                    for class_name in CLASSES:
                        teaching_assignments.append(teacher_class_assignment[teacher][class_name][day][period])
                    
                    is_teaching = model.NewBoolVar(f'{teacher}_is_teaching_{day}_P{period}')
                    model.AddBoolOr(teaching_assignments).OnlyEnforceIf(is_teaching)
                    model.AddBoolAnd([var.Not() for var in teaching_assignments]).OnlyEnforceIf(is_teaching.Not())
                    
                    model.Add(
                        teacher_activity[teacher][day][period] == ACTIVITIES.index('Teaching')
                    ).OnlyEnforceIf(is_teaching)
        
        # One teacher per class per period
        for class_name in CLASSES:
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    class_teachers = []
                    for teacher in ALL_TEACHERS:
                        class_teachers.append(teacher_class_assignment[teacher][class_name][day][period])
                    model.Add(sum(class_teachers) <= 1)
        
        # ============================================================================
        # CORE SUBJECT CONSTRAINTS
        # ============================================================================
        
        print("Adding core subject constraints...")
        
        for team_num in range(1, 5):
            team_key = f'team_{team_num}'
            if team_key in TEACHERS:
                team_classes = TEAMS[team_num]
                
                for subject in CORE_SUBJECTS:
                    if subject in TEACHERS[team_key]:
                        teacher = TEACHERS[team_key][subject]
                        for class_name in team_classes:
                            weekly_teaching = []
                            for day in DAYS:
                                for period in TEACHING_PERIODS[day]:
                                    weekly_teaching.append(
                                        teacher_class_assignment[teacher][class_name][day][period]
                                    )
                            model.Add(sum(weekly_teaching) == 4)
        
        # ============================================================================
        # LITERACY CONSTRAINTS
        # ============================================================================

        print("Adding literacy constraints...")

        # Find literacy teachers and their classes - FIXED VERSION
        literacy_teachers = {}
        for teacher_data in teachers_data:
            teacher_name = teacher_data['Teacher Name']
            if teacher_data['Type'] == 'Literacy':
                if teacher_name not in literacy_teachers:
                    literacy_teachers[teacher_name] = []
                # Convert to string and split
                team_str = str(teacher_data['Team'])
                teams_served = [int(t.strip()) for t in team_str.split(',')]
                for team_num in teams_served:
                    if team_num in TEAMS:  # Add safety check
                        literacy_teachers[teacher_name].extend(TEAMS[team_num])

        print(f"Literacy teachers found: {literacy_teachers}")

        for literacy_teacher, classes in literacy_teachers.items():
            for class_name in classes:
                weekly_literacy = []
                for day in DAYS:
                    for period in TEACHING_PERIODS[day]:
                        weekly_literacy.append(
                            teacher_class_assignment[literacy_teacher][class_name][day][period]
                        )
                model.Add(sum(weekly_literacy) == 2)
        
        # ============================================================================
        # PE CONSTRAINTS (SIMPLIFIED)
        # ============================================================================
        
        print("Adding PE constraints...")
        
        # Each team gets exactly 3 PE periods per week  
        for team_num in range(1, 5):
            team_classes = TEAMS[team_num]
            
            weekly_pe = []
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    team_has_pe = model.NewBoolVar(f'team_{team_num}_has_PE_{day}_P{period}')
                    
                    pe_teaching_vars = []
                    for pe_teacher in PE_TEACHERS:
                        for class_name in team_classes:
                            pe_teaching_vars.append(teacher_class_assignment[pe_teacher][class_name][day][period])
                    
                    model.AddBoolOr(pe_teaching_vars).OnlyEnforceIf(team_has_pe)
                    model.AddBoolAnd([var.Not() for var in pe_teaching_vars]).OnlyEnforceIf(team_has_pe.Not())
                    
                    weekly_pe.append(team_has_pe)
            
            model.Add(sum(weekly_pe) == 3)
        
        # PE teachers can only teach one team at a time
        for day in DAYS:
            for period in TEACHING_PERIODS[day]:
                pe_assignments = []
                for pe_teacher in PE_TEACHERS:
                    for class_name in CLASSES:
                        pe_assignments.append(teacher_class_assignment[pe_teacher][class_name][day][period])
                
                model.Add(sum(pe_assignments) <= 4)
        
        # ============================================================================
        # TEAM MEETING CONSTRAINTS
        # ============================================================================
        
        print("Adding team meeting constraints...")
        
        team_meeting_schedule = {}
        for team_num in range(1, 5):
            team_meeting_schedule[team_num] = {}
            for day in DAYS:
                team_meeting_schedule[team_num][day] = {}
                for period in TEACHING_PERIODS[day]:
                    team_meeting_schedule[team_num][day][period] = model.NewBoolVar(
                        f'team_{team_num}_meeting_{day}_P{period}'
                    )
        
        # Each team has exactly 2 team meetings per week
        for team_num in range(1, 5):
            weekly_meetings = []
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    weekly_meetings.append(team_meeting_schedule[team_num][day][period])
            model.Add(sum(weekly_meetings) == 2)
        
        # Team meetings can only happen when PE is teaching that team
        for team_num in range(1, 5):
            team_classes = TEAMS[team_num]
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    pe_teaching_team = []
                    for pe_teacher in PE_TEACHERS:
                        for class_name in team_classes:
                            pe_teaching_team.append(teacher_class_assignment[pe_teacher][class_name][day][period])
                    
                    team_has_pe = model.NewBoolVar(f'team_{team_num}_has_PE_for_meeting_{day}_P{period}')
                    model.AddBoolOr(pe_teaching_team).OnlyEnforceIf(team_has_pe)
                    model.AddBoolAnd([var.Not() for var in pe_teaching_team]).OnlyEnforceIf(team_has_pe.Not())
                    
                    model.Add(team_meeting_schedule[team_num][day][period] <= team_has_pe)
        
        # When team has meeting, core teachers participate
        for team_num in range(1, 5):
            team_key = f'team_{team_num}'
            if team_key in TEACHERS:
                core_teachers = [TEACHERS[team_key][subject] for subject in CORE_SUBJECTS if subject in TEACHERS[team_key]]
                
                for day in DAYS:
                    for period in TEACHING_PERIODS[day]:
                        for teacher in core_teachers:
                            model.Add(
                                teacher_activity[teacher][day][period] == ACTIVITIES.index('Team_Meeting')
                            ).OnlyEnforceIf(team_meeting_schedule[team_num][day][period])
        
        # ============================================================================
        # DISCIPLINE MEETING CONSTRAINTS
        # ============================================================================
        
        print("Adding discipline meeting constraints...")
        
        discipline_schedule = {}
        for subject in CORE_SUBJECTS:
            discipline_schedule[subject] = {}
            for day in DAYS:
                discipline_schedule[subject][day] = {}
                for period in TEACHING_PERIODS[day]:
                    discipline_schedule[subject][day][period] = model.NewBoolVar(
                        f'{subject}_discipline_{day}_P{period}'
                    )
        
        # Each subject has exactly 1 discipline meeting per week
        for subject in CORE_SUBJECTS:
            weekly_discipline = []
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    weekly_discipline.append(discipline_schedule[subject][day][period])
            model.Add(sum(weekly_discipline) == 1)
        
        # When subject has discipline meeting, all teachers of that subject participate
        for subject in CORE_SUBJECTS:
            subject_teachers = []
            for i in range(1, 5):
                team_key = f'team_{i}'
                if team_key in TEACHERS and subject in TEACHERS[team_key]:
                    subject_teachers.append(TEACHERS[team_key][subject])
            
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    for teacher in subject_teachers:
                        model.Add(
                            teacher_activity[teacher][day][period] == ACTIVITIES.index('Discipline_Meeting')
                        ).OnlyEnforceIf(discipline_schedule[subject][day][period])
        
        # ============================================================================
        # ADVISORY CONSTRAINTS
        # ============================================================================
        
        print("Adding advisory constraints...")
        
        team_advisory_schedule = {}
        for team_num in range(1, 5):
            team_advisory_schedule[team_num] = {}
            for day in DAYS:
                team_advisory_schedule[team_num][day] = {}
                for period in TEACHING_PERIODS[day]:
                    team_advisory_schedule[team_num][day][period] = model.NewBoolVar(
                        f'team_{team_num}_advisory_{day}_P{period}'
                    )
        
        # Each team gets exactly 2 advisory periods per week
        for team_num in range(1, 5):
            weekly_advisory = []
            for day in DAYS:
                for period in TEACHING_PERIODS[day]:
                    weekly_advisory.append(team_advisory_schedule[team_num][day][period])
            model.Add(sum(weekly_advisory) == 2)
        
        # When team has advisory, all team teachers participate
        for team_num in range(1, 5):
            team_key = f'team_{team_num}'
            if team_key in TEACHERS:
                team_teachers = [TEACHERS[team_key][subject] for subject in CORE_SUBJECTS if subject in TEACHERS[team_key]]
                if 'Literacy' in TEACHERS[team_key]:
                    team_teachers.append(TEACHERS[team_key]['Literacy'])
                
                for day in DAYS:
                    for period in TEACHING_PERIODS[day]:
                        for teacher in team_teachers:
                            model.Add(
                                teacher_activity[teacher][day][period] == ACTIVITIES.index('Advisory')
                            ).OnlyEnforceIf(team_advisory_schedule[team_num][day][period])
        
        # ============================================================================
        # ELECTIVE CONSTRAINTS
        # ============================================================================
        
        print("Adding elective constraints...")
        
        elective_schedule = {}
        for day in DAYS:
            elective_schedule[day] = {}
            for period in TEACHING_PERIODS[day]:
                elective_schedule[day][period] = model.NewBoolVar(f'school_elective_{day}_P{period}')
        
        # Exactly 2 elective periods per week for the whole school
        weekly_electives = []
        for day in DAYS:
            for period in TEACHING_PERIODS[day]:
                weekly_electives.append(elective_schedule[day][period])
        model.Add(sum(weekly_electives) == 2)
        
        # ============================================================================
        # SOLVER
        # ============================================================================

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 300.0  # Increase time limit
        solver.parameters.log_search_progress = True   # Enable logging

        print("🔧 Solving model...")
        start_time = time.time()
        status = solver.Solve(model)
        solve_time = time.time() - start_time

        status_name = status_names.get(status, f"UNKNOWN_STATUS_{status}")
        print(f"Solver status: {status_name} ({status})")

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            quality = "Optimal" if status == cp_model.OPTIMAL else "Feasible"
            print(f"✅ {quality} solution found in {solve_time:.2f} seconds!")
            
            return {
                'status': status,
                'solver': solver,
                'model': model,
                'data': data,
                'solve_time': solve_time,
                'quality': quality,
                'teacher_activity': teacher_activity,
                'teacher_class_assignment': teacher_class_assignment,
                'team_advisory_schedule': team_advisory_schedule,
                'elective_schedule': elective_schedule
            }
        else:
            print(f"❌ No solution found. Status: {status_name}")
            print(f"Solve time: {solve_time:.2f} seconds")
            
            # Add some basic constraint debugging
            print("\n🔍 Debugging info:")
            print(f"Total teachers: {len(ALL_TEACHERS)}")
            print(f"Total classes: {len(CLASSES)}")
            print(f"Teaching periods per day: {[len(TEACHING_PERIODS[day]) for day in DAYS]}")
            print(f"Core subjects: {CORE_SUBJECTS}")
            print(f"PE teachers: {PE_TEACHERS}")
            
            return None
    
    def convert_solution_to_sheets_format(self, solution, data):
        """Convert solver solution to Google Sheets format"""
        
        solver = solution['solver']
        teacher_activity = solution['teacher_activity']
        teacher_class_assignment = solution['teacher_class_assignment']
        team_advisory_schedule = solution['team_advisory_schedule']
        elective_schedule = solution['elective_schedule']
        
        DAYS = data['DAYS']
        ALL_PERIODS = data['ALL_PERIODS']  # This has the correct periods per day
        TEACHING_PERIODS = data['TEACHING_PERIODS']
        CLASSES = data['CLASSES']
        ALL_TEACHERS = data['ALL_TEACHERS']
        ACTIVITIES = data['ACTIVITIES']
        TEACHERS = data['TEACHERS']
        PE_TEACHERS = data['PE_TEACHERS']
        TEAM_MAPPING = data['TEAM_MAPPING']
        
        # Convert teacher schedules
        teacher_schedules = {}
        for teacher in ALL_TEACHERS:
            teacher_schedules[teacher] = {}
            for day in DAYS:
                teacher_schedules[teacher][day] = {}
                # Use the correct periods for each day
                for period in ALL_PERIODS[day]:  # This will give us the right periods per day
                    activity_idx = solver.Value(teacher_activity[teacher][day][period])
                    activity = ACTIVITIES[activity_idx]
                    
                    # Find classes being taught
                    teaching_classes = []
                    if period in TEACHING_PERIODS[day]:
                        for class_name in CLASSES:
                            if solver.Value(teacher_class_assignment[teacher][class_name][day][period]) == 1:
                                teaching_classes.append(class_name)
                    
                    # Determine subject
                    subject = ""
                    if activity == 'Teaching' and teaching_classes:
                        # Find subject based on teacher
                        for team_key, team_teachers in TEACHERS.items():
                            for subj, t_name in team_teachers.items():
                                if t_name == teacher:
                                    subject = subj
                                    break
                        if teacher in PE_TEACHERS:
                            subject = "PE"
                    
                    teacher_schedules[teacher][day][period] = {
                        'activity': activity,
                        'classes': teaching_classes,
                        'subject': subject,
                        'notes': ''
                    }
        
        # Convert class schedules
        class_schedules = {}
        for class_name in CLASSES:
            class_schedules[class_name] = {}
            for day in DAYS:
                class_schedules[class_name][day] = {}
                # Use the correct periods for each day
                for period in ALL_PERIODS[day]:  # This will give us the right periods per day
                    if period == 3:  # Lunch
                        class_schedules[class_name][day][period] = {
                            'subject': 'Lunch',
                            'teacher': '',
                            'activity_type': 'Lunch',
                            'team': TEAM_MAPPING[class_name]
                        }
                    else:
                        # Find teacher teaching this class
                        teaching_teacher = None
                        if period in TEACHING_PERIODS[day]:
                            for teacher in ALL_TEACHERS:
                                if solver.Value(teacher_class_assignment[teacher][class_name][day][period]) == 1:
                                    teaching_teacher = teacher
                                    break
                        
                        if teaching_teacher:
                            # Determine subject
                            subject = "Unknown"
                            for team_key, team_teachers in TEACHERS.items():
                                for subj, t_name in team_teachers.items():
                                    if t_name == teaching_teacher:
                                        subject = subj
                                        break
                            if teaching_teacher in PE_TEACHERS:
                                subject = "PE"
                            
                            class_schedules[class_name][day][period] = {
                                'subject': subject,
                                'teacher': teaching_teacher,
                                'activity_type': 'Teaching',
                                'team': TEAM_MAPPING[class_name]
                            }
                        else:
                            # Check for school-wide activities
                            if period in TEACHING_PERIODS[day]:
                                if solver.Value(elective_schedule[day][period]) == 1:
                                    activity_type = "Elective"
                                elif solver.Value(team_advisory_schedule[TEAM_MAPPING[class_name]][day][period]) == 1:
                                    activity_type = "Advisory"
                                else:
                                    activity_type = "Free"
                            else:
                                activity_type = "Free"
                            
                            class_schedules[class_name][day][period] = {
                                'subject': activity_type,
                                'teacher': '',
                                'activity_type': activity_type,
                                'team': TEAM_MAPPING[class_name]
                            }
        
        return teacher_schedules, class_schedules
    
    def run_solver(self):
        """Run the complete scheduling solver with Google Sheets data"""
        try:
            # Update status
            self.sheets.update_status("Loading data...")
            
            # Load data from sheets
            config, teachers_data, classes_data = self.load_data_from_sheets()
            
            # Convert to model format
            model_data = self.convert_sheets_data_to_model_format(config, teachers_data, classes_data)
            
            # Update status
            self.sheets.update_status("Building model...")
            
            # Build and solve model
            solution = self.solve_scheduling_model(model_data, teachers_data)
            
            if solution:
                # Update status
                self.sheets.update_status("Writing results...")
                
                # Convert solution to sheets format and write
                teacher_schedules, class_schedules = self.convert_solution_to_sheets_format(solution, model_data)

                # Write both formats
                self.sheets.write_teacher_schedules(teacher_schedules)
                self.sheets.write_class_schedules(class_schedules)

                # Try grid formats with better error handling
                try:
                    self.sheets.write_teacher_schedules_grid(teacher_schedules)
                except Exception as e:
                    print(f"⚠️ Grid format failed, continuing with list format: {e}")

                try:
                    self.sheets.write_class_schedules_grid(class_schedules)
                except Exception as e:
                    print(f"⚠️ Class grid format failed, continuing with list format: {e}")
                
                # Update final status
                solve_time = solution.get('solve_time', 0)
                quality = solution.get('quality', 'Unknown')
                self.sheets.update_status(
                    "Complete ✅", 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    solve_time,
                    quality
                )
                
                print("🎉 Scheduling complete! Check the Teacher_Schedules and Class_Schedules sheets.")
                return True
            else:
                self.sheets.update_status("Failed - No solution found ❌")
                return False
                
        except Exception as e:
            self.sheets.update_status(f"Error: {str(e)} ❌")
            print(f"❌ Error in solver: {e}")
            return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    # Configuration - UPDATE THESE PATHS
    CREDENTIALS_FILE = "/Users/javiertello/Code/python/international-highschool-scheduler/school-scheduler-credentials.json"
    SPREADSHEET_NAME = "Testing Schedule Grid Sheets"
    
    try:
        print("🚀 Starting School Scheduler with Google Sheets Integration")
        
        # Initialize scheduler
        scheduler = GoogleSheetsScheduler(CREDENTIALS_FILE, SPREADSHEET_NAME)
        
        # Setup sheets (run this once to create template sheets)
        print("📋 Setting up Google Sheets...")
        scheduler.setup_sheets()
        
        # Run solver
        print("🔧 Running scheduler...")
        success = scheduler.run_solver()
        
        if success:
            print("✅ Scheduling completed successfully!")
            print(f"📊 View results at: {scheduler.sheets.spreadsheet.url}")
        else:
            print("❌ Scheduling failed.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()