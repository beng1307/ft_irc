# 222_PASS_quit_before_pass.spec
# QUIT before PASS / registration cleanly closes connection with ERROR :Closing connection
CLIENTS C1

C1 SEND QUIT :Leaving early
C1 EXPECT ERROR :Closing connection
