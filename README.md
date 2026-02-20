# 🏏 NPL Fantasy League – DBMS Project

NPL Fantasy League is a full-stack web application developed as part of the THA079BCT batch syllabus for the DBMS subject.

This project demonstrates practical implementation of Database Management Systems concepts using ORM only, as required by the course guidelines.

The system allows users to create fantasy cricket teams for NPL matches, manage players, and compete on a leaderboard based on performance scores.

---

## Project Objective

The main objective of this project is:
- To build a interactive web application for NPL fantasy league.
- To design a well structured database for NPL fantasy league using PostreSQL.

---

## Tech Stack

### Frontend
- React.js

### Backend
- Django ORM

### Database
- PostgreSQL

### Host
- Vercel (Frontend and Backend)
- Supabase (Database)

---

## Features

### 👤 User Features
- User Registration
- User Login / Authentication
- Create Fantasy Team for each match
- Select players from available teams
- View match-wise player list
- View Leaderboard rankings
- Track fantasy score

### 🛠️ Admin Features
- Add Teams
- Edit Teams
- Remove Teams
- Add Players
- Edit Players
- Remove Players
- Add Matches
- Edit Matches
- Remove Matches

> All admin operations are implemented using Django ORM (CRUD functionality).

---

## Database Tables Scheme
![Database Schema](NPLdatabaseSchema.png)


Tables:
- users
- teams
- players
- matches
- match_players
- players_stats
- fantasy_teams
- fantasy_team_players
- leaderboard

> The schema includes proper foreign key relationships and constraints to maintain data integrity.

---

## Fantasy Team Selection Rules

The following rules apply when selecting players for a fantasy team:

1. A user can create only **one fantasy team per match**.
2. A fantasy team must contain exactly **7 players**.
3. Players must be selected only from the two teams playing that match.
4. Team composition rules:
   - Maximum of 4 ALLROUNDER
   - Maximum of 4 BATTER
   - Maximum of 4 BOWLER
5. Maximum 4 players can be selected from a single real-life team.
6. A captain and vice-captain must be selected:
   - Captain earns 2x points
   - Vice-captain earns 1.5x points
7. Cost of the Teams **should not exceed 60**

---

## 📈 Scoring Mechanism

The fantasy points calculation is performed using match-based player statistics.
All calculations are derived dynamically from player performance using backend logic.

### Base Points Formula

Each player's **base points** are calculated using the following formula:

Base Points =  
(runs ÷ 10)  
+ (run_rate ÷ 100)  
+ (10 ÷ economy_rate, if economy_rate > 0)  
+ (wickets × 2)  
+ (sixes)  
+ (fours × 0.5)  
+ (catches)

> All null values are handled safely using `COALESCE` to prevent calculation errors.

---

### Captain & Vice-Captain Multiplier

After calculating base points:

- **Captain** → Final Points = Base Points × 2  
- **Vice Captain** → Final Points = Base Points × 1.5  
- **Other Players** → Final Points = Base Points  

> Final points are rounded to 2 decimal places.

---

### Total Fantasy Team Score

- A team's total score is the sum of all 7 players' final points.
- The leaderboard ranks fantasy teams based on total points.

---

## DBMS Concepts Used

- Relational Model Design
- Primary and Foreign Keys
- Many-to-Many Relationships
- ORM Query Filtering
- Aggregation & Annotation
- Data Integrity Constraints
- Ranking System using computed fields

---


## 🛠️ Installation Guide

### 1 Clone the Repository

```bash
git clone https://github.com/hang-kulung/NPL_DATABASE_porject.git
cd NPL_DATABASE_porject
```

### 2 Backend Setup
```bash
cd backend
pip install -r requirements.txt
cd npl_fatasy
python manage.py migrate
python manage.py runserver
```

### 3 Frontend Setup
```bash
cd frontend/npl_frontend
npm install
npm run dev
```

## Developed By
- [Ninamhang Kulung](https://github.com/hang-kulung) (THA079BCT023)
- [Prabesh Babu Adhikari](https://github.com/prabesh130) (THA079BCT026)
- [Suprem Khatri](https://github.com/supremkhatri) (THA079BCT047)    

## Links
- Frontend: https://npl-fantasy.vercel.app/
- Backend: https://npl-fantasy-backend.vercel.app/
- Demo Video: https://drive.google.com/file/d/1oZxZV0uD0ccnebHVLHkKLeQ9mQBv1U6E/view?usp=sharing



