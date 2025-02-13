
![Logo](https://i.ibb.co.com/1tmQBn2K/Whats-App-Image-2025-02-13-at-2-11-59-PM.jpg)


## Authors

- FullStract: [@mdjobayerarafat](https://github.com/mdjobayerarafat)

- Frontend: [@mdhabibullahmahmudncs13](https://github.com/mdhabibullahmahmudncs13)
## Badges


[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)]()
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)]()


# A Education Exam System for A Event [Name: Dig The Data 3.0]

This project is a **Event And Exam Management System** designed for educational or competitive environments, such as university departments, hackathons, or online quiz competitions. It allows teams to participate in quizzes, answer questions, request hints, and track their scores. The system is built using **Django**, a Python web framework, and includes features for user authentication, team management, quiz administration, and score tracking.

---

### **Key Features**
1. **User Authentication and Team Management**:
   - Users can register and log in.
   - Each user is associated with a team, and teams can have multiple members.
   - Teams can be created, and team members can be added with details like name, position, class ID, WhatsApp number, email, and department.

2. **Quiz Management**:
   - Admins can create quizzes and mark them as active or inactive.
   - Questions can be added to quizzes, with options for common questions (shared across teams) or unique questions (specific to a team).
   - Questions can include links (e.g., to external resources) and have correct answers.

3. **Answer Submission and Scoring**:
   - Teams can submit answers to questions.
   - Answers are automatically checked against the correct answer, and scores are calculated.
   - Common questions are worth 10 points, while unique questions are worth 20 points.

4. **Hint System**:
   - Teams can request hints for questions.
   - Admins can fulfill hint requests and notify teams.

5. **Score Tracking**:
   - Scores for each team are tracked and displayed.
   - Admins can view and manage scores.

6. **Site Settings**:
   - Admins can control whether registration and login are open or closed.

7. **User and Team Profiles**:
   - Users have profiles with personal details.
   - Teams have profiles with team members and their details.

---

### **Who is this for?**
This project is designed for:
- **Educational Institutions**: Departments can use it to conduct quizzes for students.
- **Competitions**: Organizers can use it to manage online quizzes for participants.
- **Hackathons**: Teams can use it to answer questions and track their progress.
- **Admins**: They can manage quizzes, questions, hints, and scores.

---

### **Models Overview**
1. **Team**: Represents a team participating in the quiz.
2. **Quiz**: Represents a quiz with questions.
3. **Question**: Represents a question in a quiz, with options for common or unique questions.
4. **TeamQuestion**: Links a question to a team, tracking whether hints were used or the question was answered.
5. **Answer**: Represents an answer submitted by a team, with automatic scoring.
6. **Score**: Tracks the total score for each team.
7. **TeamUser**: Represents a member of a team, with personal details.
8. **Hint**: Represents a hint for a question.
9. **HintRequest**: Tracks hint requests from teams.
10. **HintNotification**: Notifies users about hint requests.
11. **UserPerson**: Represents a user with personal details and authentication.
12. **SiteSettings**: Controls site-wide settings like registration and login status.

---

### **How It Works**
1. **Admins**:
   - Create quizzes and questions.
   - Activate or deactivate quizzes.
   - Fulfill hint requests and notify teams.
   - Manage site settings.

2. **Teams**:
   - Register and log in.
   - Participate in active quizzes.
   - Submit answers to questions.
   - Request hints for questions.
   - View their scores.

3. **Users**:
   - Register and join teams.
   - Update their profiles.
   - Participate in quizzes as part of a team.

---

### **Potential Improvements**
1. **Frontend Development**: Build a user-friendly interface for teams and admins.
2. **Real-Time Updates**: Use WebSockets or Django Channels for real-time notifications (e.g., when a hint is fulfilled).
3. **Advanced Scoring**: Add bonus points, penalties, or time-based scoring.
4. **Analytics**: Add dashboards for admins to analyze quiz performance.
5. **Email Notifications**: Send email notifications for hint requests or score updates.

---

This project is a robust foundation for managing quizzes and competitions, with room for customization and expansion based on specific needs.


## Tech Stack

**Client:** Html, Css, JavaScript as Website

**Server:** Python, Django, Django Rest Framework


## Installation

Install my-project with npm

```bash
  sudo pip3 install virtualenv
```

```bash
  mkdir ~/projectdir
  cd ~/projectdir
```
```bash
  virtualenv env

```
```bash
  source env/bin/activate

```
```bash
 pip install -r requirements.txt
```
```bash
  python manage.py makemigrations
```
```bash
  python manage.py migrate
```
```bash
  python manage.py createsuperuser
```
```bash
  python manage.py runserver
```
## 🛠 Skills
Javascript, HTML, CSS...


## Used By

This project is used by the following companies:

- NIter Computer Club (NCC)


## Screenshots

![App Screenshot](https://i.ibb.co.com/7dDdVmsF/Screenshot-2025-02-13-13-49-11.png)
![App Screenshot](https://i.ibb.co.com/HTsfWmFh/Screenshot-2025-02-13-13-49-35.png)
![App Screenshot](https://i.ibb.co.com/sprZzHbj/Screenshot-2025-02-13-13-50-15.png)
![App Screenshot](https://i.ibb.co.com/fYKtLJf2/Screenshot-2025-02-13-13-50-32.png)




