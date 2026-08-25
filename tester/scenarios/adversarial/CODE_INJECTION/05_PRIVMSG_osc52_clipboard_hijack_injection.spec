# 05_PRIVMSG_osc52_clipboard_hijack_injection.spec
# Vulnerability: PRIVMSG relays raw OSC 52 clipboard escape sequences (\x1b]52;c;<base64>\x07)
# or terminal bell floods (\x07), which can overwrite client clipboards or DoS terminal emulators.
# Expected secure behavior: Server must filter out dangerous terminal control codes from user chat messages.
CLIENTS C1, C2

# Setup Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali032
C1 SEND USER ali032 0 * :Ali032 Usr032
C1 EXPECT 001 Ali032 :*

C2 SEND PASS 1234
C2 SEND NICK Bob032
C2 SEND USER bob032 0 * :Bob032 Usr032
C2 EXPECT 001 Bob032 :*

# Alice attempts to send an OSC 52 clipboard hijacking sequence to Bob
C1 SEND_RAW PRIVMSG Bob032 :\x1b]52;c;c3RlYWw=\x07InjectedText\r\n

# Secure server must strip the escape sequence, relaying only safe printable payload
C2 WAIT_RECV :Ali032!* PRIVMSG Bob032 :InjectedText
