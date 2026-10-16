# Smart Student Focus Monitoring (SSFM)

A Flask web app that helps instructors see how focused a class is during a lecture. A webcam feed is analysed in real time with computer vision, each detected face gets a live focus score, and sessions are saved so instructors can review reports and history later.

Graduation project at Yarmouk University (team project). **My role:** full-stack web application - Flask backend, SQLite database, instructor sign-up/sign-in, live monitoring page, lecture reports and history dashboards - and integrating the team's computer-vision module into it.

## Features

- **Instructor accounts:** sign up / sign in with hashed passwords (Werkzeug).
- **Courses and sections:** each instructor sees their own courses and starts monitoring a section.
- **Live monitoring:** webcam stream with a box and focus percentage per detected face (up to 5 faces), plus a class average.
- **Focus scoring:** built from eye openness (eye aspect ratio from MediaPipe Face Mesh landmarks) and head tilt - a score drops when eyes stay closed or the head stays turned away, and recovers gradually when attention returns.
- **Audio alert:** a sound plays when the class average falls below 50%.
- **Random student highlight:** a button picks one detected student at random.
- **Reports and history:** each session is saved (average focus, duration, per-student scores) and can be reviewed per lecture and over time.

## Background and goals

Instructors usually judge attention by eye, which is subjective and hard to do for a whole room, especially in long lectures where students get tired or bored. This project explores an objective, real-time alternative: use a camera and computer vision to estimate how focused each student and the whole class are, give the instructor live feedback, and keep a history for later review.

Goals:
1. Estimate focus per student and for the class in real time.
2. Give the instructor an interactive dashboard with individual and class-level focus.
3. Raise an alert when class attention drops.
4. Store past sessions and show detailed reports per lecture.

## Requirements (summary)

**Functional:** instructor sign-up and login; list of the instructor's courses; start and stop a monitoring session for a chosen course section; live focus percentages per student and for the class; audio alert below a threshold; save a session with "Stop and Save"; history of past lectures and a detailed report for each.

**Non-functional:** near real-time processing, a simple interface, protected credentials, and a structure that can grow to more courses and students.

## Architecture

The app is a single Flask server that talks to the browser over HTTP, reads the webcam with OpenCV, scores each face with MediaPipe, and stores finished sessions in SQLite.

```mermaid
flowchart LR
    Browser["Instructor's browser"] -->|"HTTP pages and fetch calls"| Flask["Flask app (app.py)"]
    Camera["Webcam"] --> CV["OpenCV frames + MediaPipe face landmarks"]
    CV --> Score["Per-face focus scoring"]
    Score --> Flask
    Flask -->|"/video_feed (MJPEG stream)"| Browser
    Browser -->|"polls /focus-data"| Flask
    Score --> Alert["Pygame audio alert"]
    Flask <-->|"sessions, courses, history"| DB[("SQLite database")]
```

How a monitoring session works:

1. The instructor signs in, picks a course section, and opens the monitoring page.
2. The page calls `/start_camera`, then shows the annotated video from `/video_feed`.
3. For every frame, MediaPipe finds up to 5 faces, and the app updates each face's focus score from eye openness and head tilt. Scores are kept in memory behind a lock because the video generator and the web routes run on different threads.
4. The page polls `/focus-data` to update the per-student and class-average numbers. If the class average drops below the threshold, an alert sound plays.
5. On "Stop and Save", the page posts the results to `/save_session`, which writes a row to `sessions` and one row per student to `student_focus_data`.
6. History and report pages read those tables back for each section.

The analysis-phase diagrams (use case, context and entity-relationship) are in [`docs/diagrams`](docs/diagrams).

### Routes

| Route | Method | What it does |
|---|---|---|
| `/` | GET | Monitoring page |
| `/f_page` | GET | Landing page |
| `/signup` | GET, POST | Create an instructor account |
| `/signin` | GET, POST | Sign in (password checked against the stored hash) |
| `/logout` | GET | End the session |
| `/courses` | GET | List the signed-in instructor's courses and sections |
| `/monitor/<section_id>` | GET | Monitoring page for one course section |
| `/start_camera` | GET | Turn the camera and analysis on |
| `/stop_camera` | GET | Turn the camera and analysis off |
| `/video_feed` | GET | Live annotated video as an MJPEG stream |
| `/focus-data` | GET | JSON with each student's focus score and the class average |
| `/highlight_random` | GET | Pick a random detected student and highlight them |
| `/save_session` | POST | Save the session and per-student scores to the database |
| `/history/<section_id>` | GET | Past sessions for a section |
| `/last-report?id=` | GET | Report page for the session that was just saved |
| `/report-page?id=` | GET | Detailed report for one past lecture |

### Database

SQLite with six tables: `instructors`, `courses`, `sections` (links a course to an instructor), `students`, `sessions` (average focus, duration and timestamp per lecture) and `student_focus_data` (focus score per student per session). See `database.py` for the schema.

## Tech stack

Python, Flask, SQLite, OpenCV, MediaPipe, NumPy, Pygame; HTML/CSS/JavaScript front end.

## Run it locally

You need Python 3 and a webcam.

```bash
pip install -r requirements.txt
python database.py          # creates smart_focus.db with the schema
python seed_demo_data.py    # adds a demo instructor, courses and fake students
python app.py
```

Open http://127.0.0.1:5000 and sign in with the demo account: `demo@example.com` / `demo123`.

Optional environment variables: `SECRET_KEY` (Flask session key - set it for anything beyond a local demo) and `FLASK_DEBUG=1`.

## Project structure

```
app.py               Flask app, video stream, focus scoring, routes
database.py          SQLite schema (instructors, courses, sections, students, sessions, focus data)
seed_demo_data.py    Demo data (fake instructor and students)
templates/           HTML pages
static/              Logo images and alert sound
docs/diagrams/       Use case, context and ERD diagrams from the analysis phase
```

## Privacy

Video is processed live and frames are not saved by the app. The repository contains no real student or instructor data - the demo database is created from fake data by `seed_demo_data.py`.

## Limitations

- Focus is estimated from face landmarks only (eye openness and head pose), so it is a rough indicator, not a measure of real attention. The original design also considered facial expressions and audio interaction, which are not part of this implementation.
- Uses one webcam and is designed for a small group of visible faces.
- Student identities in the demo are placeholders; there is no face recognition.
- Basic authentication only (no CSRF protection or password reset) - not production-ready.
