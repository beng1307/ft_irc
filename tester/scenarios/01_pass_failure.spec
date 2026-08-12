CLIENTS C1

C1 SEND PASS WRONGPASSWORD
C1 SEND NICK Alice
# Prefix 'F' asserts that USER registration fails (receives 464 ERR_PASSWDMISMATCH or 4xx error)
C1 F SEND USER alice 0 * :Alice
