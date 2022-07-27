# Tech Topics Quiz App

### Project Proposal

## Overview

A quiz app to test your technical knowledge independently or with a study group. The quiz questions will come from the [QuizAPI](https://quizapi.io/docs/1.0/overview). Users will be able to create accounts and study groups to challenge themselves on technical topics.

## Goals

1. Allow users to be able to take a quiz on technical topics individually.
2. Users can connect with other users to create study groups and compare how they did on the same questions. This will be done by students answering the questions at the same time as a game, or they can tag a friend in a quiz to take later.
3. Get video recommendations from [YouTube API](https://developers.google.com/youtube/v3) based on type of questions missed.

## Demographic

Users of this site will be students in college or anyone wanting to possibly transition into the tech-field.

## Data

The data that will be for this application is from the [QuizAPI](https://quizapi.io/docs/1.0/overview) which has a wide variety of technical topic questions in their database. This will be used to query for types of questions for the quiz. It will also use the [YouTube API](https://developers.google.com/youtube/v3) to recommend videos based on the users most missed question topic.

## Approach

### Schema (Tentative)

![alt text](Quiz_app_schema.drawio.svg)

### Potential Problems

1. Limited number of questions for specific topics. Questions are limited to what is in the API database.
2. Making too many request in a given time frame

### Sensitive Information

1. User passwords and scores on quizzes.
2. Will need user permission to show scores to the public or in study groups.

### Functionality

Users should be able to take quizzes, join study groups and take quizzes as a game with fellow users. On their dashboard they can view grades on the three most recent quizzes taken (click on link to view all). Badges will be displayed on the topic that the user has the most correct answers on. Suggested study for most missed questions topic.

Study groups will have their own page where it will show the leaderboard for overall and most tested topics. Users will be able to comment and make suggestions for the next study topic or session.

Use YouTube API to suggest videos on topics where questions were missed.

### User Flow

(Initial - will add more detail)

Users who are not logged in will see a list of topics for questions, and list of features of the application.

Users sign up, once signed up they will be taken to their home dashboard where they can search for quizzes and/or study groups.

Logged-in users will be able to create quizzes and study groups. They can invite people to join their study groups via email or group code.
