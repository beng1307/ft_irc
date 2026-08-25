# 98_PRIVMSG_multi_word_without_colon.spec
# Tests PRIVMSG with multiple words without leading colon on payload.
# Strict RFC 1459/2812 behavior: Without a colon ':' prefix, spaces act as argument
# delimiters (middle parameters). PRIVMSG takes exactly 2 parameters (<target> <text>).
# Therefore, only the first word 'hello' is parsed as the text parameter (arguments[1]),
# while extraneous trailing words are not merged into the text body.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali312
C1 SEND USER ali312 0 * :Ali312
C1 EXPECT 001 Ali312 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob312
C2 SEND USER bob312 0 * :Bob312
C2 EXPECT 001 Bob312 :*

# Join channel
C1 SEND JOIN #chan
C1 EXPECT 366 Ali312 #chan :End of /NAMES list
C2 SEND JOIN #chan
C1 WAIT_RECV :Bob312!* JOIN #chan

# C1 sends multi-word message without colon (only first token is the message payload)
C1 SEND PRIVMSG #chan hello world from ali312
C2 WAIT_RECV :Ali312!* PRIVMSG #chan :hello

