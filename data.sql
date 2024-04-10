DROP DATABASE IF EXISTS shore_tour_invite;
CREATE DATABASE shore_tour_invite;
\c shore_tour_invite

CREATE TABLE golfers (
    golfer_id SERIAL PRIMARY KEY,
    golfer_name TEXT,
    username TEXT,
    email TEXT,
    GHIN TEXT,
    handicap FLOAT
);

CREATE TABLE clubs (
    club_id SERIAL PRIMARY KEY,
    club_name TEXT,
    city TEXT,
    state TEXT
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name TEXT,
    club_id INT REFERENCES clubs(club_id)
);

CREATE TABLE courses_holes(
    course_id INT,
    number INT,
    par INT,
    handicap INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE tees (
    tee_id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(course_id),
    tee_name TEXT,
    slope INT,
    rating FLOAT,
    total_yards INT
);

CREATE TABLE tees_holes (
    tee_id INT,
    hole_number INT,
    yards INT,
    FOREIGN KEY (tee_id) REFERENCES tees(tee_id)
);

CREATE TABLE golfer_rounds (
    golfer_round_id SERIAL PRIMARY KEY,
    golfer_id INT REFERENCES golfers(golfer_id),
    round_id INT,
    total_strokes INT,
    total_holes INT
);

CREATE TABLE round (
    round_id SERIAL PRIMARY KEY,
    club_id INT REFERENCES clubs(club_id),
    date_of_round DATE
);

CREATE TABLE round_course (
    round_course_id SERIAL PRIMARY KEY,
    round_id INT REFERENCES round(round_id),
    course_id INT REFERENCES courses(course_id),
    sequence_number INT,
    tee_id INT REFERENCES tees(tee_id)
);

CREATE TABLE round_strokes (
    golfer_id INT,
    round_course_id INT REFERENCES round_course(round_course_id),
    hole_number INT,
    strokes INT,
    fairway_hit BOOLEAN,
    green_in_reg BOOLEAN,
    number_of_putts INT,
    bunker_shot BOOLEAN,
    FOREIGN KEY (golfer_id) REFERENCES golfers(golfer_id)
);


CREATE TABLE leaderboards (
    leaderboard_id SERIAL PRIMARY KEY,
    tournament_id INT REFERENCES tournaments(tournament_id),
    golfer_id INT REFERENCES golfers(golfer_id),
    holes_played INT,
    position INT
);

CREATE TABLE tournaments (
    tournament_id SERIAL PRIMARY KEY,
    country TEXT,
    course TEXT,
    course_par TEXT,
    end_date TEXT,
    live_details JSONB,
    name TEXT,
    start_date TEXT,
    timezone TEXT,
    tour_id TEXT,
    type TEXT,
    results_id INT REFERENCES Results(results_id)
);

CREATE TABLE results (
    results_id SERIAL PRIMARY KEY,
    leaderboard JSONB,
    tournament JSONB
);
