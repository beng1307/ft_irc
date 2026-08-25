SHELL := /bin/bash
MAKEFLAGS += -j

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
OBJS_FOLDER = .obj
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

re: fclean
	@$(MAKE) all

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

# make test parallel [single|multi] [-i] OR make test [/folder] OR make test [port] [pass] [/folder] OR make test [pass] [/folder]
# make test DIR=<folder> OR make test FOLDER=<folder>
test: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ "$$1" = "parallel" ]; then \
		inc=""; \
		case "$(MAKEFLAGS)" in *i*) inc="-i" ;; esac; \
		SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_parallel "$${@:2}" $$inc; \
		exit $$?; \
	fi; \
	port=""; pass=""; targets=(); nums=(); \
	for arg in "$$@"; do \
		clean_arg="$${arg#/}"; clean_arg="$${clean_arg%/}"; \
		if [[ "$$arg" == /* ]] || [[ "$$arg" == */ ]] || [ -d "$$arg" ] || [ -d "tester/scenarios/$$arg" ] || [ -d "tester/scenarios/$$clean_arg" ] || [ -n "$$(find tester/scenarios -mindepth 1 -maxdepth 2 -type d \( -iname "$$clean_arg" -o -name "$$clean_arg" \) 2>/dev/null)" ]; then \
			targets+=("$$arg"); \
		elif [[ "$$arg" =~ ^[0-9]+$$ ]]; then \
			nums+=("$$arg"); \
		else \
			targets+=("$$arg"); \
		fi; \
	done; \
	if [ $${#nums[@]} -ge 2 ]; then \
		port="$${nums[0]}"; \
		pass="$${nums[1]}"; \
		if [ $${#nums[@]} -gt 2 ]; then \
			for (( i=2; i<$${#nums[@]}; i++ )); do \
				targets+=("$${nums[$$i]}"); \
			done; \
		fi; \
	elif [ $${#nums[@]} -eq 1 ]; then \
		if [ $${#targets[@]} -gt 0 ] && [ "$${nums[0]}" -le 99 ] 2>/dev/null; then \
			targets+=("$${nums[0]}"); \
		else \
			pass="$${nums[0]}"; \
		fi; \
	fi; \
	cmd=(SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios); \
	if [ -n "$(DIR)$(FOLDER)" ]; then cmd+=(--dir "$(if $(DIR),$(DIR),$(FOLDER))"); fi; \
	if [ -n "$$port" ]; then cmd+=(--port "$$port"); fi; \
	if [ -n "$$pass" ]; then cmd+=(--password "$$pass"); fi; \
	if [ $${#targets[@]} -gt 0 ]; then cmd+=("$${targets[@]}"); fi; \
	env "$${cmd[@]}"

parallel: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	inc=""; \
	case "$(MAKEFLAGS)" in *i*) inc="-i" ;; esac; \
	SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_parallel "$$@" $$inc

# make case [testcase|/folder] OR make case [pass] [case|/folder] OR make case [port] [pass] [case|/folder]
case: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -eq 0 ] && [ -z "$(DIR)$(FOLDER)" ]; then \
		echo "Usage: make case <case|/folder>  OR  make case <password> <case|/folder>  OR  make case <port> <password> <case|/folder>"; \
		exit 1; \
	fi; \
	port=""; pass=""; targets=(); nums=(); \
	for arg in "$$@"; do \
		clean_arg="$${arg#/}"; clean_arg="$${clean_arg%/}"; \
		if [[ "$$arg" == /* ]] || [[ "$$arg" == */ ]] || [ -d "$$arg" ] || [ -d "tester/scenarios/$$arg" ] || [ -d "tester/scenarios/$$clean_arg" ] || [ -n "$$(find tester/scenarios -mindepth 1 -maxdepth 2 -type d \( -iname "$$clean_arg" -o -name "$$clean_arg" \) 2>/dev/null)" ]; then \
			targets+=("$$arg"); \
		elif [[ "$$arg" =~ ^[0-9]+$$ ]]; then \
			nums+=("$$arg"); \
		else \
			targets+=("$$arg"); \
		fi; \
	done; \
	if [ $${#nums[@]} -ge 2 ]; then \
		port="$${nums[0]}"; \
		pass="$${nums[1]}"; \
		if [ $${#nums[@]} -gt 2 ]; then \
			for (( i=2; i<$${#nums[@]}; i++ )); do \
				targets+=("$${nums[$$i]}"); \
			done; \
		fi; \
	elif [ $${#nums[@]} -eq 1 ]; then \
		if [ $${#targets[@]} -gt 0 ] && [ "$${nums[0]}" -le 99 ] 2>/dev/null; then \
			targets+=("$${nums[0]}"); \
		elif [ $${#targets[@]} -gt 0 ]; then \
			pass="$${nums[0]}"; \
		else \
			targets+=("$${nums[0]}"); \
		fi; \
	fi; \
	cmd=(SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios); \
	if [ -n "$(DIR)$(FOLDER)" ]; then cmd+=(--dir "$(if $(DIR),$(DIR),$(FOLDER))"); fi; \
	if [ -n "$$port" ]; then cmd+=(--port "$$port"); fi; \
	if [ -n "$$pass" ]; then cmd+=(--password "$$pass"); fi; \
	if [ $${#targets[@]} -gt 0 ]; then cmd+=("$${targets[@]}"); fi; \
	env "$${cmd[@]}"

# make caseverbose [testcase|/folder] OR make caseverbose [pass] [case|/folder] OR make caseverbose [port] [pass] [case|/folder]
caseverbose: all
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	port=""; pass=""; targets=(); nums=(); \
	for arg in "$$@"; do \
		clean_arg="$${arg#/}"; clean_arg="$${clean_arg%/}"; \
		if [[ "$$arg" == /* ]] || [[ "$$arg" == */ ]] || [ -d "$$arg" ] || [ -d "tester/scenarios/$$arg" ] || [ -d "tester/scenarios/$$clean_arg" ] || [ -n "$$(find tester/scenarios -mindepth 1 -maxdepth 2 -type d \( -iname "$$clean_arg" -o -name "$$clean_arg" \) 2>/dev/null)" ]; then \
			targets+=("$$arg"); \
		elif [[ "$$arg" =~ ^[0-9]+$$ ]]; then \
			nums+=("$$arg"); \
		else \
			targets+=("$$arg"); \
		fi; \
	done; \
	if [ $${#nums[@]} -ge 2 ]; then \
		port="$${nums[0]}"; \
		pass="$${nums[1]}"; \
		if [ $${#nums[@]} -gt 2 ]; then \
			for (( i=2; i<$${#nums[@]}; i++ )); do \
				targets+=("$${nums[$$i]}"); \
			done; \
		fi; \
	elif [ $${#nums[@]} -eq 1 ]; then \
		if [ $${#targets[@]} -gt 0 ] && [ "$${nums[0]}" -le 99 ] 2>/dev/null; then \
			targets+=("$${nums[0]}"); \
		else \
			pass="$${nums[0]}"; \
		fi; \
	fi; \
	cmd=(SERVER_BIN="$(CURDIR)/ircserv" ./tester/run_scenarios); \
	if [ -n "$(DIR)$(FOLDER)" ]; then cmd+=(--dir "$(if $(DIR),$(DIR),$(FOLDER))"); fi; \
	if [ -n "$$port" ]; then cmd+=(--port "$$port"); fi; \
	if [ -n "$$pass" ]; then cmd+=(--password "$$pass"); fi; \
	if [ $${#targets[@]} -gt 0 ]; then cmd+=("$${targets[@]}"); fi; \
	VERBOSE=1 env "$${cmd[@]}"

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

final:
	@./copy_to_final.sh

help:
	@echo "Usage: make [target] [args...]"
	@echo ""
	@echo "  make                                        - Compile ircserv"
	@echo "  make run [password]                         - Run server with custom password (port: .env or 6667)"
	@echo "  make run <port> <password>                  - Run server with custom port and password"
	@echo "  make test [password]                        - Run all tests with custom password (port: .env or 6667)"
	@echo "  make test <port> <password>                 - Run all tests with custom port and password"
	@echo "  make test parallel [single|multi]           - Run all tests in parallel (single=shared server, multi=isolated servers)"
	@echo "  make parallel [single|multi]                - Run all tests in parallel (single=shared server, multi=isolated servers)"
	@echo "  make case <case>                            - Run single test scenario"
	@echo "  make case <password> <case>                 - Run single scenario with custom password"
	@echo "  make case <port> <password> <case>          - Run single scenario with custom credentials"
	@echo "  make caseverbose <case>                     - Run single test scenario in verbose mode"
	@echo "  make caseverbose <pass> <case>              - Run single scenario with custom password in verbose mode"
	@echo "  make caseverbose <p> <pass> <case>          - Run single scenario with custom credentials in verbose mode"
	@echo "  make runv <case>                            - Alias for make caseverbose"
	@echo "  make final                                  - Export submission files to ../ft_irc_final"
	@echo ""
	@echo "  [.env file = can persist custom port/password configuration]"
	@echo ""
	@echo "  make env <port> <password>                  - Save default port and password to .env"
	@echo "  make env                                    - Delete .env and reset to defaults"
	@echo ""
	@echo "  make client [password]                      - Launch irssi with custom password (port: .env or 6667)"
	@echo "  make client <port> <password>               - Launch irssi with custom port and password"
	@echo "  make clean / fclean / re                    - Clean object files, binary, or rebuild"

%:
	@:

.PHONY: all clean fclean re run test parallel case caseverbose env client help final