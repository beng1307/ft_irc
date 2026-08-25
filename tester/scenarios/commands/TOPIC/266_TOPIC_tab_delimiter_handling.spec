# 266_TOPIC_tab_delimiter_handling.spec
# Tests adversarial command formatting using TAB (\t) delimiters instead of spaces.
# Expected: Server rejects tab-delimited command with 461 ERR_NEEDMOREPARAMS (or 421) because IRC grammar requires space delimiters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Alice sends TOPIC delimited with tabs
C1 SEND TOPIC	#lobby	:TabDelimitedTopic
C1 EXPECT 461 Alice TOPIC :Not enough parameters
