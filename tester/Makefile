SHELL := /bin/bash
NAME = testrunner
CONCURRENCY_NAME = concurrency_tester
CXX = c++
CXXFLAGS = -Wall -Wextra -Werror -std=c++98 -pthread

SRCS = testrunner.cpp
OBJS = $(SRCS:.cpp=.o)

CONCURRENCY_SRCS = concurrency_tester.cpp
CONCURRENCY_OBJS = $(CONCURRENCY_SRCS:.cpp=.o)

all: $(NAME) $(CONCURRENCY_NAME)

$(NAME): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $(NAME)

$(CONCURRENCY_NAME): $(CONCURRENCY_OBJS)
	$(CXX) $(CXXFLAGS) $(CONCURRENCY_OBJS) -o $(CONCURRENCY_NAME)

clean:
	rm -f $(OBJS) $(CONCURRENCY_OBJS)

fclean: clean
	rm -f $(NAME) $(CONCURRENCY_NAME)
	rm -rf logs

re: fclean all

-include ../.env
-include .env

ENV_PORT := $(PORT)
ENV_PASSWORD := $(PASSWORD)
PORT := $(if $(ENV_PORT),$(ENV_PORT),6667)
PASSWORD := $(if $(ENV_PASSWORD),$(ENV_PASSWORD),1234)

