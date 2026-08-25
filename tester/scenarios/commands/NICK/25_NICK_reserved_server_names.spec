# 25_NICK_reserved_server_names.spec
# Malicious actor attempts to impersonate the server hostname or use wildcard as nickname (localhost, ircserv, *).
# Expected: Server rejects reserved / wildcard names with 432 Erroneous nickname.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK localhost
C1 EXPECT 432 * localhost :Erroneous nickname

C1 SEND NICK *
C1 EXPECT 432 * * :Erroneous nickname
