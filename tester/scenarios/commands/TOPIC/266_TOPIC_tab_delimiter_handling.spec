# 266_TOPIC_tab_delimiter_handling.spec
# Tests adversarial command formatting using TAB (\t) delimiters instead of spaces.
# Expected: Server rejects tab-delimited command with 461 ERR_NEEDMOREPARAMS (or 421) because IRC grammar requires space delimiters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali367
C1 SEND USER ali367 0 * :Ali367
C1 EXPECT 001 Ali367 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali367!* JOIN #lobby

# Alice sends TOPIC delimited with tabs
C1 SEND TOPIC	#lobby	:TabDelimitedTopic
C1 EXPECT 421 Ali367 Unknown command.