# make run [/folder] OR make run [port] [pass] [/folder] OR make run [pass] [/folder]
# make run DIR=<folder> OR make run FOLDER=<folder>
run: $(NAME)
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	port=""; pass=""; targets=(); nums=(); \
	for arg in "$$@"; do \
		clean_arg="$${arg#/}"; clean_arg="$${clean_arg%/}"; \
		if [[ "$$arg" == /* ]] || [[ "$$arg" == */ ]] || [ -d "$$arg" ] || [ -d "scenarios/$$arg" ] || [ -d "scenarios/$$clean_arg" ] || [ -n "$$(find scenarios -mindepth 1 -maxdepth 2 -type d \( -iname "$$clean_arg" -o -name "$$clean_arg" \) 2>/dev/null)" ]; then \
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
	cmd=("./run_scenarios"); \
	if [ -n "$(DIR)$(FOLDER)" ]; then cmd+=(--dir "$(if $(DIR),$(DIR),$(FOLDER))"); fi; \
	if [ -n "$$port" ]; then cmd+=(--port "$$port"); fi; \
	if [ -n "$$pass" ]; then cmd+=(--password "$$pass"); fi; \
	if [ $${#targets[@]} -gt 0 ]; then cmd+=("$${targets[@]}"); fi; \
	"$${cmd[@]}"

# make case [testcase|/folder] OR make case [pass] [case|/folder] OR make case [port] [pass] [case|/folder]
case: $(NAME)
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -eq 0 ] && [ -z "$(DIR)$(FOLDER)" ]; then \
		echo "Usage: make case <testcase|/folder>  OR  make case <pass> <testcase|/folder>  OR  make case <port> <pass> <testcase|/folder>"; \
		exit 1; \
	fi; \
	port=""; pass=""; targets=(); nums=(); \
	for arg in "$$@"; do \
		clean_arg="$${arg#/}"; clean_arg="$${clean_arg%/}"; \
		if [[ "$$arg" == /* ]] || [[ "$$arg" == */ ]] || [ -d "$$arg" ] || [ -d "scenarios/$$arg" ] || [ -d "scenarios/$$clean_arg" ] || [ -n "$$(find scenarios -mindepth 1 -maxdepth 2 -type d \( -iname "$$clean_arg" -o -name "$$clean_arg" \) 2>/dev/null)" ]; then \
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
	cmd=("./run_scenarios"); \
	if [ -n "$(DIR)$(FOLDER)" ]; then cmd+=(--dir "$(if $(DIR),$(DIR),$(FOLDER))"); fi; \
	if [ -n "$$port" ]; then cmd+=(--port "$$port"); fi; \
	if [ -n "$$pass" ]; then cmd+=(--password "$$pass"); fi; \
	if [ $${#targets[@]} -gt 0 ]; then cmd+=("$${targets[@]}"); fi; \
	"$${cmd[@]}"

# make caseverbose [testcase|/folder] OR make caseverbose [pass] [case|/folder] OR make caseverbose [port] [pass] [case|/folder]
caseverbose: $(NAME)
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	port=""; pass=""; targets=(); nums=(); \
	for arg in "$$@"; do \
		clean_arg="$${arg#/}"; clean_arg="$${clean_arg%/}"; \
		if [[ "$$arg" == /* ]] || [[ "$$arg" == */ ]] || [ -d "$$arg" ] || [ -d "scenarios/$$arg" ] || [ -d "scenarios/$$clean_arg" ] || [ -n "$$(find scenarios -mindepth 1 -maxdepth 2 -type d \( -iname "$$clean_arg" -o -name "$$clean_arg" \) 2>/dev/null)" ]; then \
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
	cmd=("./run_scenarios"); \
	if [ -n "$(DIR)$(FOLDER)" ]; then cmd+=(--dir "$(if $(DIR),$(DIR),$(FOLDER))"); fi; \
	if [ -n "$$port" ]; then cmd+=(--port "$$port"); fi; \
	if [ -n "$$pass" ]; then cmd+=(--password "$$pass"); fi; \
	if [ $${#targets[@]} -gt 0 ]; then cmd+=("$${targets[@]}"); fi; \
	VERBOSE=1 "$${cmd[@]}"

# Alias for make caseverbose
runv: caseverbose

# make full [port] [pass] OR make full [pass] OR make full = run all 3 test suites (run, memory, lifecycle)
full: $(NAME)
	@printf "\n\033[1;35m======================================================================\033[0m\n"
	@printf "\033[1;35m             TEST SUITE 1/3: SCENARIO INTEGRATION TESTS (run)         \033[0m\n"
	@printf "\033[1;35m======================================================================\033[0m\n\n"
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	if [ $$# -ge 2 ]; then \
		./run_scenarios --port "$$1" --password "$$2"; \
	elif [ $$# -eq 1 ]; then \
		./run_scenarios --port $(PORT) --password "$$1"; \
	else \
		./run_scenarios; \
	fi
	@printf "\n\033[1;35m======================================================================\033[0m\n"
	@printf "\033[1;35m             TEST SUITE 2/3: MEMORY & DOS STRESS TESTS (memory)       \033[0m\n"
	@printf "\033[1;35m======================================================================\033[0m\n\n"
	@python3 ./test_memory_dos.py
	@printf "\n\033[1;35m======================================================================\033[0m\n"
	@printf "\033[1;35m             TEST SUITE 3/3: SERVER LIFECYCLE TESTS (lifecycle)       \033[0m\n"
	@printf "\033[1;35m======================================================================\033[0m\n\n"
	@./test_server_lifecycle.sh


lifecycle:
	@./test_server_lifecycle.sh

concurrency: $(CONCURRENCY_NAME)
	@./ensure_server.sh ./$(CONCURRENCY_NAME) $(filter-out $@,$(MAKECMDGOALS))

memory:
	@python3 ./test_memory_dos.py

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

help:
	@echo "Usage: make [target] [args...]"
	@echo ""
	@echo "  make                                - Compile testrunner and concurrency_tester"
	@echo "  make run                            - Run all scenarios"
	@echo "  make run <folder>                   - Run scenarios in specified folder (e.g. make run commands)"
	@echo "  make run DIR=<folder>               - Run scenarios in specified folder"
	@echo "  make run <password> [folder]        - Run scenarios with custom password (port: .env or 6667)"
	@echo "  make run <port> <password> [folder] - Run scenarios with custom port and password"
	@echo "  make runv [folder/testcase]         - Run scenarios in verbose mode"
	@echo "  make case <testcase|folder>         - Run single test scenario or folder"
	@echo "  make case <password> <testcase>     - Run single test scenario with custom password"
	@echo "  make case <port> <password> <case>  - Run single test scenario with custom port and password"
	@echo "  make caseverbose <testcase|folder>  - Run single test scenario or folder in verbose mode"
	@echo "  make full                           - Run all 3 test suites (run, memory, lifecycle)"
	@echo "  make concurrency                    - Run concurrency and thread-safety tests"
	@echo "  make lifecycle                      - Run server lifecycle and reboot tests"
	@echo "  make memory                         - Run memory / leak / stress tests"
	@echo ""
	@echo "  [.env file = persist custom port/password configuration]"
	@echo ""
	@echo "  make env <port> <password>          - Save default port and password to .env"
	@echo "  make env                            - Delete .env and reset to defaults"
	@echo "  make clean / fclean / re            - Clean object files, binaries, or rebuild"

# Allow passing scenario arguments to 'make run' without make complaining about missing targets
%:
	@:

.PHONY: all clean fclean re run full runv case caseverbose lifecycle concurrency memory env help
