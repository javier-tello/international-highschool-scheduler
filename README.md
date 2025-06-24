# School Scheduling System

## Project Overview

A school scheduling system using Python OR-Tools CP-SAT solver with Google Sheets integration. The system schedules 24 teachers across 16 classes with complex constraint requirements and produces feasible, optimal solutions.

## School Structure

- 24 Teachers: 20 core (5 subjects × 4 teams), 2 PE, 2 literacy
- 16 Classes: A-P, organized into 4 teams
	- Team 1: A, B, C, D
	- Team 2: E, F, G, H
	- Team 3: I, J, K, L
	- Team 4: M, N, O, P
- 5 Core Subjects: ELA, SS, Science, Math, Arts
- Time Structure: 34 periods/week (Mon:7, Tue:7, Wed:6, Thu:7, Fri:7), Period 3 = lunch

## Core Academic Constraints:

- Core subjects: 4 periods/week per class per subject
- Arts: 4 periods/week per class (stakeholder confirmed - same as other core subjects)
- PE: 3 periods/week per team (team-based, all 4 classes together)
- Literacy: 2 periods/week per class
- No repeat classes same day (except PE)

## Teacher Assignment Rules:

- Core teachers: Can ONLY teach their assigned team's classes
- Literacy teachers:
	- Literacy_T1 → Classes A-H (Teams 1&2)
	- Literacy_T2 → Classes I-P (Teams 3&4)
- PE teachers: Can teach any team when scheduled

## Meeting Constraints:

### Team Meetings

- Frequency: 2/week per team
- Participants: ONLY core teachers (ELA, SS, Science, Math, Arts)
- Exclusions: PE and literacy teachers do NOT participate
- Timing: When PE is teaching that team
- Non-consecutive days

### Advisory

- Frequency: 2/week per team
- Participants: Core teachers + literacy teachers (NO PE teachers)
- Synchronization: All teachers in same team have Advisory at same periods
- Literacy participation: With their served teams only
- No consecutive days for literacy teachers

### Discipline Meetings

- Frequency: 1/week per subject (5 core subjects + 1 literacy)
- Participants: All teachers of same subject (synchronized)
- Exclusions: PE teachers do NOT participate in discipline meetings
- Scheduling: Only when no subject teachers are teaching
- Limit: At most 1 discipline meeting per period

## Elective Constraints:

- Frequency: 2 periods/week school-wide
- Must be on different days
- Synchronization: Entire school has electives at same 2 periods
- PE teachers get "Extra Prep" during electives

## Other Constraints:

- Daily prep: Exactly 1 prep period per day per teacher
- Lunch: Period 3 fixed for all
- PE teacher load: 15-25 periods/week
- 4-in-a-row prevention (accounting for lunch break)
