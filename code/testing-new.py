from sentinalysis import validation, sentiment, plotting

# Get validated file
chat_file = "C:\\Users\\dusno\\Desktop\\chats.txt"
validated_chat_file = validation.data_validation(chat_file)

# Get sentiment values
sentiment_dict = sentiment.sentiment_analysis(validated_chat_file)

# Plot stuff
plotting.get_charts(sentiment_dict)