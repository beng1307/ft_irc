CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie

C1 SEND JOIN #opchan
C2 SEND JOIN #opchan
C3 SEND JOIN #opchan
C1 WAIT_RECV :Charlie!* JOIN #opchan

# C2 is regular user -> non-op cannot kick C3
C2 F SEND KICK #opchan Charlie :Out!

# C1 grants op to C2
C1 SEND MODE #opchan +o Bob
C2 WAIT_RECV :Alice!* MODE #opchan +o Bob

# Now C2 has op and can kick C3
C2 SEND KICK #opchan Charlie :Out!
C3 WAIT_RECV :Bob!* KICK #opchan Charlie :Out!
