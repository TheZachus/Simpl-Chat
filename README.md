# SIMPL CHAT
#### Video Demo:  <URL HERE>
#### Description:

# Introduction

Simpl Chat is a live chat app that cuts out the BS when chatting with others. Minimal account setup is required, allowing users to instantly connect with your friends. For this project, Based on the final project before the end of CS50, “finance”, I had to acquire many new skills in the making of this application. The tech stack borrowed from lessons from a class ahead of CS50X, CS50W, to fully implement a React frontend environment and a Flask backend with a SQLite3 database. Both CoPilot and Cursor also played a role in automating code I already knew how to implement. I will first touch on the overall structure of the project, the schema of the databases used, and how I applied the new technologies that I learned.

## Structure

As stated before, the structure of this project is heavily based on the final homework assignment of CS50, “finance.” In this spirit, I placed all of the views within a singular file named app.py, the SQLite3 database in a file called “chats.db,” all of the HTML templates into a directory called “templates,” and any static components (reusable code that was not going to change) into a static directory. This would be accessed by the HTML templates to display items and other logic that was implemented in React.

Courtesy of CS50W’s React lecture, I recycled Bootstrap and lite React implementations, as to not expend more time than necessary learning tools that could have made the project more bloated and unruly (Vite, other frontend applications). This was heavily considered during the project’s conception, but because of time constraints and the holiday season, it was thought that using the bare minimum code to still be able to implement React’s features would be the best use of my time.

## Database Schema

The database was split up into four separate tables: Users for authentication, Chats for keeping track of chat names and participants, ChatMembers for understanding who was in what chat and how they were contributing to the chat, and messages to keep track of what messages were being sent in what chat. It was debated whether or not ChatMembers was necessary or if it would end up being superfluous, easily able to be merged with the Users schema. It was decided that a separation of concerns for this information was necessary. If all ChatMember data was given in the Users schema, there would be far too much to keep track of for one tablet. All other schemas within the project I feel are straight forward in nature for their inclusion.

## React

The biggest reason that I wanted to do this project in the first place was because of the chance to learn React as a framework. I debated whether or not I wanted to learn Typescript along with React as it is also widely used in most modern frontend development, but as to not allow scope to run away with things that were unnecessary to learn for the project, I decided that it was best to stick with what I knew. The key reason why I was keen to learn React was because of its components and props architecture, allowing what would otherwise need to be handwritten multiple times to be recycled in an intuitive, concise format. 

The implementation of React within the project was borrowed from Lecture 6 of Harvard’s CS50W course: adding a <script></script> tag that included Babel and React Lite within each of my templates. This was included within the layout template, allowing me to focus on writing in an HTML document much like it was a JSX file.This was a headache in terms of using VS code’s built in autocorrect and Intellisense styling because of Flask’s Jinja2 syntax was woefully unrecognized. Regardless, it was extraordinarily useful being able to simplify and reuse HTML elements and JavaScript logic created within React as functions.

## Web Sockets

The nature of live chat requires consistent, bi-directional communication in each of its users’ chat sessions. Unfortunately, simple forms such as the ones used in the login and registration pages would not be sufficient for this kind of interaction, as the page would need to be frequently refreshed, making communication slow and cumbersome for the user. It was researching this problem that I learned about WebSocket.io.

This library accomplished exactly the type of bi-directional communication that I was looking to implement and was natively compatible with both React and Flask.Implementation on the backend by setting up an API was easy enough, but implementation on the frontend was significantly more involved. The most time consuming aspect of this project was ensuring that the WebSockets performed as expected.

## Authentication

During development, It became clear that the way we were authenticating in class was incredibly insecure and easily replicable for malicious actors. Creating a cookie related to a user’s ID within the system was too easily brute forced if given the right tools. It was necessary to create cookies specifically used for sessions. Luckily, a Flask library that I was already using, flask_login, was already capable of managing user sessions on both the backend and frontend. Implementing this was fairly straightforward, as it only required me to replace a few lines of code relating to the session itself while being significantly more secure.

# Conclusion

Utilizing newfound knowledge with frontend, session maintenance technology, and authentication hardening, Simpl Chat remains simple and easy to use, but complex under the hood.
