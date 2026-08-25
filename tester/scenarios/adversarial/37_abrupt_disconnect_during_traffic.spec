# Tests abrupt disconnects during active broadcast (ADV-MEM-01), channel destruction on last member part (ADV-MEM-02), simultaneous channel cleanup (ADV-MEM-03), and mid-command FIN (ADV-NET-05).
CLIENTS C1, C2, C3, C4

# Register 4 clients
C1 SEND PASS 1234
C1 SEND NICK Ali017
C1 SEND USER ali017 0 * :Ali017
C1 EXPECT 001 Ali017 :*

C2 SEND PASS 1234
C2 SEND NICK Bob017
C2 SEND USER bob017 0 * :Bob017
C2 EXPECT 001 Bob017 :*

C3 SEND PASS 1234
C3 SEND NICK Cha017
C3 SEND USER cha017 0 * :Cha017
C3 EXPECT 001 Cha017 :*

C4 SEND PASS 1234
C4 SEND NICK Dan017
C4 SEND USER dan017 0 * :Dan017
C4 EXPECT 001 Dan017 :*

# Join shared channel and solo channel
C1 SEND JOIN #abrupt
C1 EXPECT :Ali017!* JOIN #abrupt
C2 SEND JOIN #abrupt
C2 WAIT_RECV :Bob017!* JOIN #abrupt
C3 SEND JOIN #abrupt
C3 WAIT_RECV :Cha017!* JOIN #abrupt
C4 SEND JOIN #abrupt
C4 WAIT_RECV :Dan017!* JOIN #abrupt

# Ali017 creates solo channel
C1 SEND JOIN #solochan
C1 EXPECT :Ali017!* JOIN #solochan

# ADV-MEM-01: Client D abruptly drops with RST while active
C4 RESET

# Ali017 broadcasts to #abrupt; remaining clients C2 and C3 must receive without server crashing
C1 SEND PRIVMSG #abrupt :Broadcast after C4 RST
C2 WAIT_RECV :Ali017!* PRIVMSG #abrupt :Broadcast after C4 RST
C3 WAIT_RECV :Ali017!* PRIVMSG #abrupt :Broadcast after C4 RST

# Client C3 closes connection normally
C3 CLOSE_SOCKET

# Broadcast continues smoothly to C2
C1 SEND PRIVMSG #abrupt :Broadcast after C3 close
C2 WAIT_RECV :Ali017!* PRIVMSG #abrupt :Broadcast after C3 close

# ADV-MEM-02: Self-part from solo channel triggers channel deletion during execution
C1 SEND PART #solochan :Leaving solo
C1 EXPECT :Ali017!* PART #solochan*

# ADV-MEM-03: C2 sends QUIT to cleanly clean up from #abrupt
C2 SEND QUIT :Leaving gracefully
C1 WAIT_RECV :Bob017!* QUIT :Leaving gracefully

# ADV-NET-05: Ali017 sends half a frame without CRLF and abruptly closes socket
C1 SEND_RAW PRIVMSG #abrupt :Half_message_no_crlf
C1 CLOSE_SOCKET
