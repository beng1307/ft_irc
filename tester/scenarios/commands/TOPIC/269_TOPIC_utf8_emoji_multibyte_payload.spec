# 269_TOPIC_utf8_emoji_multibyte_payload.spec
# Tests multi-byte UTF-8, emojis, and international characters in channel topic.
# Expected: Server binary-safe buffer preserves all UTF-8 codepoints without corruption or truncation.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #international
C1 EXPECT :Alice!* JOIN #international

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #international
C2 EXPECT :Bob!* JOIN #international
C1 WAIT_RECV :Bob!* JOIN #international

# Alice sets UTF-8 topic with emojis and CJK
C1 SEND TOPIC #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎
C1 EXPECT :Alice!* TOPIC #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎
C2 EXPECT :Alice!* TOPIC #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎

# Bob queries topic
C2 SEND TOPIC #international
C2 EXPECT 332 Bob #international :🚀 IRC Server Launch 🔥 | サーバー起動 | 欢迎
