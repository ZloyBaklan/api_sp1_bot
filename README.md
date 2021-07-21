# api_sp1_bot
This project is a Telegram bot that:
accesses the API of the Praktikum.Domashka service;
finds out if the homework was taken in the review, whether it has been checked, failed or accepted;
sends the result (homework status) to your Telegram chat.

The bot regularly polls the homework API and, upon receiving updates, 
parses the response and sends a message to the Telegram account.
The polling mechanism has been implemented.
The bot logs the moment of its launch (DEBUG level) and every message sending (INFO level). 
Modify: The bot logs messages of the ERROR level and (additionally) sends you to Telegram.
FileHandler and StreamHandler handlers are used for logs.
Bot uses Heroku server.
