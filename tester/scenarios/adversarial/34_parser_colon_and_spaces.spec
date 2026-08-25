# Tests leading/consecutive colons (ADV-FUZZ-01), whitespace handling (ADV-FUZZ-03), CRLF boundary splitting (ADV-FUZZ-06), and non-printable chars (ADV-FUZZ-08).
CLIENTS C1, C2

# Clean preamble with whitespace
C1 SEND_RAW \r\n  \t  \r\n
C1 SEND PASS 1234
C1 SEND NICK Ali014
C1 SEND USER ali014 0 * :Ali014 Usr014
C1 EXPECT 001 Ali014 :*

C2 SEND PASS 1234
C2 SEND NICK Bob014
C2 SEND USER bob014 0 * :Bob014 Usr014
C2 EXPECT 001 Bob014 :*

# ADV-FUZZ-01: Colon prefixes and consecutive colons in parameters
C1 SEND PRIVMSG Bob014 ::::hello::::world::::
C2 WAIT_RECV :Ali014!* PRIVMSG Bob014 ::::hello::::world::::

# ADV-FUZZ-03: Extra whitespace between command and arguments
C1 SEND PRIVMSG    Bob014    :Message with multiple spaces between args
C2 WAIT_RECV :Ali014!* PRIVMSG Bob014 :Message with multiple spaces between args

# ADV-FUZZ-06: TCP packet split across \r and \n boundary
C1 SEND_RAW PRIVMSG Bob014 :Split boundary message\r
WAIT 100ms
C1 SEND_RAW \n
C2 WAIT_RECV :Ali014!* PRIVMSG Bob014 :Split boundary message

# ADV-FUZZ-08: Non-printable ASCII / safe control character handling in message payload
C1 SEND PRIVMSG Bob014 :Testing non-printable \x01\x02\x03 payload
C2 WAIT_RECV :Ali014!* PRIVMSG Bob014 :Testing non-printable * payload

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
