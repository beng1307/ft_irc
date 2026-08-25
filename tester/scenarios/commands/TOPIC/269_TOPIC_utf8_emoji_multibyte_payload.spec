# 269_TOPIC_utf8_emoji_multibyte_payload.spec
# Tests multi-byte UTF-8, emojis, and international characters in channel topic.
# Expected: Server binary-safe buffer preserves all UTF-8 codepoints without corruption or truncation.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali370
C1 SEND USER ali370 0 * :Ali370
C1 EXPECT 001 Ali370 :*
C1 SEND JOIN #international
C1 EXPECT :Ali370!* JOIN #international

C2 SEND PASS 1234
C2 SEND NICK Bob370
C2 SEND USER bob370 0 * :Bob370
C2 EXPECT 001 Bob370 :*
C2 SEND JOIN #international
C2 EXPECT :Bob370!* JOIN #international
C1 WAIT_RECV :Bob370!* JOIN #international

# Alice sets UTF-8 topic with emojis and CJK
C1 SEND TOPIC #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎
C1 EXPECT :Ali370!* TOPIC #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎
C2 EXPECT :Ali370!* TOPIC #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎

# Bob queries topic
C2 SEND TOPIC #international
C2 EXPECT 332 Bob370 #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎
