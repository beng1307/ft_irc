# Tests abrupt disconnects during active broadcast (ADV-MEM-01), channel destruction on last member part (ADV-MEM-02), simultaneous channel cleanup (ADV-MEM-03), and mid-command FIN (ADV-NET-05).
CLIENTS C1, C2, C3, C4

# Register 4 clients
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

C4 SEND PASS 1234
C4 SEND NICK Dana
C4 SEND USER dana 0 * :Dana
C4 EXPECT 001 Dana :*

# Join shared channel and solo channel
C1 SEND JOIN #abrupt
C1 EXPECT :Alice!* JOIN #abrupt
C2 SEND JOIN #abrupt
C2 WAIT_RECV :Bob!* JOIN #abrupt
C3 SEND JOIN #abrupt
C3 WAIT_RECV :Charlie!* JOIN #abrupt
C4 SEND JOIN #abrupt
C4 WAIT_RECV :Dana!* JOIN #abrupt

# Alice creates solo channel
C1 SEND JOIN #solochan
C1 EXPECT :Alice!* JOIN #solochan

# ADV-MEM-01: Client D abruptly drops with RST while active
C4 RESET

# Alice broadcasts to #abrupt; remaining clients C2 and C3 must receive without server crashing
C1 SEND PRIVMSG #abrupt :Broadcast after C4 RST
C2 WAIT_RECV :Alice!* PRIVMSG #abrupt :Broadcast after C4 RST
C3 WAIT_RECV :Alice!* PRIVMSG #abrupt :Broadcast after C4 RST

# Client C3 closes connection normally
C3 CLOSE_SOCKET

# Broadcast continues smoothly to C2
C1 SEND PRIVMSG #abrupt :Broadcast after C3 close
C2 WAIT_RECV :Alice!* PRIVMSG #abrupt :Broadcast after C3 close

# ADV-MEM-02: Self-part from solo channel triggers channel deletion during execution
C1 SEND PART #solochan :Leaving solo
C1 EXPECT :Alice!* PART #solochan*

# ADV-MEM-03: C2 sends QUIT to cleanly clean up from #abrupt
C2 SEND QUIT :Leaving gracefully
C1 WAIT_RECV :Bob!* QUIT :Leaving gracefully

# ADV-NET-05: Alice sends half a frame without CRLF and abruptly closes socket
C1 SEND_RAW PRIVMSG #abrupt :Half_message_no_crlf
C1 CLOSE_SOCKET
