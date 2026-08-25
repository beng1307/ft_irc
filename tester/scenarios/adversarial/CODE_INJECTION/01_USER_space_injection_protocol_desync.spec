# 01_USER_space_injection_protocol_desync.spec
# Vulnerability: USER command does not validate username and allows space-injected strings.
# Expected secure behavior: Server must reject usernames with spaces (e.g. 432 Erroneous username/nickname or 468)
# and never allow an attacker to forge IRC command prefixes (e.g. ":Attacker!admin PRIVMSG #target@localhost").

# THIS IS VALID TEST DO NOT DELETE!!!!!!!!!!!!!
CLIENTS C1, C2

# C1 attempts registering with an invalid/space-injected username designed to split the prefix
C1 SEND PASS 1234
C1 SEND NICK Hacker
C1 SEND USER :admin PRIVMSG #secret 0 * :RealName
C1 EXPECT 432 * :*

# Verify C1 is blocked from registering
C1 SEND JOIN #injection_test
C1 EXPECT 451 * :You have not registered

# C2 registers cleanly
C2 SEND PASS 1234
C2 SEND NICK Observer
C2 SEND USER observer 0 * :Observer Realname
C2 EXPECT 001 Observer :*
C2 EXPECT 002 Observer :*
C2 EXPECT 003 Observer :*
C2 EXPECT 004 Observer *

# C2 joins #injection_test and receives channel burst
C2 SEND JOIN #injection_test
C2 EXPECT :Observer!observer@localhost JOIN #injection_test
C2 EXPECT 331 Observer #injection_test :No topic is set
C2 EXPECT 353 Observer = #injection_test :@Observer
C2 EXPECT 366 Observer #injection_test :End of /NAMES list

# C1 recovers with a valid USER command and registers successfully
C1 SEND USER validuser 0 * :Valid Realname
C1 EXPECT 001 Hacker :*
C1 EXPECT 002 Hacker :*
C1 EXPECT 003 Hacker :*
C1 EXPECT 004 Hacker *

# C1 joins #injection_test and verifies clean prefix on C2
C1 SEND JOIN #injection_test
C2 EXPECT :Hacker!validuser@localhost JOIN #injection_test
C1 EXPECT :Hacker!validuser@localhost JOIN #injection_test
C1 EXPECT 331 Hacker #injection_test :No topic is set
C1 EXPECT 353 Hacker = #injection_test :@Observer Hacker
C1 EXPECT 366 Hacker #injection_test :End of /NAMES list

# Verify message broadcast prefix integrity
C1 SEND PRIVMSG #injection_test :hello 
C2 EXPECT :Hacker!validuser@localhost PRIVMSG #injection_test :hello