COMPILE = c++ -g -Wall -Wextra -Werror -std=c++98 -fPIE
NAME = ircserv
SRCS = main.cpp \
	   Channel/Channel.cpp \
	   Client/Client.cpp \
	   Server/Server.cpp \
	   Server/ServerSocket.cpp \
	   Server/ServerLoop.cpp \
	   Server/ServerCommands.cpp \
	   Server/ServerChannelOps.cpp \
	   Server/ServerMessaging.cpp \
	   Server/ServerHelper.cpp
OBJS_FOLDER = obj
OBJS = $(SRCS:%.cpp=$(OBJS_FOLDER)/%.o)
HEADERS = Server/Server.hpp Channel/Channel.hpp Client/Client.hpp 

$(NAME): $(OBJS)
	$(COMPILE) $(OBJS) -o $(NAME)	

$(OBJS_FOLDER)/%.o: %.cpp $(HEADERS)
	@mkdir -p $(dir $@)
	$(COMPILE) -c $< -o $@

all: $(NAME)

clean:
	@rm -rf $(OBJS_FOLDER)

fclean:	clean
	@rm -f $(NAME)

re: fclean all

-include .env

ENV_PORT := $(PORT)
ENV_PASSWORD := $(PASSWORD)
PORT := $(if $(ENV_PORT),$(ENV_PORT),6667)
PASSWORD := $(if $(ENV_PASSWORD),$(ENV_PASSWORD),1234)

# make run [port] [password] OR make run [password] = uses given args, .env, or default (6667 / 1234)
run: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		./ircserv "$$1" "$$2"; \
	elif [ $$# -eq 1 ]; then \
		./ircserv $(PORT) "$$1"; \
	else \
		./ircserv $(PORT) $(PASSWORD); \
	fi

# make test [port] [password] OR make test [password] = run all scenarios (uses .env or default if omitted)
test: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios --port "$$1" --password "$$2"; \
	elif [ $$# -eq 1 ]; then \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios --port $(PORT) --password "$$1"; \
	else \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios; \
	fi

# make case <case> OR make case <password> <case> OR make case <port> <password> <case> = run scenario
case: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -eq 1 ]; then \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios "$$1"; \
	elif [ $$# -eq 2 ]; then \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios --port $(PORT) --password "$$1" "$$2"; \
	elif [ $$# -ge 3 ]; then \
		P="$$1"; PW="$$2"; shift 2; \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios --port "$$P" --password "$$PW" "$$@"; \
	else \
		echo "Usage: make case <case>  OR  make case <password> <case>  OR  make case <port> <password> <case>"; \
		exit 1; \
	fi

# make caseverbose <case> OR make caseverbose <password> <case> OR make caseverbose <port> <password> <case> = run scenario in verbose mode
caseverbose: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -eq 1 ]; then \
		VERBOSE=1 SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios "$$1"; \
	elif [ $$# -eq 2 ]; then \
		VERBOSE=1 SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios --port $(PORT) --password "$$1" "$$2"; \
	elif [ $$# -ge 3 ]; then \
		P="$$1"; PW="$$2"; shift 2; \
		VERBOSE=1 SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios --port "$$P" --password "$$PW" "$$@"; \
	else \
		echo "Usage: make caseverbose <case>  OR  make caseverbose <password> <case>  OR  make caseverbose <port> <password> <case>"; \
		exit 1; \
	fi

# make env [port] [password] = edits / saves .env (or removes .env if no args)
env:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		echo "PORT=$$1" > .env; \
		echo "PASSWORD=$$2" >> .env; \
		echo "Saved to .env -> PORT=$$1, PASSWORD=$$2"; \
	elif [ $$# -eq 0 ]; then \
		rm -f .env; \
		echo "Removed .env (reset to defaults)"; \
	else \
		echo "Usage: make env <port> <password>  (or 'make env' to remove)"; \
	fi

client: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		irssi -c localhost -p "$$1" -w "$$2"; \
	elif [ $$# -eq 1 ]; then \
		irssi -c localhost -p $(PORT) -w "$$1"; \
	else \
		irssi -c localhost -p $(PORT) -w $(PASSWORD); \
	fi

help:
	@echo "Usage: make [target] [args...]"
	@echo ""
	@echo "  make                                - Compile ircserv"
	@echo "  make run [password]                 - Run server with custom password (port: .env or 6667)"
	@echo "  make run <port> <password>          - Run server with custom port and password"
	@echo "  make test [password]                - Run all tests with custom password (port: .env or 6667)"
	@echo "  make test <port> <password>         - Run all tests with custom port and password"
	@echo "  make case <case>                    - Run single test scenario"
	@echo "  make case <password> <case>         - Run single scenario with custom password"
	@echo "  make case <port> <password> <case>  - Run single scenario with custom credentials"
	@echo "  make caseverbose <case>             - Run single test scenario in verbose mode"
	@echo "  make caseverbose <pass> <case>      - Run single scenario with custom password in verbose mode"
	@echo "  make caseverbose <p> <pass> <case>  - Run single scenario with custom credentials in verbose mode"
	@echo "  make runv <case>                    - Alias for make caseverbose"
	@echo ""
	@echo "  [.env file = can persist custom port/password configuration]"
	@echo ""
	@echo "  make env <port> <password>          - Save default port and password to .env"
	@echo "  make env                            - Delete .env and reset to defaults"
	@echo ""
	@echo "  make client [password]              - Launch irssi with custom password (port: .env or 6667)"
	@echo "  make client <port> <password>       - Launch irssi with custom port and password"
	@echo "  make clean / fclean / re            - Clean object files, binary, or rebuild"

%:
	@:

.PHONY: all clean fclean re run test case caseverbose env client help