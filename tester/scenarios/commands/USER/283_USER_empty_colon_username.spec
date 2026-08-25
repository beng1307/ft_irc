# 283_USER_empty_colon_username.spec
# Edge Case: Username parameter given as single colon (USER : 0 * :Real)
# Expected: Server rejects invalid empty username with 461 Not enough parameters or 432 Erroneous username.
# Bug: split_arguments extracts ' 0 * :Real', embedding leading space in username and corrupting hostmask.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali405
C1 SEND USER : 0 * :Real
C1 EXPECT 461 Ali405 USER :Not enough parameters
